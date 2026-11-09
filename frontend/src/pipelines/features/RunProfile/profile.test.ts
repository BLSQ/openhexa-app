import {
  buildTimeline,
  formatSeconds,
  getLaneDuration,
  getFrameColor,
  getFunctionName,
  getSlowestLines,
  Profile,
} from "./profile";

const profile: Profile = {
  duration: 12,
  frames: [
    "main (pipeline.py:1)",
    "compute (pipeline.py:10)",
    "wait (pipeline.py:30)",
  ],
  lanes: [
    {
      name: "Main process",
      nodes: [[0, 0, 12_000, [[1, 1_000, 7_000, []]]]],
    },
  ],
  files: {},
};

describe("buildTimeline", () => {
  it("shows durations and converts times to seconds", () => {
    expect(buildTimeline(profile, profile.lanes[0].nodes)).toEqual([
      {
        name: "main · {{value}}s",
        frame: "main (pipeline.py:1)",
        start: 0,
        duration: 12,
        color: getFrameColor("main (pipeline.py:1)"),
        children: [
          {
            name: "compute · {{value}}s",
            frame: "compute (pipeline.py:10)",
            start: 1,
            duration: 6,
            color: getFrameColor("compute (pipeline.py:10)"),
            children: [],
          },
        ],
      },
    ]);
  });
});

describe("getLaneDuration", () => {
  it("leaves out the import of the pipeline", () => {
    expect(
      getLaneDuration(
        {
          ...profile,
          frames: ["<module> (pipeline.py:1)", "compute (pipeline.py:10)"],
        },
        [
          [0, 0, 500, []],
          [1, 500, 2_000, []],
          [1, 3_000, 4_000, []],
        ],
      ),
    ).toEqual(2.5);
  });
});

describe("getFunctionName", () => {
  it("drops the file and line", () => {
    expect(getFunctionName("compute (pipeline.py:26)")).toEqual("compute");
    expect(getFunctionName("<module>")).toEqual("<module>");
  });
});

describe("getFrameColor", () => {
  it("depends on the function only", () => {
    expect(getFrameColor("compute (pipeline.py:26)")).toEqual(
      getFrameColor("compute (other.py:3)"),
    );
  });
});

describe("formatSeconds", () => {
  it("formats less than a second in milliseconds", () => {
    expect(formatSeconds(0.37)).toEqual("{{value}}ms");
  });

  it("formats longer times as a duration", () => {
    expect(formatSeconds(123.4)).toEqual("{{value}}m {{value}}s");
  });
});

describe("getSlowestLines", () => {
  it("sorts the lines of all files, slowest first", () => {
    expect(
      getSlowestLines(
        {
          ...profile,
          files: {
            "pipeline.py": [
              [3, 100],
              [10, 900],
            ],
            "lib/tasks.py": [[5, 400]],
          },
        },
        2,
      ),
    ).toEqual([
      { path: "pipeline.py", line: 10, milliseconds: 900 },
      { path: "lib/tasks.py", line: 5, milliseconds: 400 },
    ]);
  });
});
