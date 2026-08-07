import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import TagFilter from "./TagFilter";

jest.mock("next-i18next", () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

const TAGS = ["analytics", "covid", "malaria"];

const openPanel = async (user: ReturnType<typeof userEvent.setup>) => {
  await user.click(screen.getByText("Tags"));
  await waitFor(() => {
    expect(screen.getByText("Filter by tags")).toBeInTheDocument();
  });
};

describe("TagFilter", () => {
  const onChange = jest.fn();

  it("renders nothing when there is no tag to filter on", () => {
    const { container: empty } = render(
      <TagFilter tags={[]} value={[]} onChange={onChange} />,
    );
    expect(empty).toBeEmptyDOMElement();

    const { container: nullish } = render(
      <TagFilter tags={null} value={[]} onChange={onChange} />,
    );
    expect(nullish).toBeEmptyDOMElement();

    const { container: undef } = render(
      <TagFilter value={[]} onChange={onChange} />,
    );
    expect(undef).toBeEmptyDOMElement();
  });

  it("lists the available tags once opened", async () => {
    const user = userEvent.setup();
    render(<TagFilter tags={TAGS} value={[]} onChange={onChange} />);

    expect(screen.queryByText("covid")).not.toBeInTheDocument();

    await openPanel(user);

    for (const tag of TAGS) {
      expect(screen.getByText(tag)).toBeInTheDocument();
    }
    expect(screen.getAllByRole("checkbox")).toHaveLength(TAGS.length);
  });

  it("adds a tag to the selection", async () => {
    const user = userEvent.setup();
    render(<TagFilter tags={TAGS} value={[]} onChange={onChange} />);

    await openPanel(user);
    await user.click(screen.getByText("covid"));

    expect(onChange).toHaveBeenCalledWith(["covid"]);
  });

  it("removes an already selected tag from the selection", async () => {
    const user = userEvent.setup();
    render(
      <TagFilter
        tags={TAGS}
        value={["covid", "analytics"]}
        onChange={onChange}
      />,
    );

    await openPanel(user);
    await user.click(screen.getByText("covid"));

    expect(onChange).toHaveBeenCalledWith(["analytics"]);
  });

  it("checks the boxes of the selected tags", async () => {
    const user = userEvent.setup();
    render(<TagFilter tags={TAGS} value={["malaria"]} onChange={onChange} />);

    await openPanel(user);

    const checkboxes = screen.getAllByRole("checkbox");
    expect(checkboxes[0]).not.toBeChecked();
    expect(checkboxes[1]).not.toBeChecked();
    expect(checkboxes[2]).toBeChecked();
  });

  it("displays the number of selected tags", () => {
    render(
      <TagFilter
        tags={TAGS}
        value={["covid", "malaria"]}
        onChange={onChange}
      />,
    );

    expect(screen.getByText("2")).toBeInTheDocument();
  });

  it("clears the selection", async () => {
    const user = userEvent.setup();
    render(<TagFilter tags={TAGS} value={["covid"]} onChange={onChange} />);

    await openPanel(user);
    await user.click(screen.getByText("Clear"));

    expect(onChange).toHaveBeenCalledWith([]);
  });

  it("does not offer to clear an empty selection", async () => {
    const user = userEvent.setup();
    render(<TagFilter tags={TAGS} value={[]} onChange={onChange} />);

    await openPanel(user);

    expect(screen.queryByText("Clear")).not.toBeInTheDocument();
  });
});
