import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { TestApp } from "core/helpers/testutils";
import WebappHistory from "./WebappHistory";
import { WebappVersionsDocument } from "webapps/graphql/queries.generated";

jest.mock("next-i18next", () => ({
  useTranslation: jest.fn().mockReturnValue({ t: (key: string) => key }),
}));

const LATEST = "aaaaaaa1111111111111111111111111111111111";
const PUBLISHED = "bbbbbbb2222222222222222222222222222222222";
const OLDEST = "ccccccc3333333333333333333333333333333333";

const version = (id: string, message: string, date: string) => ({
  __typename: "WebappVersion",
  id,
  message,
  authorName: "Jane",
  authorEmail: "jane@example.com",
  date,
});

const versionsMock = {
  request: {
    query: WebappVersionsDocument,
    variables: {
      workspaceSlug: "ws",
      webappSlug: "app",
      page: 1,
      perPage: 20,
    },
  },
  maxUsageCount: Infinity,
  result: {
    data: {
      webapp: {
        __typename: "Webapp",
        id: "webapp-1",
        source: { __typename: "GitSource", publishedVersion: PUBLISHED },
        versions: {
          __typename: "WebappVersionsPage",
          items: [
            version(LATEST, "feat: latest change", "2026-10-30T10:00:00Z"),
            version(PUBLISHED, "feat: live change", "2026-10-30T09:00:00Z"),
            version(OLDEST, "Initial content", "2026-10-29T09:00:00Z"),
          ],
          page: 1,
        },
      },
    },
  },
};

const renderHistory = (
  props: Partial<React.ComponentProps<typeof WebappHistory>>,
) =>
  render(
    <TestApp mocks={[versionsMock]}>
      <WebappHistory workspaceSlug="ws" webappSlug="app" {...props} />
    </TestApp>,
  );

describe("WebappHistory", () => {
  it("marks the latest and the published versions", async () => {
    renderHistory({});

    const latestRow = await screen.findByTestId(`webapp-version-${LATEST}`);
    expect(latestRow).toHaveTextContent("Latest");
    expect(latestRow).not.toHaveTextContent("Published");

    const publishedRow = screen.getByTestId(`webapp-version-${PUBLISHED}`);
    expect(publishedRow).toHaveTextContent("Published");
    expect(publishedRow).not.toHaveTextContent("Latest");
  });

  it("offers preview, browse and roll back on older versions", async () => {
    const onPreviewCommit = jest.fn();
    const onBrowseCommit = jest.fn();
    const onRollbackCommit = jest.fn();
    renderHistory({
      onPreviewCommit,
      onBrowseCommit,
      onRollbackCommit,
      canEdit: true,
    });

    const row = await screen.findByTestId(`webapp-version-${OLDEST}`);
    fireEvent.click(
      screen.getAllByRole("button", { name: "Preview this version" })[2],
    );
    fireEvent.click(
      screen.getAllByRole("button", { name: "Browse at this point" })[2],
    );
    fireEvent.click(
      row.querySelector('[aria-label="Roll back to this version"]')!,
    );

    await waitFor(() => {
      expect(onPreviewCommit).toHaveBeenCalledWith(OLDEST);
      expect(onBrowseCommit).toHaveBeenCalledWith(OLDEST);
      expect(onRollbackCommit).toHaveBeenCalledWith(OLDEST);
    });
  });

  it("never offers to roll back to the latest version", async () => {
    renderHistory({ onRollbackCommit: jest.fn(), canEdit: true });

    const latestRow = await screen.findByTestId(`webapp-version-${LATEST}`);
    expect(
      latestRow.querySelector('[aria-label="Roll back to this version"]'),
    ).toBeNull();
    expect(
      screen.getAllByRole("button", { name: "Roll back to this version" }),
    ).toHaveLength(2);
  });

  it("hides roll back from users who cannot edit", async () => {
    renderHistory({ onRollbackCommit: jest.fn(), canEdit: false });

    await screen.findByTestId(`webapp-version-${LATEST}`);
    expect(
      screen.queryByRole("button", { name: "Roll back to this version" }),
    ).toBeNull();
  });
});
