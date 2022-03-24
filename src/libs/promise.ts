import assert from "assert";

export type Deferred = {
  resolve: (value: unknown) => void;
  reject: (reason?: any) => void;
  promise: Promise<any>;
};

export function createDeferred(): Deferred {
  let re;
  let rj;

  const promise = new Promise((resolve, reject) => {
    re = resolve;
    rj = reject;
  });

  assert(re && rj);

  return {
    resolve: re,
    reject: rj,
    promise,
  };
}
