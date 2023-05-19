import { faker } from "@faker-js/faker";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TestApp } from "core/helpers/testutils";
import {
  DeletePipelineVersionDocument,
  useDeletePipelineVersionMutation,
} from "workspaces/graphql/mutations.generated";
import DeletePipelineVersionDialog from "./DeletePipelineVersionDialog";

jest.mock("workspaces/graphql/mutations.generated", () => ({
  ...jest.requireActual("workspaces/graphql/mutations.generated"),
  __esModule: true,
  useDeletePipelineVersionMutation: jest.fn().mockReturnValue([]),
}));

const PIPELINE = {
  id: faker.datatype.uuid(),
  code: faker.science.chemicalElement().name,
};
const VERSION = {
  id: faker.datatype.uuid(),
  number: faker.datatype.number(),
};
const useDeletePipelineVersionMutationMock =
  useDeletePipelineVersionMutation as jest.Mock;

describe("DeletePipelineVersionDialog", () => {
  const onClose = jest.fn();
  beforeEach(() => {
    useDeletePipelineVersionMutationMock.mockClear();
  });

  it("is not displayed ", async () => {
    const { container } = render(
      <DeletePipelineVersionDialog
        open={false}
        pipeline={PIPELINE}
        version={VERSION}
        onClose={() => {}}
      />
    );
    const dialog = await screen.queryByRole("dialog");
    expect(dialog).not.toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(container).toMatchSnapshot();
  });

  it("is displayed when open is true", async () => {
    const { container } = render(
      <TestApp mocks={[]}>
        <DeletePipelineVersionDialog
          open={true}
          pipeline={PIPELINE}
          version={VERSION}
          onClose={() => {}}
        />
      </TestApp>
    );

    const dialog = await screen.queryByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(onClose).not.toHaveBeenCalled();
    expect(container).toMatchSnapshot();
  });

  it("Archives a workspace ", async () => {
    const { useArchiveWorkspaceMutation } = jest.requireActual(
      "workspaces/graphql/mutations.generated"
    );
    useDeletePipelineVersionMutationMock.mockImplementation(
      useArchiveWorkspaceMutation
    );

    const user = userEvent.setup();
    const mocks = [
      {
        request: {
          query: DeletePipelineVersionDocument,
          variables: {
            input: {
              pipelineId: PIPELINE.id,
              versionId: VERSION.id,
            },
          },
        },
        result: {
          data: {
            archiveWorkspace: {
              success: true,
              errors: [],
            },
          },
        },
      },
    ];
    render(
      <TestApp mocks={mocks}>
        <DeletePipelineVersionDialog
          open={true}
          pipeline={PIPELINE}
          version={VERSION}
          onClose={() => {}}
        />
      </TestApp>
    );
    expect(useDeletePipelineVersionMutation).toHaveBeenCalled();
  });
});
