import { FileType } from "graphql/types";
import { buildFileTree } from "./buildFileTree";
import { AugmentedFile } from "./types";

const makeNode = (overrides: Partial<AugmentedFile>): AugmentedFile => ({
  __typename: "FileNode",
  id: "id",
  name: "file.py",
  path: "file.py",
  type: FileType.File,
  content: "",
  parentId: null,
  autoSelect: false,
  language: null,
  lineCount: null,
  ...overrides,
});

describe("buildFileTree", () => {
  it("returns empty array for empty input", () => {
    expect(buildFileTree([])).toEqual([]);
  });

  it("root nodes have empty children array", () => {
    const tree = buildFileTree([makeNode({ id: "1" })]);
    expect(tree[0].children).toEqual([]);
  });

  it("attaches children to their parent", () => {
    const nodes = [
      makeNode({ id: "dir", name: "src", type: FileType.Directory, parentId: null }),
      makeNode({ id: "file", name: "main.py", parentId: "dir" }),
    ];
    const tree = buildFileTree(nodes);
    const dir = tree.find((n) => n.id === "dir")!;
    expect(dir.children).toHaveLength(1);
    expect(dir.children[0].id).toBe("file");
  });

  it("sorts children alphabetically by name", () => {
    const nodes = [
      makeNode({ id: "dir", name: "src", type: FileType.Directory }),
      makeNode({ id: "b", name: "b.py", path: "src/b.py", parentId: "dir" }),
      makeNode({ id: "a", name: "a.py", path: "src/a.py", parentId: "dir" }),
    ];
    const tree = buildFileTree(nodes);
    const dir = tree.find((n) => n.id === "dir")!;
    expect(dir.children.map((c) => c.name)).toEqual(["a.py", "b.py"]);
  });

  it("returns all nodes including children in the flat result", () => {
    const nodes = [
      makeNode({ id: "dir", name: "src", type: FileType.Directory }),
      makeNode({ id: "file", name: "main.py", parentId: "dir" }),
    ];
    expect(buildFileTree(nodes)).toHaveLength(2);
  });

  it("handles multiple levels of nesting", () => {
    const nodes = [
      makeNode({ id: "root", name: "root", type: FileType.Directory }),
      makeNode({ id: "sub", name: "sub", type: FileType.Directory, parentId: "root" }),
      makeNode({ id: "file", name: "deep.py", parentId: "sub" }),
    ];
    const tree = buildFileTree(nodes);
    const root = tree.find((n) => n.id === "root")!;
    const sub = root.children[0];
    expect(sub.children[0].id).toBe("file");
  });
});
