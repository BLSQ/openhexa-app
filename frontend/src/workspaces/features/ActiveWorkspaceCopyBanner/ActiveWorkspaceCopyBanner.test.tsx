import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { WorkspaceCopyRunStatus } from "graphql/types";
import ActiveWorkspaceCopyBanner from "./ActiveWorkspaceCopyBanner";

const RUN = {
  id: "run-1",
  status: WorkspaceCopyRunStatus.Running,
  targetWorkspaceName: "Malaria (copy)",
  sourceWorkspaceSlug: "malaria",
  sourceWorkspace: { slug: "malaria", name: "Malaria" },
  error: null,
  workspace: null,
};

describe("ActiveWorkspaceCopyBanner", () => {
  it("opens the copy's progress", async () => {
    const user = userEvent.setup();
    const onViewProgress = jest.fn();
    render(
      <ActiveWorkspaceCopyBanner run={RUN} onViewProgress={onViewProgress} />,
    );

    expect(screen.getByRole("status")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "View progress" }));

    expect(onViewProgress).toHaveBeenCalled();
  });
});
