import { panelCookieName, sanitizePanelLayout } from "./panelLayout";

describe("panelCookieName", () => {
  it("turns a route and a side into a name a cookie can carry", () => {
    expect(
      panelCookieName("/workspaces/[workspaceSlug]/data-studio", "left"),
    ).toBe("panel__workspaces__workspaceSlug__data-studio_left");
  });
});

describe("sanitizePanelLayout", () => {
  it("keeps a layout someone chose", () => {
    expect(sanitizePanelLayout({ size: 380, collapsed: true }, 240)).toEqual({
      size: 380,
      collapsed: true,
    });
  });

  it("falls back to the default size for anything that is not one", () => {
    const nonsense = [
      { size: "red;position:fixed" },
      { size: -40 },
      { size: 99_999_999 },
      { size: NaN },
      {},
    ];

    for (const layout of nonsense) {
      expect(sanitizePanelLayout(layout as never, 240).size).toBe(240);
    }
  });
});
