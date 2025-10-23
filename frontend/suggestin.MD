Now I'll propose a comprehensive fix for moving pipeline heartbeats from the pipeline runner subprocesses to the pipeline pods themselves.

  Problem Analysis

  Current Architecture (HEXA-1406 Issue):
  - Heartbeats are sent by the pipelines_runner process (lines 214-216 for Kubernetes, 343-346 for Docker in pipelines_runner.py:214)
  - The runner subprocess continuously polls the pod/container status and updates last_heartbeat field in the database
  - The runner acts as a proxy between the pod and the OpenHEXA backend
  - If the runner dies, heartbeats stop even if the pod is healthy

  Problems with Current Design:
  1. Single point of failure: Runner death means no heartbeats, causing false positives for zombie detection
  2. Tight coupling: Runner must constantly poll pods to prove they're alive
  3. Resource waste: Continuous polling and DB writes every 5 seconds
  4. Scalability: Each runner subprocess uses resources just for monitoring

  Proposed Solution

  Architecture Overview

  Move heartbeat responsibility from runner to the pipeline pods themselves using the OpenHEXA SDK.

  Implementation Plan

  Phase 1: Add GraphQL Mutation for Heartbeat

  1. Add heartbeat mutation to GraphQL schema (backend/hexa/pipelines/graphql/schema.graphql:777)
  """
  Updates the heartbeat timestamp for a running pipeline.
  """
  input UpdatePipelineHeartbeatInput {
    # No parameters needed - authenticated via PipelineRunUser token
  }

  """
  Represents the result of updating a pipeline heartbeat.
  """
  type UpdatePipelineHeartbeatResult {
    success: Boolean!
    errors: [PipelineError!]!
  }

  extend type Mutation {
    """
    Updates the heartbeat timestamp for the current pipeline run.
    Must be called by an authenticated pipeline run.
    """
    updatePipelineHeartbeat(input: UpdatePipelineHeartbeatInput!): UpdatePipelineHeartbeatResult!
  }
  2. Implement mutation resolver (backend/hexa/pipelines/schema/mutations.py:653)
  @pipelines_mutations.field("updatePipelineHeartbeat")
  def resolve_update_pipeline_heartbeat(_, info, **kwargs):
      request: HttpRequest = info.context["request"]
      if not request.user.is_authenticated or not isinstance(
          request.user, PipelineRunUser
      ):
          return {
              "success": False,
              "errors": ["PIPELINE_NOT_FOUND"],
          }

      try:
          pipeline_run = PipelineRun.objects.get(pk=request.user.pipeline_run.id)
      except PipelineRun.DoesNotExist:
          return {
              "success": False,
              "errors": ["PIPELINE_NOT_FOUND"],
          }

      if pipeline_run.state in [PipelineRunState.SUCCESS, PipelineRunState.FAILED, PipelineRunState.STOPPED]:
          return {
              "success": False,
              "errors": ["PIPELINE_ALREADY_COMPLETED"],
          }

      # Update heartbeat
      pipeline_run.last_heartbeat = timezone.now()
      pipeline_run.save(update_fields=["last_heartbeat"])

      return {"success": True, "errors": []}

  Phase 2: Add Heartbeat to OpenHEXA SDK

  3. Add heartbeat thread to SDK (in the OpenHEXA SDK repository)
    - Modify the SDK's pipeline run context to start a background thread
    - Thread sends heartbeat every 30-60 seconds (less frequent than current 5s)
    - Gracefully handle failures (log but don't fail the pipeline)

  Conceptual implementation:
  # In openhexa.sdk.pipelines.run
  import threading
  import time
  from datetime import datetime, timedelta

  class HeartbeatThread(threading.Thread):
      def __init__(self, run_context, interval=30):
          super().__init__(daemon=True)
          self.run_context = run_context
          self.interval = interval
          self.stop_event = threading.Event()
          self.last_successful_heartbeat = None

      def run(self):
          while not self.stop_event.is_set():
              try:
                  # Send heartbeat via GraphQL mutation
                  self.run_context._send_heartbeat()
                  self.last_successful_heartbeat = datetime.now()
              except Exception as e:
                  # Log error but don't crash pipeline
                  logger.warning(f"Failed to send heartbeat: {e}")

              # Wait for next interval
              self.stop_event.wait(self.interval)

      def stop(self):
          self.stop_event.set()

  Phase 3: Update Pipeline Runner

  4. Remove heartbeat loops from runner (backend/hexa/pipelines/management/commands/pipelines_runner.py)

  4. For Kubernetes spawner (lines 210-233):
  # REMOVE the heartbeat update from the monitoring loop
  while True:
      start_time = timezone.now()
      run.refresh_from_db()
      # REMOVE: run.last_heartbeat = start_time  # <-- Delete this
      # REMOVE: run.save()                       # <-- Delete this

      remote_pod = v1.read_namespaced_pod(pod.metadata.name, pod.metadata.namespace)
      duration = (timezone.now() - start_time).total_seconds()
      pod_read_durations.append(duration)

      if run.state == PipelineRunState.TERMINATING:
          break

      if (remote_pod and remote_pod.status
          and remote_pod.status.phase in {"Succeeded", "Failed"}):
          break

      sleep(5)

  4. For Docker spawner (lines 343-346):
  while True:
      run.refresh_from_db()
      # REMOVE: run.last_heartbeat = timezone.now()  # <-- Delete this
      # REMOVE: run.save()                           # <-- Delete this

      if run.state == PipelineRunState.TERMINATING:
          container.kill()
          return False, container.logs().decode("UTF-8")

      # ... rest of logic
  5. Increase heartbeat timeout (backend/hexa/pipelines/management/commands/pipelines_runner.py:23)
  # Since pods now send heartbeats less frequently, increase timeout
  HEARTBEAT_TIMEOUT = 5 * 60  # 5 minutes (was 15 minutes)
  # This gives 5x buffer for 60-second heartbeat interval

  Phase 4: Backward Compatibility & Rollout

  6. Hybrid approach for rollout:
    - Keep runner heartbeat initially as fallback
    - Add SDK version check or feature flag
    - Phase out runner heartbeat once all pipelines use new SDK version
  7. Add monitoring:
    - Log when heartbeats come from pods vs runner
    - Alert if heartbeat pattern changes unexpectedly
    - Track heartbeat latency

  Benefits of This Solution

  1. Decoupled architecture: Pods are self-reporting, runner just waits for completion
  2. More reliable: Pod health is reported directly from the pod
  3. Better resource usage: Less frequent heartbeats, no constant polling
  4. Scalability: Runner processes do less work per pipeline
  5. True health signal: Heartbeat proves code is executing, not just pod exists
  6. Graceful degradation: If heartbeat thread fails, pipeline continues but may be marked zombie

  Edge Cases Handled

  - Pod crashes: No more heartbeats → zombie reaper catches it
  - Network issues: Heartbeat thread retries, pipeline continues
  - SDK upgrade: Backward compatible, runner can still send heartbeats initially
  - Long-running operations: Heartbeat continues even during blocking operations

  Testing Strategy

  1. Unit tests: Mock GraphQL mutation, test heartbeat thread lifecycle
  2. Integration tests: Run pipeline with new SDK, verify heartbeats in DB
  3. Failure tests: Kill heartbeat thread, verify zombie detection
  4. Performance tests: Measure DB load reduction

  Rollout Plan

  1. Deploy GraphQL mutation (Phase 1)
  2. Release new SDK version with heartbeat thread (Phase 2)
  3. Monitor hybrid mode (both runner and pod sending heartbeats)
  4. Once >95% pipelines use new SDK, remove runner heartbeat (Phase 3)
  5. Update documentation and examples

⏺ ---
  Summary

  I've thoroughly analyzed the codebase and proposed a comprehensive fix for HEXA-1406: Pipeline heartbeats should come from the pipeline pods, not the pipeline runner subprocesses.

  Key Findings

  Current Problem:
  - Heartbeats are sent by the runner subprocess every 5 seconds (pipelines_runner.py:214-216, pipelines_runner.py:343-346)
  - Runner polls pods/containers to prove they're alive
  - Creates tight coupling and single point of failure

  Proposed Solution (4-Phase Approach):

  1. Phase 1: Add updatePipelineHeartbeat GraphQL mutation
  2. Phase 2: Implement heartbeat background thread in OpenHEXA SDK (30-60s interval)
  3. Phase 3: Remove heartbeat code from runner monitoring loops
  4. Phase 4: Gradual rollout with hybrid mode for backward compatibility

  Benefits:
  - Decoupled architecture (pods self-report)
  - Better resource usage (less DB writes)
  - True health signal (proves code is executing)
  - More reliable (no single point of failure)

  The solution ensures pods actively send their own heartbeats while the runner focuses solely on detecting pod completion, resulting in a cleaner separation of concerns and more reliable pipeline monitoring.
