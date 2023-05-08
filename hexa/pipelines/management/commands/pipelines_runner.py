import json
import os
import sys
from datetime import timedelta
from logging import getLogger
from time import sleep

from django import db
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.signing import Signer
from django.utils import timezone
from slugify import slugify

from hexa.pipelines.models import PipelineRun, PipelineRunState

logger = getLogger(__name__)


def run_pipeline_kube(run: PipelineRun, env_var: dict):
    from kubernetes import config
    from kubernetes.client import CoreV1Api
    from kubernetes.client import models as k8s
    from kubernetes.client.rest import ApiException

    exec_time_str = timezone.now().replace(tzinfo=None, microsecond=0).isoformat()
    logger.debug("K8S RUN %s: %s for %s", os.getpid(), run.pipeline.name, exec_time_str)
    container_name = slugify("pipeline-" + run.pipeline.name + "-" + exec_time_str)
    config.load_incluster_config()
    v1 = CoreV1Api()
    pod = k8s.V1Pod(
        api_version="v1",
        kind="Pod",
        metadata=k8s.V1ObjectMeta(
            namespace=os.environ.get("PIPELINE_NAMESPACE", "default"),
            name=slugify("pipeline-" + run.pipeline.name + "-" + exec_time_str),
            annotations={
                # Unfortunately, it also seems that GKE (at least) uses app armor to restrict
                # the syscalls a container is allowed to execute, so we need to ask to run
                # in "unconfined" mode. Beware, you might think you are already in
                # "unconfined" mode by default. You are not. If you get a "fuse: mount
                # failed: Permission denied" error, you did something wrong over here.
                "container.apparmor.security.beta.kubernetes.io/"
                + container_name: "unconfined",
            },
        ),
        spec=k8s.V1PodSpec(
            restart_policy="Never",
            tolerations=[
                k8s.V1Toleration(
                    key="hub.jupyter.org_dedicated",
                    operator="Equal",
                    value="user",
                    effect="NoSchedule",
                ),
            ],
            affinity=k8s.V1Affinity(
                node_affinity=k8s.V1NodeAffinity(
                    required_during_scheduling_ignored_during_execution=k8s.V1NodeSelector(
                        node_selector_terms=[
                            k8s.V1NodeSelectorTerm(
                                match_expressions=[
                                    k8s.V1NodeSelectorRequirement(
                                        key="hub.jupyter.org/node-purpose",
                                        operator="In",
                                        values=["user"],
                                    )
                                ],
                            ),
                        ],
                    ),
                ),
            ),
            containers=[
                k8s.V1Container(
                    image=env_var["HEXA_PIPELINE_IMAGE"],
                    name=container_name,
                    image_pull_policy="Always",
                    args=[json.dumps(run.config)],
                    env=[
                        k8s.V1EnvVar(
                            name="HEXA_ENVIRONMENT",
                            value="PIPELINE",
                        ),
                        k8s.V1EnvVar(
                            name="HEXA_SERVER_URL",
                            value=env_var["HEXA_SERVER_URL"],
                        ),
                        k8s.V1EnvVar(
                            name="HEXA_TOKEN",
                            value=env_var["HEXA_TOKEN"],
                        ),
                        k8s.V1EnvVar(
                            name="HEXA_PIPELINE_NAME",
                            value=env_var["HEXA_PIPELINE_NAME"],
                        ),
                        k8s.V1EnvVar(
                            name="HEXA_RUN_ID",
                            value=env_var["HEXA_RUN_ID"],
                        ),
                    ],
                    # We need to have /dev/fuse mounted inside the container
                    # This is done by requesting a resource: smarter-devices/fuse
                    # This resource, is provided by the smarter-device-manager DaemonSet.
                    # In our case, this DaemonSet is described in devops/config/smarter-device-manager.yaml.
                    # Useful links:
                    # - Source of the pod: https://gitlab.com/arm-research/smarter/smarter-device-manager
                    # - Inspiration for the yaml: https://github.com/samos123/gke-gcs-fuse-unprivileged
                    resources={
                        "limits": {
                            "smarter-devices/fuse": 1,
                        },
                        "requests": {
                            "smarter-devices/fuse": 1,
                        },
                    },
                    # Having /dev/fuse is not enough. We also need to be able to execute the mount()
                    # syscall from inside the container. Requiring CAP_SYS_ADMIN seems enough and
                    # we DON'T need to be privileged.
                    security_context={
                        "privileged": False,
                        "capabilities": {
                            "add": ["SYS_ADMIN"],
                        },
                    },
                )
            ],
        ),
    )
    v1.create_namespaced_pod(namespace=pod.metadata.namespace, body=pod)

    # monitore the pod
    while True:
        run.refresh_from_db()
        run.last_heartbeat = timezone.now()
        run.save()

        remote_pod = v1.read_namespaced_pod(pod.metadata.name, pod.metadata.namespace)
        # still running
        if (
            remote_pod
            and remote_pod.status
            and remote_pod.status.phase in {"Succeeded", "Failed"}
        ):
            break
        sleep(5)

    # download logs
    try:
        stdout = v1.read_namespaced_pod_log(
            name=pod.metadata.name,
            namespace=pod.metadata.namespace,
            container=container_name,
        )
    except Exception:
        logger.exception("get logs")
        stdout = ""

    # delete terminated pod
    try:
        v1.delete_namespaced_pod(
            name=pod.metadata.name,
            namespace=pod.metadata.namespace,
            body=k8s.V1DeleteOptions(),
        )
    except ApiException as e:
        # If the pod not found -> ignore exception, osef
        if e.status != 404:
            logger.exception("pod delete")

    return remote_pod.status.phase == "Succeeded", "STDOUT\n%s" % (stdout,)


