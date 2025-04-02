import { createDeferred, Deferred } from "./promise";

type XHROptions = {
  url: string;
  method: "POST" | "PUT" | "PATCH";
  headers: Record<string, string>;
};

type ProgressFunc = (progress: number) => void;
type GetXHROptionsFunc<T extends File = File> = (
  file: T,
) => Promise<XHROptions>;

type JobOptions<T extends File> = {
  files: T[];
  getXHROptions: GetXHROptionsFunc<T>;
  onProgress?: ProgressFunc;
};
type JobItem<T extends File> = {
  job: Job<T>;
  deferred: Deferred;
};

/*
  A Job represents the upload of a set of files.
*/

export interface JobFile extends File {
  loaded?: number;
  isUploaded?: boolean;
}

class Job<T extends JobFile = JobFile> {
  private _files: T[];
  private getXHROptions: GetXHROptionsFunc<T>;
  private _onProgress?: ProgressFunc;
  private _runs: number = 0;
  private _status: "pending" | "running" | "done" | "error";
  private _error: undefined | Error;

  constructor({ files, getXHROptions, onProgress }: JobOptions<T>) {
    this._files = files;
    this.getXHROptions = getXHROptions;
    this._onProgress = onProgress;
    this._status = "pending";
  }

  public get progress() {
    let total = 0;
    let loaded = 0;
    for (const file of this._files) {
      if (file.isUploaded) {
        loaded += file.size;
      }
      total += file.size;
    }
    return Math.round((loaded * 100) / (total || 1));
  }

  public get runs() {
    return this._runs;
  }

  public get status() {
    return this._status;
  }

  public get error() {
    return this._error;
  }

  onProgress() {
    if (this._onProgress) {
      try {
        this._onProgress(this.progress);
      } catch (err) {
        console.error("Error in provided onProgress function.", err);
      }
    }
  }

  async run(): Promise<any> {
    this._runs++;
    this._status = "running";

    for (const file of this._files) {
      if (file.isUploaded) continue; // In case of retry, do not upload again the files that were already uploaded

      console.log(`Uploading "${file.name}"`);

      // Get Axios request options
      const options = await this.getXHROptions(file);

      console.log(`Start upload of "${file.name}"`, options);
      try {
        const xhr = new XMLHttpRequest();
        const success = await new Promise((resolve) => {
          // Add event listeners to track the upload progress
          xhr.upload.addEventListener("progress", (event) => {
            if (event.lengthComputable) {
              file.loaded = event.loaded;
              this.onProgress();
            }
          });

          xhr.addEventListener("loadend", () => {
            resolve(
              xhr.readyState === 4 && xhr.status >= 200 && xhr.status < 300,
            );
          });

          xhr.open(options.method, options.url, true);

          for (const key in options.headers) {
            xhr.setRequestHeader(key, options.headers[key]);
          }

          xhr.send(file);
        });
        if (success) {
          console.log(`Upload of "${file.name}" completed.`);
          file.isUploaded = true;
        } else {
          throw new Error(`Upload failed: ${xhr.statusText}`);
        }
      } catch (err: any) {
        this._error = err;
        this._status = "error";
        throw err;
      }
    }

    this._status = "done";

    return;
  }
}

/*
  The UploadManager is the main part of the upload mechanism. It keeps the list of all upload jobs in the app.
  User can create new upload job with: 
  
    manager.createUploadJob({
      files: [],
      getXHROptions: () => {} // Returns the required options to execute the request
    })
  
*/
class UploadManager<T extends JobFile = JobFile> {
  pendingJobs: JobItem<T>[];
  runningJobs: JobItem<T>[];
  maxConcurrentJobs: number;

  constructor(maxConcurrentJobs: number = 2) {
    this.maxConcurrentJobs = maxConcurrentJobs;
    this.pendingJobs = [];
    this.runningJobs = [];
  }

  removeRunningJob(job: Job<T>) {
    this.runningJobs = this.runningJobs.filter((item) => item.job !== job);
  }

  process() {
    if (this.runningJobs.length >= this.maxConcurrentJobs) {
      // We already run the maximum jobs concurrently
      return;
    }

    // Try to get the first pending job of the list
    const next = this.pendingJobs.shift();
    if (!next) {
      return;
    }
    this.runningJobs.push(next);
    const { job, deferred } = next;

    job.run().then(
      (result) => {
        this.removeRunningJob(job);
        deferred.resolve(result);
        this.process();
      },
      (err) => {
        console.error("onJobFailure", job, err);
        this.removeRunningJob(job);
        if (job.runs >= 3) {
          err.job = job;
          deferred.reject(err);
        } else {
          setTimeout(
            () => {
              this.pendingJobs.push(next);
              this.process();
            },
            2 ^ (job.runs + 1),
          );
        }
        this.process();
      },
    );
  }

  createUploadJob(options: JobOptions<T>) {
    const job = new Job<T>(options);
    const deferred = createDeferred();

    this.pendingJobs.push({ job, deferred });
    this.process();

    return deferred.promise;
  }
}

export const uploader = new UploadManager(
  parseInt(process.env.MAX_CONCURRENT_UPLOADS ?? "10", 10),
);
