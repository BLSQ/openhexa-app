import { fileToBase64 } from "../fileEncoding";

describe("fileToBase64", () => {
  it("encodes a text blob to base64 without the data URL prefix", async () => {
    const blob = new Blob(["hello"], { type: "text/plain" });
    expect(await fileToBase64(blob)).toBe("aGVsbG8=");
  });

  it("returns an empty string for an empty blob", async () => {
    const blob = new Blob([], { type: "text/plain" });
    expect(await fileToBase64(blob)).toBe("");
  });

  it("rejects with the reader's error when reading fails", async () => {
    const fakeError = new Error("read failed");
    const spy = jest
      .spyOn(FileReader.prototype, "readAsDataURL")
      .mockImplementation(function (this: FileReader) {
        Object.defineProperty(this, "error", { value: fakeError });
        this.onerror?.(new ProgressEvent("error") as ProgressEvent<FileReader>);
      });

    await expect(fileToBase64(new Blob(["x"]))).rejects.toBe(fakeError);
    spy.mockRestore();
  });
});
