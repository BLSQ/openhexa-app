import { render, screen } from "@testing-library/react";
import { getApolloClient } from "core/helpers/apollo";
import { DatasetVisibility } from "graphql/types";
import PublicDatasetPage, {
  getServerSideProps,
} from "pages/datasets/[publicSlug]";

const mockPageQuery = jest.fn();
const mockExplorer = jest.fn();

jest.mock("identity/hooks/useMe", () => () => ({ user: null, features: [] }));

jest.mock("next/router", () => ({
  useRouter: () => ({ asPath: "/datasets/malaria" }),
}));

jest.mock("datasets/graphql/queries.generated", () => ({
  ...jest.requireActual("datasets/graphql/queries.generated"),
  usePublicDatasetPageQuery: () => mockPageQuery(),
}));

jest.mock("datasets/features/DatasetExplorer", () => ({
  __esModule: true,
  default: (props: any) => mockExplorer(props),
}));

jest.mock("datasets/features/DatasetVersionPicker", () => ({
  __esModule: true,
  default: () => null,
}));

jest.mock("core/components/MarkdownViewer", () => ({
  __esModule: true,
  default: ({ markdown }: { markdown: string }) => <div>{markdown}</div>,
}));

jest.mock("core/helpers/apollo", () => ({
  ...jest.requireActual("core/helpers/apollo"),
  __esModule: true,
  getApolloClient: jest.fn(),
  addApolloState: jest.fn(() => ({ props: {} })),
}));

jest.mock("identity/helpers/auth", () => ({
  ...jest.requireActual("identity/helpers/auth"),
  __esModule: true,
  getMe: jest.fn().mockResolvedValue({ user: null, features: [] }),
}));

jest.mock("next-i18next/serverSideTranslations", () => ({
  serverSideTranslations: jest.fn().mockResolvedValue({}),
}));

const file = { id: "f1", filename: "cases.csv" };
const version = {
  id: "v1",
  name: "v3",
  changelog: "Adds September",
  createdAt: "2026-10-09T16:42:00Z",
  files: { items: [file, { id: "f2", filename: "districts.csv" }] },
};
const publicDataset = {
  id: "d1",
  publicSlug: "malaria",
  name: "Malaria indicators",
  description: "Monthly indicators",
  visibility: DatasetVisibility.Public,
  workspaceName: "Malaria Workspace",
  organizationName: "Health Org",
  latestVersion: version,
};

const renderPage = (dataset: any) => {
  mockExplorer.mockReturnValue(null);
  mockPageQuery.mockReturnValue({ data: { publicDataset: dataset } });
  return render(<PublicDatasetPage publicSlug="malaria" />);
};

describe("PublicDatasetPage", () => {
  it("shows the dataset, its publisher and its latest version", () => {
    renderPage(publicDataset);

    expect(screen.getByRole("heading", { name: "Malaria indicators" }));
    expect(screen.getByText("Public")).toBeInTheDocument();
    expect(
      screen.getByText("Published by {{workspace}} ({{organization}})"),
    ).toBeInTheDocument();
    expect(screen.getByText("Monthly indicators")).toBeInTheDocument();
    expect(screen.getByText("Adds September")).toBeInTheDocument();
    expect(mockExplorer).toHaveBeenCalledWith(
      expect.objectContaining({ version, currentFile: file }),
    );
  });

  it("tells visitors when there is nothing to explore yet", () => {
    renderPage({ ...publicDataset, latestVersion: null });

    expect(
      screen.getByText("This dataset has no versions yet."),
    ).toBeInTheDocument();
    expect(mockExplorer).not.toHaveBeenCalled();
  });
});

describe("PublicDatasetPage getServerSideProps", () => {
  const ctx = {
    params: { publicSlug: "malaria" },
    req: { headers: {} },
    res: {},
    resolvedUrl: "/datasets/malaria",
  } as any;

  const mockClient = (dataset: any) =>
    (getApolloClient as jest.Mock).mockReturnValue({
      query: jest.fn(() =>
        Promise.resolve({ data: { publicDataset: dataset } }),
      ),
    });

  it("renders a public dataset", async () => {
    mockClient(publicDataset);

    const result: any = await getServerSideProps(ctx);

    expect(result.props).toMatchObject({ publicSlug: "malaria" });
  });

  // Members are not redirected: a dataset that is not public has no permalink.
  it("returns notFound when the dataset is not public", async () => {
    mockClient(null);

    const result: any = await getServerSideProps(ctx);

    expect(result.notFound).toBe(true);
  });
});
