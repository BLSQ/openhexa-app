export type BackoffOptions = {
  min: number;
  max: number;
  factor: number;
  jitter: number;
};

class Backoff {
  private _attempts: number;
  private _base: number;
  private _max: number;
  private _factor: number;
  private _jitter: number;

  constructor(options: BackoffOptions) {
    this._base = options.min || 100;
    this._max = options.max || 10000;
    this._factor = options.factor || 2;
    this._jitter =
      options.jitter > 0 && options.jitter < 1 ? options.jitter : 0;
    this._attempts = 0;
  }

  get attempts(): number {
    return this._attempts;
  }

  duration() {
    let duration = this._base * Math.pow(this._factor, this._attempts++);
    if (this._jitter) {
      var rand = Math.random();
      var deviation = Math.floor(rand * this._jitter * duration);
      duration =
        (Math.floor(rand * 10) & 1) == 0
          ? duration - deviation
          : duration + deviation;
    }
    return Math.min(duration, this._max) | 0;
  }

  reset() {
    this._attempts = 0;
  }
}

export default Backoff;