def run_pipeline_docker(run: PipelineRun, env_var: dict):
    from subprocess import PIPE, STDOUT, Popen

    docker_cmd = f'docker run --privileged -e HEXA_ENVIRONMENT=PIPELINE -e HEXA_RUN_ID={env_var["HEXA_RUN_ID"]} -e HEXA_SERVER_URL={env_var["HEXA_SERVER_URL"]} -e HEXA_TOKEN={env_var["HEXA_TOKEN"]} --network openhexa --platform linux/amd64 --rm {env_var["HEXA_PIPELINE_IMAGE"]}'
    cmd = docker_cmd.split(" ") + [f"{json.dumps(run.config)}"]

    proc = Popen(
        cmd,
        stdout=PIPE,
        stderr=STDOUT,
        close_fds=True,
    )

    while True:
        run.refresh_from_db()
        run.last_heartbeat = timezone.now()
        run.save()

        proc.poll()
        if proc.returncode is not None:
            break
        sleep(5)

    return proc.returncode == 0, proc.stdout.read().decode("UTF-8")


def run_pipeline(run: PipelineRun):
    logger.info("Run pipeline: %s", run)

    if os.fork() != 0:
        # parent or error -> return
        return

    # force a cycle of the DB connection to stop interference with parent
    db.connections.close_all()
    run.refresh_from_db()

    env_var = {}
    env_var["HEXA_SERVER_URL"] = f"{settings.PIPELINE_API_URL}"
    env_var["HEXA_TOKEN"] = Signer().sign_object(run.access_token)
    env_var["HEXA_RUN_ID"] = str(run.id)
    env_var["HEXA_PIPELINE_NAME"] = run.pipeline.name
    env_var["HEXA_PIPELINE_IMAGE"] = settings.get(
        "PIPELINE_IMAGE", "blsq/openhexa-pipelines:latest"
    )

    time_start = timezone.now()

    try:
        if settings.PIPELINE_SCHEDULER_SPAWNER == "docker":
            success, logs = run_pipeline_docker(run, env_var)
        elif settings.PIPELINE_SCHEDULER_SPAWNER == "kubernetes":
            success, logs = run_pipeline_kube(run, env_var)
        else:
            logger.error("Scheduler spawner %s not found", settings.SCHEDULER_SPAWNER)
            success, logs = False, ""
    except Exception as e:
        run.state = PipelineRunState.FAILED
        run.duration = timezone.now() - time_start
        run.run_logs = str(e)
        run.save()
        logger.info("Failure of run: %s", run)
        sys.exit(1)

    run.refresh_from_db()
    run.duration = timezone.now() - time_start
    run.run_logs = logs
    if success:
        run.state = PipelineRunState.SUCCESS
    else:
        run.state = PipelineRunState.FAILED
    run.save()
    logger.info("End of run pipeline: %s", run)

    sys.exit()


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("start pipeline runner")
        sleep(10)

        i = 0
        sleeptime = 5
        while True:
            # cycle DB connection because of fork()
            db.connections.close_all()

            # timeout-manager/zombie-reaper
            if i > 60:
                zombie_runs = PipelineRun.objects.filter(
                    state=PipelineRunState.RUNNING,
                    last_heartbeat__lt=(timezone.now() - timedelta(seconds=2 * 60)),
                )
                for run in zombie_runs:
                    logger.warning("Timeout kill run %s #%s", run.pipeline.name, run.id)
                    run.state = PipelineRunState.FAILED
                    run.run_logs = "Killed by timeout"
                    run.save()
                i = 0
            else:
                i += sleeptime

            runs = PipelineRun.objects.filter(state=PipelineRunState.QUEUED).order_by(
                "execution_date"
            )
            for run in runs:
                # mark all pipelines to be sure to never try executing them again
                run.state = PipelineRunState.RUNNING
                run.save()
            for run in runs:
                run_pipeline(run)

            sleep(sleeptime)
