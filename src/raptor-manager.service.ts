import { Injectable } from '@nestjs/common';
import { JobResponse } from './raptor-manager.controller';
import { StorageService } from './quantification/services/storage.service';
import { JobMetadata } from './shared/minio.service';

@Injectable()
export class RaptorManagerService {
  constructor(private readonly storageService: StorageService) {}
  /**
   * Retrieves the types of jobs available.
   *
   * @returns An object containing a message describing the types of jobs.
   */
  public getJobTypes(): JobResponse {
    return { message: 'return the types of jobs' };
  }

  /**
   * Retrieves the list of pending jobs.
   *
   * @returns An object containing a message describing the pending jobs.
   */
  public async getJobs(status: string): Promise<{ jobs: JobMetadata[] }> {
    const allJobs = await this.storageService.getQuantifiedReports();
    const filteredJobs = allJobs.filter((job) => job.status === status);

    return {
      jobs: filteredJobs,
    };
  }

  /**
   * Retrieves the list of pending jobs.
   *
   * @returns An object containing a message describing the pending jobs.
   */
  public async getPendingJobs(): Promise<{ jobs: JobMetadata[] }> {
    return this.getJobs('pending');
  }

  public async getRunningJobs(): Promise<{ jobs: JobMetadata[] }> {
    return this.getJobs('running');
  }

  public async getCompletedJobs(): Promise<{ jobs: JobMetadata[] }> {
    return this.getJobs('completed');
  }

  /**
   * Creates a new job.
   *
   * @returns An object containing a message confirming the creation of a new job.
   */
  public createJob(): JobResponse {
    return { message: 'create a new job' };
  }
}
