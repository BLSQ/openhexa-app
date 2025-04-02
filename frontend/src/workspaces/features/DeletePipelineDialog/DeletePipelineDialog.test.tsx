import { faker } from "@faker-js/faker";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";

import DeletePipelineDialog from "./DeletePipelineDialog";
import {
  DeletePipelineDocument,
  useDeletePipelineMutation,
} from "workspaces/graphql/mutations.generated";

jest.mock("workspaces/graphql/mutations.generated", () => ({
  ...jest.requireActual("workspaces/graphql/mutations.generated"),
  __esModule: true,
  useDeletePipelineMutation: jest.fn().mockReturnValue([]),
}));

const PIPELINE = {
  id: faker.string.uuid(),
  code: faker.science.chemicalElement().name,
};
const WORKSPACE = {
  slug: faker.lorem.slug(5),
};
const useDeletePipelineMutationMock = useDeletePipelineMutation as jest.Mock;

const windowAlertSpy = jest.spyOn(window, "alert").mockImplementation(() => {});

describe("DeletePipelineDialog", () => {
  const onClose = jest.fn();
  beforeEach(() => {
    useDeletePipelineMutationMock.mockClear();
    windowAlertSpy.mockClear();
  });

  it("is displayed when open is true", async () => {
    const { container } = render(
      <TestApp mocks={[]}>
        <DeletePipelineDialog
          open
          pipeline={PIPELINE}
          workspace={WORKSPACE}
          onClose={() => {}}
        />
        ,
      </TestApp>,
    );

    const dialog = await screen.queryByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(container).toMatchSnapshot();
  });

  it("Deletes a pipeline ", async () => {
    const { useArchiveWorkspaceMutation } = jest.requireActual(
      "workspaces/graphql/mutations.generated",
    );
    useDeletePipelineMutationMock.mockImplementation(
      useArchiveWorkspaceMutation,
    );

    const mocks = [
      {
        request: {
          query: DeletePipelineDocument,
          variables: {
            input: {
              id: PIPELINE.id,
            },
          },
        },
        result: {
          data: {
            deletePipeline: {
              success: true,
              errors: [],
            },
          },
        },
      },
    ];
    render(
      <TestApp mocks={mocks}>
        <DeletePipelineDialog
          open={false}
          pipeline={PIPELINE}
          workspace={WORKSPACE}
          onClose={() => {}}
        />
        ,
      </TestApp>,
    );
    expect(useDeletePipelineMutation).toHaveBeenCalled();
    expect(windowAlertSpy).not.toHaveBeenCalled();
  });
  it("Shows an alert if an error occurs ", async () => {
    const { useArchiveWorkspaceMutation } = jest.requireActual(
      "workspaces/graphql/mutations.generated",
    );
    useDeletePipelineMutationMock.mockImplementation(
      useArchiveWorkspaceMutation,
    );

    const mocks = [
      {
        request: {
          query: DeletePipelineDocument,
          variables: {
            input: {
              id: PIPELINE.id,
            },
          },
        },
        result: {
          data: {
            deletePipeline: {
              success: false,
              errors: [],
            },
          },
        },
      },
    ];
    render(
      <TestApp mocks={mocks}>
        <DeletePipelineDialog
          open={false}
          pipeline={PIPELINE}
          workspace={WORKSPACE}
          onClose={() => {}}
        />
        ,
      </TestApp>,
    );
    expect(useDeletePipelineMutation).toHaveBeenCalled();
    expect(windowAlertSpy).not.toHaveBeenCalled();
  });
});
