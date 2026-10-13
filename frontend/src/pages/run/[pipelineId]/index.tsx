import { ExclamationCircleIcon, PlayIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import Block from "core/components/Block";
import Button from "core/components/Button";
import Field from "core/components/forms/Field";
import Page from "core/components/Page";
import { ensureArray } from "core/helpers/array";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import useForm from "core/hooks/useForm";
import PublicLayout from "core/layouts/public/PublicLayout";
import { RunPublicPipelineError } from "graphql/types";
import { getMe } from "identity/helpers/auth";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import {
  getPublicPipelineRunPath,
  PipelineVisibilityBadge,
} from "pipelines/features/PipelineVisibility";
import { useRunPublicPipelineMutation } from "pipelines/graphql/mutations.generated";
import {
  PublicPipelinePageDocument,
  PublicPipelinePageQuery,
  PublicPipelinePageQueryVariables,
  PublicPipelineRedirectDocument,
  PublicPipelineRedirectQuery,
  PublicPipelineRedirectQueryVariables,
  usePublicPipelinePageQuery,
} from "pipelines/graphql/queries.generated";
import { useMemo } from "react";
import ParameterField from "workspaces/features/RunPipelineDialog/ParameterField";
import {
  convertParametersToPipelineInput,
  getDisabledParameterCodes,
  getParameterDisablers,
} from "workspaces/helpers/pipelines";

type PublicPipelinePageProps = {
  pipelineId: string;
};

// Launcher of a public pipeline, reached by its permalink. Visitors only see the
// parameters they can fill in on their own (plain values); the rest runs with
// the defaults the publisher vetted. The run form of the Data Studio is not
// reused: it is a dialog bound to a workspace, with pickers for connections,
// datasets and files the visitor cannot open.
const PublicPipelinePage: NextPageWithLayout = ({
  pipelineId,
}: PublicPipelinePageProps) => {
  const { t } = useTranslation();
  const router = useRouter();
  const { data } = usePublicPipelinePageQuery({
    variables: { id: pipelineId },
  });
  const [runPipeline] = useRunPublicPipelineMutation();
  const pipeline = data?.publicPipeline;
  const parameters = useMemo(() => pipeline?.parameters ?? [], [pipeline]);

  const form = useForm<{ [key: string]: any }>({
    async onSubmit(values) {
      const { data } = await runPipeline({
        variables: {
          input: {
            id: pipelineId,
            config: convertParametersToPipelineInput({ parameters }, values),
          },
        },
      });
      const result = data?.runPublicPipeline;
      if (result?.success && result.run) {
        await router.push(getPublicPipelineRunPath(pipelineId, result.run.id));
        return;
      }
      const errors = result?.errors ?? [];
      if (errors.includes(RunPublicPipelineError.PublicRunInProgress)) {
        throw new Error(
          t(
            "A run of this pipeline is already in progress. Please wait for it to finish and try again.",
          ),
        );
      }
      if (errors.includes(RunPublicPipelineError.PipelineRunsLimitReached)) {
        throw new Error(
          t("This pipeline cannot run right now: its run limit was reached."),
        );
      }
      if (errors.includes(RunPublicPipelineError.InvalidConfig)) {
        throw new Error(t("Some of the values entered are not valid."));
      }
      throw new Error(t("This pipeline cannot be run from this page."));
    },
    getInitialState() {
      const initialState: { [key: string]: any } = {};
      for (const parameter of parameters) {
        if (parameter.default !== null && parameter.default !== undefined) {
          initialState[parameter.code] = parameter.default;
        }
      }
      return initialState;
    },
    validate(values) {
      const errors = {} as any;
      const disabledCodes = getDisabledParameterCodes(parameters, values);
      const normalized = convertParametersToPipelineInput(
        { parameters },
        values,
        disabledCodes,
      );
      for (const parameter of parameters) {
        if (disabledCodes.has(parameter.code)) {
          continue;
        }
        const value = normalized[parameter.code];
        if (parameter.type === "int" || parameter.type === "float") {
          if (ensureArray(value).length === 0 && parameter.required) {
            errors[parameter.code] = t("This field is required");
          } else if (ensureArray(value).some((v) => isNaN(v))) {
            errors[parameter.code] = t("This field must contain only numbers");
          }
        } else if (parameter.required && ensureArray(value).length === 0) {
          errors[parameter.code] = t("This field is required");
        }
      }
      return errors;
    },
  });

  const parameterDisablers = useMemo(
    () => getParameterDisablers(parameters, form.formData),
    [parameters, form.formData],
  );
  const parameterNameByCode = useMemo(
    () =>
      Object.fromEntries(parameters.map((param) => [param.code, param.name])),
    [parameters],
  );

  if (!pipeline) {
    return null;
  }

  return (
    <Page title={pipeline.name}>
      <PublicLayout>
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-semibold text-gray-900">
              {pipeline.name}
            </h1>
            <PipelineVisibilityBadge
              visibility={pipeline.visibility}
              size="sm"
            />
          </div>
          {pipeline.organizationName && (
            <p className="mt-1 text-sm text-gray-500">
              {t("Published by {{organization}}", {
                organization: pipeline.organizationName,
              })}
            </p>
          )}
        </div>

        {pipeline.description && (
          <Block>
            <Block.Content>
              <p className="text-sm whitespace-pre-line text-gray-700">
                {pipeline.description}
              </p>
            </Block.Content>
          </Block>
        )}

        <Block>
          <form onSubmit={form.handleSubmit}>
            <Block.Content className="space-y-4">
              {!pipeline.runnable && (
                <div className="flex items-center gap-2 rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-700">
                  <ExclamationCircleIcon className="h-4 w-4 shrink-0 text-amber-500" />
                  {t(
                    "This pipeline cannot be run from this page right now. Please contact the people who shared it with you.",
                  )}
                </div>
              )}
              {parameters.length > 0 ? (
                <div
                  className={clsx(
                    "grid gap-x-3 gap-y-4",
                    parameters.length > 4 && "sm:grid-cols-2 sm:gap-x-5",
                  )}
                >
                  {parameters.map((parameter) => {
                    const disablingCodes = parameterDisablers.get(
                      parameter.code,
                    );
                    const isDisabled = !!disablingCodes;
                    return (
                      <Field
                        key={parameter.code}
                        required={
                          (parameter.required || parameter.type === "bool") &&
                          !isDisabled
                        }
                        name={parameter.code}
                        label={parameter.name}
                        help={parameter.help}
                        note={
                          disablingCodes
                            ? t("Disabled by {{names}}", {
                                names: disablingCodes
                                  .map(
                                    (code) => parameterNameByCode[code] ?? code,
                                  )
                                  .join(", "),
                              })
                            : undefined
                        }
                        error={
                          form.touched[parameter.code] &&
                          form.errors[parameter.code]
                        }
                      >
                        <fieldset
                          disabled={isDisabled}
                          className={clsx(isDisabled && "opacity-50")}
                        >
                          <ParameterField
                            parameter={parameter}
                            value={
                              form.formData[parameter.code] ??
                              (parameter.multiple ? [] : "")
                            }
                            onChange={(value: any) =>
                              form.setFieldValue(parameter.code, value)
                            }
                            form={form}
                          />
                        </fieldset>
                      </Field>
                    );
                  })}
                </div>
              ) : (
                <p className="text-sm text-gray-500">
                  {t("This pipeline has no parameters to fill in.")}
                </p>
              )}
              {form.submitError && (
                <div className="flex items-center gap-2 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
                  <ExclamationCircleIcon className="h-4 w-4 shrink-0 text-red-500" />
                  {form.submitError}
                </div>
              )}
            </Block.Content>
            <Block.Content className="flex justify-end border-t border-gray-100">
              <Button
                type="submit"
                variant="primary"
                disabled={!pipeline.runnable || form.isSubmitting}
                leadingIcon={<PlayIcon className="h-4 w-4" />}
              >
                {t("Run")}
              </Button>
            </Block.Content>
          </form>
        </Block>
      </PublicLayout>
    </Page>
  );
};

PublicPipelinePage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: false,
  async getServerSideProps(ctx, client) {
    const pipelineId = ctx.params!.pipelineId as string;
    const [{ data }, me] = await Promise.all([
      client.query<PublicPipelinePageQuery, PublicPipelinePageQueryVariables>({
        query: PublicPipelinePageDocument,
        variables: { id: pipelineId },
      }),
      getMe(ctx),
    ]);

    if (data.publicPipeline) {
      return { props: { pipelineId } };
    }

    // The pipeline may exist but not be public: give anonymous visitors a chance
    // to log in before concluding it is not there.
    if (!me?.user) {
      return {
        redirect: {
          permanent: false,
          destination: `/login?next=${encodeURIComponent(ctx.resolvedUrl)}`,
        },
      };
    }

    // Whoever can see a pipeline that is not public is a member of its
    // workspace, and that is where they work with it.
    const { data: member } = await client.query<
      PublicPipelineRedirectQuery,
      PublicPipelineRedirectQueryVariables
    >({
      query: PublicPipelineRedirectDocument,
      variables: { id: pipelineId },
      fetchPolicy: "no-cache",
    });
    if (!member.pipeline) {
      return { notFound: true };
    }
    return {
      redirect: {
        permanent: false,
        destination: `/workspaces/${encodeURIComponent(
          member.pipeline.workspace.slug,
        )}/pipelines/${encodeURIComponent(member.pipeline.code)}`,
      },
    };
  },
});

export default PublicPipelinePage;
