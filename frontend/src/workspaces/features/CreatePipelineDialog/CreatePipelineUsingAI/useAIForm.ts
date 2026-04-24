import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useCallback, useEffect, useRef, useState } from "react";
import { InstructionSet } from "assistant/instructions";
import { getPublicEnv } from "core/helpers/runtimeConfig";
import useStreamingFetch from "core/hooks/useStreamingFetch";
import { CreatePipelineDialog_WorkspaceFragment } from "../CreatePipelineDialog.generated";
import { useCreateAssistantConversationMutation } from "assistant/graphql/mutations.generated";

export enum AIPhase {
  Idle = "idle",
  Generating = "generating",
  CreatingPipeline = "creating_pipeline",
  Done = "done",
  Error = "error",
}

export type AIFormInstance = {
  prompt: string;
  setPrompt: (value: string) => void;
  handleSubmit: () => void;
  cancel: () => void;
  isSubmitting: boolean;
  phase: AIPhase;
  errorAtPhase: AIPhase | null;
  error: string | null;
  agentResponse: string | null;
  reset: () => void;
};

function getStreamUrl(conversationId: string): string {
  const apiBasePath =
    process.env.NEXT_PUBLIC_API_BASE_PATH ?? getPublicEnv().OPENHEXA_BACKEND_URL;
  return `${apiBasePath}/assistant/conversations/${conversationId}/stream/`;
}

