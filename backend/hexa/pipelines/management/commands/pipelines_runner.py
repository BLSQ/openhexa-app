import base64
import json
import os
import sys
from datetime import timedelta
from enum import Enum
from logging import getLogger
from time import sleep

import requests
from django import db
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.signing import Signer
from django.utils import timezone

from hexa.files import storage
from hexa.pipelines.models import PipelineRun, PipelineRunState, PipelineType
from hexa.pipelines.utils import generate_pipeline_container_name, mail_run_recipients

logger = getLogger(__name__)

HEARTBEAT_TIMEOUT = 15 * 60  # 15 minutes


class PodTerminationReason(Enum):
    DeadlineExceeded = "DeadlineExceeded"


def load_local_dev_kubernetes_config():
    """Load Kubernetes config for local dev (Docker Desktop for Mac/Windows)."""
    import tempfile

    import yaml
    from kubernetes import config

    kubeconfig_path = os.path.expanduser("~/.kube/config")
    with open(kubeconfig_path) as file:
        kubeconfig = yaml.safe_load(file)

    # Replace 127.0.0.1 with host.docker.internal for Docker containers
    for cluster in kubeconfig.get("clusters", []):
        server = cluster.get("cluster", {}).get("server", "")
        if "127.0.0.1" in server or "localhost" in server:
            cluster["cluster"]["server"] = server.replace(
                "127.0.0.1", "host.docker.internal"
            ).replace("localhost", "host.docker.internal")
            cluster["cluster"]["insecure-skip-tls-verify"] = True
            cluster["cluster"].pop("certificate-authority-data", None)

    # Write patched config to temp file and load it
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as temp_file:
        yaml.dump(kubeconfig, temp_file)
        temp_config = temp_file.name

    config.load_kube_config(config_file=temp_config)
    os.unlink(temp_config)


