import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useCallback, useEffect, useRef, useState } from "react";
import { getErrorCodeMessage } from "assistant/helpers";
import { InstructionSet } from "assistant/instructions";
import { getPublicEnv } from "core/helpers/runtimeConfig";
import useStreamingFetch from "core/hooks/useStreamingFetch";
import { AssistantToolName } from "graphql/types";
import { useCreateAssistantConversationMutation } from "assistant/graphql/mutations.generated";

export enum AIPhase {
  Idle = "idle",
  Generating = "generating",
  Creating = "creating",
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
  objectName: string | null;
  reset: () => void;
};

export type AIFormOptions = {
  workspaceSlug: string;
  instructionSet: InstructionSet;
  // The tool whose successful result means the object exists and the user can be redirected.
  createTool: AssistantToolName;
  getRedirectUrl: (toolOutput: unknown) => string | null;
  notCreatedMessage: string;
  failedMessage: string;
};

function getStreamUrl(conversationId: string): string {
  const apiBasePath =
    process.env.NEXT_PUBLIC_API_BASE_PATH ||
    getPublicEnv().OPENHEXA_BACKEND_URL;
  return `${apiBasePath}/assistant/conversations/${conversationId}/stream/`;
}

export function useAIForm({
  workspaceSlug,
  instructionSet,
  createTool,
  getRedirectUrl,
  notCreatedMessage,
  failedMessage,
}: AIFormOptions): AIFormInstance {
  const { t } = useTranslation();
  const router = useRouter();
  const [prompt, setPrompt] = useState("");
  const [phase, setPhase] = useState<AIPhase>(AIPhase.Idle);
  const [errorAtPhase, setErrorAtPhase] = useState<AIPhase | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [agentResponse, setAgentResponse] = useState<string | null>(null);
  const [objectName, setObjectName] = useState<string | null>(null);
  // SSE event handlers are closures created at mount time and can't see updated React state.
  // phaseRef mirrors the phase state so handlers always read the current value without stale closures.
  // Always update both together via setPhaseWithRef.
  const phaseRef = useRef<AIPhase>(AIPhase.Idle);
  const agentResponseRef = useRef<string>("");
  const navigationTriggeredRef = useRef(false);
  const pendingRedirectUrlRef = useRef<string | null>(null);
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
      const { tool_name, tool_args } = data as {
        tool_name: string;
        tool_args?: { name?: string };
      };
      if (tool_name === createTool) {
        if (tool_args?.name) setObjectName(tool_args.name);
        setPhaseWithRef(AIPhase.Creating);
      }
    },
    tool_result: (data) => {
      const { tool_name, success, tool_output } = data as {
        tool_name: string;
        success: boolean;
        tool_output: unknown;
      };
      if (tool_name === createTool && success) {
        const redirectUrl = getRedirectUrl(tool_output);
        if (redirectUrl) {
          pendingRedirectUrlRef.current = redirectUrl;
          navigationTriggeredRef.current = true;
          setPhaseWithRef(AIPhase.Done);
        }
      }
    },
    done: () => {
      if (phaseRef.current === AIPhase.Done && pendingRedirectUrlRef.current) {
        const redirectUrl = pendingRedirectUrlRef.current;
        navigationTimerRef.current = setTimeout(() => {
          router.push(redirectUrl);
        }, 500);
      }
    },
    error: (data) => {
      const { error_code } = (data ?? {}) as { error_code?: string };
      setError_(getErrorCodeMessage(t, error_code));
    },
  });

  useEffect(() => {
    if (streamError) {
      setError_(
        t(
          "Could not connect to the server. Please check your connection and try again.",
        ),
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

  const clearState = useCallback(() => {
    setError(null);
    setErrorAtPhase(null);
    setAgentResponse(null);
    setObjectName(null);
    agentResponseRef.current = "";
    navigationTriggeredRef.current = false;
    pendingRedirectUrlRef.current = null;
  }, []);

  const reset = useCallback(() => {
    clearNavigationTimer();
    setPrompt("");
    clearState();
    setPhaseWithRef(AIPhase.Idle);
  }, [setPhaseWithRef, clearNavigationTimer, clearState]);

  const cancel = useCallback(() => {
    clearNavigationTimer();
    abort();
    clearState();
    setPhaseWithRef(AIPhase.Idle);
  }, [abort, setPhaseWithRef, clearNavigationTimer, clearState]);

  const handleSubmit = useCallback(async () => {
    if (
      !prompt.trim() ||
      phase === AIPhase.Generating ||
      phase === AIPhase.Creating
    )
      return;
    clearNavigationTimer();
    clearState();
    setPhaseWithRef(AIPhase.Generating);
    try {
      const convResult = await createConversation({
        variables: {
          input: {
            workspaceSlug,
            instructionSet,
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
          phaseRef.current === AIPhase.Creating)
      ) {
        setError_(notCreatedMessage);
      }
    } catch {
      setError_(failedMessage);
    }
  }, [
    prompt,
    phase,
    createConversation,
    workspaceSlug,
    instructionSet,
    send,
    setPhaseWithRef,
    setError_,
    clearNavigationTimer,
    clearState,
    t,
    notCreatedMessage,
    failedMessage,
  ]);

  return {
    prompt,
    setPrompt,
    handleSubmit,
    cancel,
    isSubmitting:
      phase === AIPhase.Generating ||
      phase === AIPhase.Creating ||
      phase === AIPhase.Done,
    phase,
    errorAtPhase,
    error,
    agentResponse,
    objectName,
    reset,
  };
}
