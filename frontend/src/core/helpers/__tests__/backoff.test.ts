import Backoff from "../backoff";

describe("Backoff", () => {
  beforeEach(() => {
    jest.spyOn(global.Math, "random").mockReturnValue(0.1);
  });
  afterEach(() => {
    jest.spyOn(global.Math, "random").mockRestore();
  });

  it("should return a duration", () => {
    const backoff = new Backoff({ min: 100, max: 10000, factor: 2, jitter: 0 });
    expect(backoff.attempts).toBe(0);
    expect(backoff.duration()).toBe(100);
    expect(backoff.attempts).toBe(1);
  });

  it("should return a duration with jitter", () => {
    const backoff = new Backoff({
      min: 100,
      max: 10000,
      factor: 2,
      jitter: 0.5,
    });
    expect(backoff.duration()).toBe(105);
  });

  it("should return the duration with the factor applied", () => {
    const backoff = new Backoff({
      min: 100,
      max: 2000,
      factor: 2,
      jitter: 0,
    });

    expect(backoff.duration()).toBe(100);
    expect(backoff.duration()).toBe(200);
    expect(backoff.duration()).toBe(400);
    expect(backoff.duration()).toBe(800);
    expect(backoff.duration()).toBe(1600);
    expect(backoff.duration()).toBe(2000);
    expect(backoff.duration()).toBe(2000);

    expect(backoff.attempts).toBe(7);
  });

  it("resets the attempts", () => {
    const backoff = new Backoff({
      min: 100,
      max: 2000,
      factor: 2,
      jitter: 0,
    });

    expect(backoff.duration()).toBe(100);
    expect(backoff.duration()).toBe(200);
    expect(backoff.attempts).toBe(2);
    backoff.reset();
    expect(backoff.attempts).toBe(0);
    expect(backoff.duration()).toBe(100);
  });
});
