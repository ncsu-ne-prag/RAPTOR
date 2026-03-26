import {
  Controller,
  Query,
  InternalServerErrorException,
  NotFoundException,
} from '@nestjs/common';
import { TypedRoute } from '@nestia/core';
import { PraetorManagerService } from './praetor-manager.service';
import { JobMetadata } from './shared/minio.service';

export interface JobResponse {
  message: string;
}

@Controller()
export class PraetorManagerController {
  /**
   * Constructs the PraetorManagerController with the necessary service.
   * @param praetorManagerService - The service to handle job broker operations.
   */
  constructor(private readonly praetorManagerService: PraetorManagerService) {}

  /**
   * Retrieves a list of job types.
   *
   * @returns An object containing a message with the list of job types.
   * @throws {@link NotFoundException} When the list of job types cannot be found.
   */
  @TypedRoute.Get('/job-types')
  public getJobTypes(): JobResponse {
    try {
      return this.praetorManagerService.getJobTypes();
    } catch {
      throw new NotFoundException(
        'Server was unable to find the requested list of job types.',
      );
    }
  }

  /**
   * Retrieves a list of jobs based on the status.
   *
   * @returns An object containing a message with the list of pending jobs.
   * @throws {@link NotFoundException} When the list of pending jobs cannot be found.
   */
  @TypedRoute.Get('/jobs')
  public async getJobs(
    @Query('status') status: string,
  ): Promise<{ jobs: JobMetadata[] }> {
    try {
      return await this.praetorManagerService.getJobs(status);
    } catch {
      throw new NotFoundException(
        'Server was unable to find the requested list of pending jobs.',
      );
    }
  }

  /**
   * Retrieves a list of pending jobs.
   *
   * @returns An object containing a message with the list of pending jobs.
   * @throws {@link NotFoundException} When the list of pending jobs cannot be found.
   */
  @TypedRoute.Get('/pending-jobs')
  public async getPendingJobs(): Promise<{ jobs: JobMetadata[] }> {
    try {
      return await this.praetorManagerService.getPendingJobs();
    } catch {
      throw new NotFoundException(
        'Server was unable to find the requested list of pending jobs.',
      );
    }
  }

  @TypedRoute.Get('/running-jobs')
  public async getRunningJobs(): Promise<{ jobs: JobMetadata[] }> {
    try {
      return await this.praetorManagerService.getRunningJobs();
    } catch {
      throw new NotFoundException(
        'Server was unable to find the requested list of running jobs.',
      );
    }
  }

  @TypedRoute.Get('/completed-jobs')
  public async getCompletedJobs(): Promise<{ jobs: JobMetadata[] }> {
    try {
      return await this.praetorManagerService.getCompletedJobs();
    } catch {
      throw new NotFoundException(
        'Server was unable to find the requested list of completed jobs.',
      );
    }
  }

  /**
   * Creates a new job.
   *
   * @returns An object containing a message confirming the job creation.
   * @throws {@link InternalServerErrorException} When there is a problem creating the job.
   */
  @TypedRoute.Post('/create-job')
  public createJob(): JobResponse {
    try {
      return this.praetorManagerService.createJob();
    } catch {
      throw new InternalServerErrorException(
        'Server encountered a problem while creating a job.',
      );
    }
  }
}