export function useAIForm(
  workspace: CreatePipelineDialog_WorkspaceFragment,
): AIFormInstance {
  const { t } = useTranslation();
  const router = useRouter();
  const [prompt, setPrompt] = useState("");
  const [phase, setPhase] = useState<AIPhase>(AIPhase.Idle);
  const [errorAtPhase, setErrorAtPhase] = useState<AIPhase | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [agentResponse, setAgentResponse] = useState<string | null>(null);
  // SSE event handlers are closures created at mount time and can't see updated React state.
  // phaseRef mirrors the phase state so handlers always read the current value without stale closures.
  // Always update both together via setPhaseWithRef.
  const phaseRef = useRef<AIPhase>(AIPhase.Idle);
  const agentResponseRef = useRef<string>("");
  const navigationTriggeredRef = useRef(false);
  const pendingPipelineCodeRef = useRef<string | null>(null);
  const navigationTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [createConversation] = useCreateAssistantConversationMutation();

  const setPhaseWithRef = useCallback((newPhase: AIPhase) => {
    phaseRef.current = newPhase;
    setPhase(newPhase);
  }, []);

  const setError_ = useCallback(
    (msg: string) => {
      setErrorAtPhase(phaseRef.current);
      setPhaseWithRef(AIPhase.Error);
      setError(msg);
      if (agentResponseRef.current) {
        setAgentResponse(agentResponseRef.current);
      }
    },
    [setPhaseWithRef],
  );

  const { send, abort, streamError } = useStreamingFetch({
    text_delta: (data) => {
      const { delta } = data as { delta: string };
      agentResponseRef.current += delta;
    },
    tool_call: (data) => {
      const { tool_name } = data as { tool_name: string };
      if (tool_name === "create_pipeline") {
        setPhaseWithRef(AIPhase.CreatingPipeline);
      }
    },
    tool_result: (data) => {
      const { tool_name, success, tool_output } = data as {
        tool_name: string;
        success: boolean;
        tool_output: unknown;
      };
      if (tool_name === "create_pipeline" && success) {
        const output = tool_output as { pipeline?: { code?: string } };
        const pipelineCode = output?.pipeline?.code;
        if (pipelineCode) {
          pendingPipelineCodeRef.current = pipelineCode;
          navigationTriggeredRef.current = true;
          setPhaseWithRef(AIPhase.Done);
        }
      }
    },
    done: () => {
      if (phaseRef.current === AIPhase.Done && pendingPipelineCodeRef.current) {
        const code = pendingPipelineCodeRef.current;
        const workspaceSlug = router.query.workspaceSlug as string;
        navigationTimerRef.current = setTimeout(() => {
          router.push(
            `/workspaces/${encodeURIComponent(workspaceSlug)}/pipelines/${encodeURIComponent(code)}/code`,
          );
        }, 500);
      }
    },
    error: (data) => {
      const { message } = (data ?? {}) as { message?: string };
      setError_(
        message ?? t("The AI service encountered an error. Please try again."),
      );
    },
  });

  useEffect(() => {
    if (streamError) {
      setError_(
        t("Could not connect to the server. Please check your connection and try again."),
      );
    }
  }, [streamError, setError_, t]);

  // Warn if the user tries to navigate away while the AI is working
  useEffect(() => {
    if (phase === AIPhase.Idle || phase === AIPhase.Error) return;
    const handler = (e: BeforeUnloadEvent) => {
      e.preventDefault();
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [phase]);

  useEffect(() => {
    return () => {
      if (navigationTimerRef.current !== null) {
        clearTimeout(navigationTimerRef.current);
      }
    };
  }, []);

  const clearNavigationTimer = useCallback(() => {
    if (navigationTimerRef.current !== null) {
      clearTimeout(navigationTimerRef.current);
      navigationTimerRef.current = null;
    }
  }, []);

  const reset = useCallback(() => {
    clearNavigationTimer();
    setPrompt("");
    setError(null);
    setErrorAtPhase(null);
    setAgentResponse(null);
    agentResponseRef.current = "";
    setPhaseWithRef(AIPhase.Idle);
    navigationTriggeredRef.current = false;
    pendingPipelineCodeRef.current = null;
  }, [setPhaseWithRef, clearNavigationTimer]);

  const cancel = useCallback(() => {
    clearNavigationTimer();
    abort();
    setPhaseWithRef(AIPhase.Idle);
    setError(null);
    setErrorAtPhase(null);
    setAgentResponse(null);
    agentResponseRef.current = "";
    navigationTriggeredRef.current = false;
    pendingPipelineCodeRef.current = null;
  }, [abort, setPhaseWithRef, clearNavigationTimer]);

  const handleSubmit = useCallback(async () => {
    if (
      !prompt.trim() ||
      phase === AIPhase.Generating ||
      phase === AIPhase.CreatingPipeline
    )
      return;
    clearNavigationTimer();
    setPhaseWithRef(AIPhase.Generating);
    setError(null);
    setErrorAtPhase(null);
    setAgentResponse(null);
    agentResponseRef.current = "";
    navigationTriggeredRef.current = false;
    pendingPipelineCodeRef.current = null;
    try {
      const convResult = await createConversation({
        variables: {
          input: {
            workspaceSlug: workspace.slug,
            instructionSet: InstructionSet.CREATE_PIPELINE,
          },
        },
      });
      const conversationId =
        convResult.data?.createAssistantConversation.conversation?.id;
      if (!conversationId) {
        setError_(t("Failed to start AI conversation."));
        return;
      }
      await send(getStreamUrl(conversationId), { message: prompt });
      // If the stream ends without a successful tool_result (e.g. the agent
      // responded in text only), fall back to an error so the user can retry.
      if (
        !navigationTriggeredRef.current &&
        (phaseRef.current === AIPhase.Generating ||
          phaseRef.current === AIPhase.CreatingPipeline)
      ) {
        setError_(t("The AI could not create the pipeline. Please try again."));
      }
    } catch {
      setError_(t("An error occurred while creating the pipeline."));
    }
  }, [prompt, phase, createConversation, workspace.slug, send, setPhaseWithRef, setError_, clearNavigationTimer, t]);

  return {
    prompt,
    setPrompt,
    handleSubmit,
    cancel,
    isSubmitting:
      phase === AIPhase.Generating ||
      phase === AIPhase.CreatingPipeline ||
      phase === AIPhase.Done,
    phase,
    errorAtPhase,
    error,
    agentResponse,
    reset,
  };
}
