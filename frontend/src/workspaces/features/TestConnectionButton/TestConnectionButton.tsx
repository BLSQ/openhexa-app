import {
  CheckCircleIcon,
  XCircleIcon,
} from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Spinner from "core/components/Spinner";
import { FormInstance } from "core/hooks/useForm";
import { ConnectionType } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useCallback, useState } from "react";
import { useTestConnectionMutation } from "workspaces/graphql/mutations.generated";
import {
  ConnectionForm,
  convertFieldsToInput,
  FieldForm,
} from "workspaces/helpers/connections/utils";
import Connections from "workspaces/helpers/connections";

type TestResult = { success: boolean; error?: string | null };

function TestConnectionBanner({ result }: { result: TestResult }) {
  const { t } = useTranslation();

  return (
    <div
      className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm ${
        result.success
          ? "bg-green-50 text-green-800"
          : "bg-red-50 text-red-800"
      }`}
    >
      {result.success ? (
        <CheckCircleIcon className="h-5 w-5 shrink-0 text-green-500" />
      ) : (
        <XCircleIcon className="h-5 w-5 shrink-0 text-red-500" />
      )}
      <p>
        {result.success
          ? t("Connection successful!")
          : result.error ||
            t(
              "Authentication failed. Please check your endpoint and/or parameters",
            )}
      </p>
    </div>
  );
}

export default function TestConnectionButton({
  connectionType,
  form,
}: {
  connectionType: ConnectionType;
  form: FormInstance<ConnectionForm>;
}) {
  const { t } = useTranslation();
  const router = useRouter();
  const workspaceSlug = router.query.workspaceSlug as string;
  const [testConnection] = useTestConnectionMutation();
  const [testing, setTesting] = useState(false);
  const [result, setResult] = useState<TestResult | null>(null);

  const handleTest = useCallback(
    async (event: React.MouseEvent<HTMLButtonElement>) => {
      const formEl = (event.currentTarget as HTMLElement).closest("form");
      if (formEl && !formEl.reportValidity()) {
        return;
      }

      setTesting(true);
      setResult(null);
      try {
        const definition = Connections[connectionType];
        const { name, description, ...rest } = form.formData;
        const fields =
          connectionType !== ConnectionType.Custom
            ? convertFieldsToInput(definition, rest)
            : (rest.fields?.map((field: FieldForm) => ({
                code: field.code,
                value: field.value,
                secret: Boolean(field.secret),
              })) ?? []);

        const { data } = await testConnection({
          variables: { input: { workspaceSlug, type: connectionType, fields } },
        });
        if (data) {
          setResult(data.testConnection);
        }
      } catch {
        setResult({
          success: false,
          error: t("An unexpected error occurred."),
        });
      } finally {
        setTesting(false);
      }
    },
    [connectionType, form.formData, testConnection, t, workspaceSlug],
  );

  return (
    <>
      {result && <TestConnectionBanner result={result} />}
      <Button
        type="button"
        variant="secondary"
        size="md"
        disabled={testing}
        onClick={handleTest}
        data-testid="test-connection"
      >
        {testing && <Spinner size="xs" className="mr-1" />}
        {t("Test connection")}
      </Button>
    </>
  );
}
