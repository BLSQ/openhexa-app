import nextConfig from "../../../next.config";

describe("next.config headers", () => {
  it("forbids other origins from framing any page", async () => {
    const rules = await nextConfig.headers();

    const rule = rules.find(({ source }) => source === "/:path*");
    expect(rule?.headers).toEqual(
      expect.arrayContaining([
        { key: "X-Frame-Options", value: "SAMEORIGIN" },
        { key: "Content-Security-Policy", value: "frame-ancestors 'self'" },
      ]),
    );
  });
});
