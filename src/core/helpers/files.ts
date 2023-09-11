import axios, { AxiosRequestConfig, AxiosResponse } from "axios";
import merge from "lodash.merge";
import { createDeferred, Deferred } from "./promise";

type ProgressFunc = (progress: number) => void;
type BeforeFileUploadFunc<T extends File = File> = (
  file: T,
) => Promise<AxiosRequestConfig | void>;

type JobOptions<T extends File> = {
  files: T[];
  axiosConfig?: AxiosRequestConfig;
  onBeforeFileUpload?: BeforeFileUploadFunc<T>;
  onAfterFileUpload?: (file: T) => void;
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
  private onBeforeFileUpload: BeforeFileUploadFunc<T> | undefined;
  private onAfterFileUpload:
    | undefined
    | ((file: T, response: AxiosResponse) => void);
  private onProgress?: ProgressFunc;
  private _axiosConfig: AxiosRequestConfig;
  private _runs: number = 0;
  private _status: "pending" | "running" | "done" | "error";
  private _error: undefined | Error;

  public get progress() {
    const total = this._files.reduce((acc, file) => acc + file.size, 0);
    const loaded = this._files.reduce(
      (acc, file) => acc + (file.loaded || 0),
      0,
    );
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

  constructor({
    files,
    axiosConfig,
    onBeforeFileUpload,
    onAfterFileUpload,
    onProgress,
  }: JobOptions<T>) {
    this._files = files;
    this._axiosConfig = axiosConfig ?? {};
    this.onBeforeFileUpload = onBeforeFileUpload;
    this.onAfterFileUpload = onAfterFileUpload;
    this.onProgress = onProgress;
    this._status = "pending";
  }

  async run(): Promise<any> {
    this._runs++;
    this._status = "running";

    for (const file of this._files) {
      if (file.isUploaded) continue; // In case of retry, do not upload again the files that were already uploaded

      console.log(`Uploading "${file.name}"`);

      // Get Axios request options
      const extraOptions = this.onBeforeFileUpload
        ? (await this.onBeforeFileUpload(file)) || {}
        : {};
      const options = merge(this._axiosConfig, extraOptions);

      console.log(`Start upload of "${file.name}"`, options);
      try {
        const response = await axios.request({
          data: file,
          ...options,
          onUploadProgress: (progressEvent) => {
            if (!progressEvent.estimated) {
              return;
            }

            file.loaded = progressEvent.loaded;
            if (this.onProgress) {
              try {
                this.onProgress(this.progress);
              } catch (err) {
                console.error("Error in provided onProgress function.", err);
              }
            }
          },
        });
        console.log(
          `Upload of "${file.name}" completed.`,
          response.status,
          response.data,
        );
        if (this.onAfterFileUpload) {
          await this.onAfterFileUpload(file, response);
        }
        file.isUploaded = true;
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
      axiosConfig: {
        url: "//my-upload.url", // It can also be provided using `onBeforeFileUpload`
        method: "POST"
      },
      onBeforeFileUpload: () => {} // Return a AxiosRequestConfig that will be merged with the above config
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
        console.log("onJobSuccess", job);
        this.removeRunningJob(job);
        deferred.resolve(result);
        this.process();
      },
      (err) => {
        console.log("onJobFailure", job, err);
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

export const uploader = new UploadManager();