def create_pod_kube(run: PipelineRun, image: str, env_vars: dict):
    """Create a new Kubernetes pod for the pipeline run."""
    from kubernetes import config
    from kubernetes.client import CoreV1Api
    from kubernetes.client import models as k8s

    exec_time_str = timezone.now().replace(tzinfo=None, microsecond=0).isoformat()
    logger.debug(
        "K8S RUN %s: Creating new pod - %s for %s",
        os.getpid(),
        run.pipeline.name,
        exec_time_str,
    )

    is_local_dev = os.environ.get("IS_LOCAL_DEV", "false").lower() == "true"
    config.load_incluster_config() if not is_local_dev else load_local_dev_kubernetes_config()

    v1 = CoreV1Api()
    container_name = generate_pipeline_container_name(run)

    logger.info("Creating new pod %s for run %s", container_name, run.id)
    pod = k8s.V1Pod(
        api_version="v1",
        kind="Pod",
        metadata=k8s.V1ObjectMeta(
            namespace=os.environ.get("PIPELINE_NAMESPACE", "default"),
            name=container_name,
            labels={
                "hexa-workspace": env_vars["HEXA_WORKSPACE"],
                "hexa-run-id": str(run.id),
            },
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
            active_deadline_seconds=run.timeout,
            tolerations=(
                [
                    k8s.V1Toleration(
                        key="hub.jupyter.org_dedicated",
                        operator="Equal",
                        value="user",
                        effect="NoSchedule",
                    ),
                ]
                if not is_local_dev
                else []
            ),
            affinity=(
                k8s.V1Affinity(
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
                )
                if not is_local_dev
                else None
            ),
            containers=[
                k8s.V1Container(
                    image=image,
                    name=container_name,
                    image_pull_policy="IfNotPresent" if is_local_dev else "Always",
                    args=[
                        "pipeline",
                        "cloudrun",
                        "--config",
                        f"{base64.b64encode(json.dumps(run.config).encode('utf-8')).decode('utf-8')}",
                    ],
                    env=[
                        k8s.V1EnvVar(name="HEXA_ENVIRONMENT", value="CLOUD_PIPELINE"),
                        *[
                            k8s.V1EnvVar(
                                name=key,
                                value=value,
                            )
                            for key, value in env_vars.items()
                        ],
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
                            **(
                                {"smarter-devices/fuse": "1"}
                                if not is_local_dev
                                else {}
                            ),
                            "cpu": (
                                run.pipeline.cpu_limit
                                if run.pipeline.cpu_limit != ""
                                else settings.PIPELINE_DEFAULT_CONTAINER_CPU_LIMIT
                            ),
                            "memory": (
                                run.pipeline.memory_limit
                                if run.pipeline.memory_limit != ""
                                else settings.PIPELINE_DEFAULT_CONTAINER_MEMORY_LIMIT
                            ),
                        },
                        "requests": {
                            **(
                                {"smarter-devices/fuse": "1"}
                                if not is_local_dev
                                else {}
                            ),
                            "cpu": (
                                run.pipeline.cpu_request
                                if run.pipeline.cpu_request != ""
                                else settings.PIPELINE_DEFAULT_CONTAINER_CPU_REQUEST
                            ),
                            "memory": (
                                run.pipeline.memory_request
                                if run.pipeline.memory_request != ""
                                else settings.PIPELINE_DEFAULT_CONTAINER_MEMORY_REQUEST
                            ),
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
    return pod


def attach_to_pod_kube(run: PipelineRun):
    """Attach to an existing Kubernetes pod for the pipeline run."""
    from kubernetes import config
    from kubernetes.client import CoreV1Api

    exec_time_str = timezone.now().replace(tzinfo=None, microsecond=0).isoformat()
    logger.debug(
        "K8S RUN %s: Re-attaching to existing pod - %s for %s",
        os.getpid(),
        run.pipeline.name,
        exec_time_str,
    )

    is_local_dev = os.environ.get("IS_LOCAL_DEV", "false").lower() == "true"
    config.load_incluster_config() if not is_local_dev else load_local_dev_kubernetes_config()

    v1 = CoreV1Api()
    namespace = os.environ.get("PIPELINE_NAMESPACE", "default")
    container_name = generate_pipeline_container_name(run)

    logger.info(
        "Re-attaching to existing pod %s for run %s",
        container_name,
        run.id,
    )
    pod_list = v1.list_namespaced_pod(
        namespace=namespace, label_selector=f"hexa-run-id={run.id}"
    )

    if not pod_list.items:
        logger.info("No pod found for run %s, exiting attachment process", run.id)
        sys.exit(0)

    return pod_list.items[0]


def monitor_pod_kube(run: PipelineRun, pod):
    """Monitor a Kubernetes pod until completion and return success status and logs."""
    from kubernetes.client import CoreV1Api
    from kubernetes.client import models as k8s
    from kubernetes.client.rest import ApiException

    v1 = CoreV1Api()
    container_name = generate_pipeline_container_name(run)

    # monitor the pod
    while True:
        start_time = timezone.now()
        run.refresh_from_db()
        run.last_heartbeat = start_time
        run.save()

        remote_pod = v1.read_namespaced_pod(pod.metadata.name, pod.metadata.namespace)

        # if the run is flagged as TERMINATING stop the loop
        if run.state == PipelineRunState.TERMINATING:
            break

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
    except Exception as e:  # NOQA
        logger.exception("Could not get logs (%s)", e)
        stdout = ""

    # check termination reason
    if remote_pod.status.reason == PodTerminationReason.DeadlineExceeded.value:
        reason = f"Timeout killed run {run.pipeline.name} #{run.id}"
        stdout = "\n".join([stdout, reason])

    grace_period = None

    if run.state == PipelineRunState.TERMINATING:
        reason = f"Stop signal sent to run {run.pipeline.name} #{run.id}."
        stdout = "\n".join([stdout, reason])
        grace_period = 0

    # delete terminated pod
    try:
        v1.delete_namespaced_pod(
            name=pod.metadata.name,
            namespace=pod.metadata.namespace,
            body=k8s.V1DeleteOptions(),
            grace_period_seconds=grace_period,
        )
    except ApiException as e:
        # If the pod not found -> ignore exception, osef
        if e.status != 404:
            logger.exception("pod delete")

    success = (
        remote_pod.status.phase == "Succeeded"
        and run.state != PipelineRunState.TERMINATING
    )

    return success, stdout


def run_pipeline_docker(run: PipelineRun, image: str, env_vars: dict):
    import docker
    import urllib3

    del env_vars[
        "HEXA_PIPELINE_NAME"
    ]  # If there are spaces in the pipeline name, it will break the command

    cmd = (
        'pipeline cloudrun --config="'
        + base64.b64encode(json.dumps(run.config).encode("utf-8")).decode("utf-8")
        + '"'
    )
    try:
        docker_client = docker.DockerClient(base_url="unix://var/run/docker.sock")
        docker_client.ping()
    except:
        logger.exception("Docker client error", exc_info=True)
        raise

    env_vars.update(
        {
            "HEXA_ENVIRONMENT": "CLOUD_PIPELINE",
            "HEXA_RUN_ID": str(run.id),
        }
    )
    volumes = None
    if storage.storage_type == "local":
        # FIXME Get this from the storage directly
        workspace_folder = os.path.join(
            settings.WORKSPACE_STORAGE_LOCATION, run.pipeline.workspace.bucket_name
        )
        volumes = {
            workspace_folder: {
                "bind": "/home/hexa/workspace",
                "mode": "rw",
            }
        }
    container = docker_client.containers.run(
        image=image,
        command=cmd,
        privileged=True,
        network="openhexa",
        platform="linux/amd64",
        environment=env_vars,
        volumes=volumes,
        detach=True,
    )
    logger.debug("Container %s started", container.id)

    while True:
        run.refresh_from_db()
        run.last_heartbeat = timezone.now()
        run.save()
        # we stop the running process when the run state is a terminating
        if run.state == PipelineRunState.TERMINATING:
            container.kill()
            return False, container.logs().decode("UTF-8")

        try:
            logger.debug("Wait for container %s", container.id)
            r = container.wait(timeout=1)
            status_code = r["StatusCode"] == 0
            logs = container.logs().decode("UTF-8")
            container.remove()
            return status_code, logs
        except (
            urllib3.exceptions.ReadTimeoutError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectionError,
        ):
            logger.debug("Container wait timeout")
            continue
        except Exception as e:
            logger.exception("Container wait error", exc_info=True)
            return False, str(e)


def run_pipeline(run: PipelineRun, create_container: bool = True):
    action = "Run pipeline" if create_container else "Re-attaching to orphaned run"
    logger.info("%s: %s", action, run)

    if os.fork() != 0:
        # parent or error -> return
        return

    # force a cycle of the DB connection to stop interference with parent
    db.connections.close_all()
    run.refresh_from_db()

    # stringify env vars for kubernetes deployment
    env_vars = {
        "HEXA_SERVER_URL": f"{settings.INTERNAL_BASE_URL}",
        "HEXA_TOKEN": Signer().sign_object(run.access_token),
        "HEXA_WORKSPACE": run.pipeline.workspace.slug,
        "HEXA_RUN_ID": str(run.id),
        "HEXA_PIPELINE_CODE": run.pipeline.code,
        "HEXA_PIPELINE_NAME": run.pipeline.name,
        "HEXA_PIPELINE_TYPE": run.pipeline.type,
        "HEXA_LOG_LEVEL": str(run.log_level),
    }
    if run.pipeline.type == PipelineType.NOTEBOOK:
        env_vars.update({"HEXA_NOTEBOOK_PATH": run.pipeline.notebook_path})

    image = (
        run.pipeline.workspace.docker_image
        if run.pipeline.workspace.docker_image
        else settings.DEFAULT_WORKSPACE_IMAGE
    )
    spawner = settings.PIPELINE_SCHEDULER_SPAWNER

    time_start = timezone.now()
    base_logs = f"Running {run.pipeline.code} pipeline with the {spawner} spawner using the {image} image"

    try:
        if spawner == "docker":
            success, container_logs = run_pipeline_docker(run, image, env_vars)
        elif spawner == "kubernetes":
            pod = (
                create_pod_kube(run, image, env_vars)
                if create_container
                else attach_to_pod_kube(run)
            )
            success, container_logs = monitor_pod_kube(run, pod)
        else:
            logger.error(
                "Scheduler spawner %s not found", settings.PIPELINE_SCHEDULER_SPAWNER
            )
            success, container_logs = False, ""
    except Exception as e:
        run.state = PipelineRunState.FAILED
        run.duration = timezone.now() - time_start
        run.run_logs = "\n".join([base_logs, str(e)])
        run.save()
        logger.exception("Failure of run: %s", run)
        if run.send_mail_notifications:
            mail_run_recipients(run)
        sys.exit(1)

    run.refresh_from_db()
    run.duration = timezone.now() - time_start
    run.run_logs = "\n".join([base_logs, container_logs])

    if run.state == PipelineRunState.TERMINATING:
        run.state = PipelineRunState.STOPPED
    elif success:
        run.state = PipelineRunState.SUCCESS
    else:
        run.state = PipelineRunState.FAILED
    run.save()
    if run.send_mail_notifications:
        mail_run_recipients(run)
    logger.info("End of run pipeline: %s", run)

    sys.exit()


KILLED_BY_TIMEOUT_MESSAGE = "Killed due to heartbeat timeout"


def process_zombie_runs():
    """Check for zombie runs and update their status based on actual pod state."""
    zombie_runs = PipelineRun.objects.filter(
        state=PipelineRunState.RUNNING,
        last_heartbeat__lt=(timezone.now() - timedelta(seconds=HEARTBEAT_TIMEOUT)),
    )

    if not zombie_runs.exists():
        return

    if settings.PIPELINE_SCHEDULER_SPAWNER != "kubernetes":
        # For non-Kubernetes spawners, mark all zombie runs as failed
        for run in zombie_runs:
            logger.warning("Timeout kill run %s #%s", run.pipeline.name, run.id)
            run.state = PipelineRunState.FAILED
            run.run_logs = (
                "\n".join([run.run_logs, KILLED_BY_TIMEOUT_MESSAGE])
                if run.run_logs
                else KILLED_BY_TIMEOUT_MESSAGE
            )
            run.save()
        return

    from kubernetes import config
    from kubernetes.client import CoreV1Api

    is_local_dev = os.environ.get("IS_LOCAL_DEV", "false").lower() == "true"
    namespace = os.environ.get("PIPELINE_NAMESPACE", "default")
    try:
        config.load_incluster_config() if not is_local_dev else load_local_dev_kubernetes_config()
    except Exception as e:
        logger.exception(
            "Could not load Kubernetes config for zombie run killing : %s", e
        )
        return

    v1 = CoreV1Api()

    for run in zombie_runs:
        try:
            pod_list = v1.list_namespaced_pod(
                namespace=namespace, label_selector=f"hexa-run-id={run.id}"
            )
            pod = pod_list.items[0] if pod_list.items else None
        except Exception as e:
            logger.exception("Could not get pod for run %s: %s", run.id, e)
            pod = None

        if pod:
            phase = pod.status.phase
            container_name = (
                pod.spec.containers[0].name
                if pod.spec.containers
                else pod.metadata.name
            )
            logger.warning(
                "Zombie pod for run %s #%s is still in phase %s",
                run.pipeline.name,
                run.id,
                phase,
            )

            try:
                logs = v1.read_namespaced_pod_log(
                    name=pod.metadata.name,
                    namespace=namespace,
                    container=container_name,
                )
            except Exception as e:
                logger.exception("Could not get logs (%s)", e)
                logs = ""

            run.run_logs = logs or run.run_logs
            if phase in {"Succeeded", "Failed"}:
                run.state = (
                    PipelineRunState.SUCCESS
                    if phase == "Succeeded"
                    else PipelineRunState.FAILED
                )
                run.save()
                continue

        logger.warning("Timeout kill run %s #%s", run.pipeline.name, run.id)
        run.state = PipelineRunState.FAILED
        run.run_logs = (
            "\n".join([run.run_logs, KILLED_BY_TIMEOUT_MESSAGE])
            if run.run_logs
            else KILLED_BY_TIMEOUT_MESSAGE
        )
        run.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("start pipeline runner")
        sleep(10)

        orphaned_runs = list(
            PipelineRun.objects.filter(state=PipelineRunState.RUNNING).order_by(
                "execution_date"
            )
        )
        logger.info(
            "Found %d orphaned RUNNING pipeline(s) to re-attach gradually",
            len(orphaned_runs),
        )

        i = 0
        sleeptime = 5
        batch_size = 8
        while True:
            if orphaned_runs:
                batch = orphaned_runs[:batch_size]
                orphaned_runs = orphaned_runs[batch_size:]
                for run in batch:
                    if run.state == PipelineRunState.RUNNING:
                        run_pipeline(run, create_container=False)

            # cycle DB connection because of fork()
            db.connections.close_all()

            # timeout-manager/zombie-reaper
            if i > 60:
                process_zombie_runs()
                i = 0
            else:
                i += sleeptime

            # Process QUEUED runs in batches to prevent spikes
            runs = PipelineRun.objects.filter(state=PipelineRunState.QUEUED).order_by(
                "execution_date"
            )[:batch_size]

            for run in runs:
                # mark all pipelines to be sure to never try executing them again
                # we first update the status for all because the fork (in run_pipeline) closes the connection
                run.state = PipelineRunState.RUNNING
                run.save()
            for run in runs:
                run_pipeline(run)

            sleep(sleeptime)
