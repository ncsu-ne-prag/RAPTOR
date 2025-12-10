import {
  Controller,
  InternalServerErrorException,
  NotFoundException,
} from '@nestjs/common';
import { ApiTags } from '@nestjs/swagger';
import { TypedRoute, TypedQuery, TypedParam, TypedBody } from '@nestia/core';
import type { NodeQuantRequest } from '../../common/types/quantify-request';
import { ProducerService } from '../services/producer.service';
import {
  StorageService,
  JobStatusIds,
  JobOutputResponse,
} from '../services/storage.service';

@ApiTags('SCRAM Quantification')
@Controller()
export class ScramController {
  constructor(
    private readonly producerService: ProducerService,
    private readonly storageService: StorageService,
  ) {}

  /**
   * @summary Creates and queues a SCRAM quantification job (supports distributed event tree sequences with query parameter distributedSequences=yes)
   */
  @TypedRoute.Post('/scram')
  public async createAndQueueQuant(
    @TypedBody() quantRequest: NodeQuantRequest,
    @TypedQuery() query?: { distributedSequences?: string },
  ): Promise<
    { parentJobId: string; sequenceJobIds: string[] } | { jobId: string }
  > {
    try {
      if (query?.distributedSequences === 'yes') {
        const sequenceJobIds =
          await this.producerService.createAndQueueSequenceBatch(quantRequest);
        const parentJobId = sequenceJobIds[0].split('-').slice(0, -1).join('-');
        return { parentJobId, sequenceJobIds };
      } else {
        const jobId = await this.producerService.createAndQueueQuant(
          quantRequest,
        );
        return { jobId };
      }
    } catch {
      throw new InternalServerErrorException(
        'Server encountered a problem while queueing SCRAM quantification job.',
      );
    }
  }

  /**
   * @summary Creates and queues an adaptive SCRAM quantification job with automatic truncation (supports distributed sequences with query parameter distributedSequences=yes)
   */
  @TypedRoute.Post('/scram/adaptive')
  public async createAndQueueAdaptiveQuant(
    @TypedBody() quantRequest: NodeQuantRequest,
    @TypedQuery() query?: { distributedSequences?: string },
  ): Promise<
    { parentJobId: string; sequenceJobIds: string[] } | { jobId: string }
  > {
    try {
      if (query?.distributedSequences === 'yes') {
        const sequenceJobIds =
          await this.producerService.createAndQueueAdaptiveSequenceBatch(
            quantRequest,
          );
        if (sequenceJobIds.length === 0) {
          throw new InternalServerErrorException(
            'No sequences were extracted for adaptive quantification.',
          );
        }
        const parentJobId = sequenceJobIds[0].split('-').slice(0, -1).join('-');
        return {
          parentJobId,
          sequenceJobIds,
        };
      } else {
        const jobId = await this.producerService.createAndQueueQuant(
          quantRequest,
        );
        return { jobId };
      }
    } catch (error: any) {
      throw new InternalServerErrorException(
        error.message ||
          'Server encountered a problem while queueing adaptive SCRAM quantification job.',
      );
    }
  }

  /**
   * @summary Retrieves all quantified report job IDs
   */
  @TypedRoute.Get('/scram')
  public async getQuantifiedReports(): Promise<string[]> {
    try {
      const jobs = await this.storageService.getQuantifiedReports();
      return jobs.map((job) => job.jobId).filter((id): id is string => !!id);
    } catch {
      throw new NotFoundException(
        'Server was unable to find the requested list of quantified reports.',
      );
    }
  }

  /**
   * @summary Retrieves job status and metadata by job ID
   */
  @TypedRoute.Get('/scram/:jobId')
  public async getJobStatus(
    @TypedParam('jobId') jobId: string,
  ): Promise<JobStatusIds> {
    try {
      return await this.storageService.getJobStatus(jobId);
    } catch {
      throw new NotFoundException(`Job with ID ${jobId} not found.`);
    }
  }

  /**
   * @summary Retrieves the input data (request body) used for a quantification job
   */
  @TypedRoute.Get('/scram/input/:inputId')
  public async getInputData(
    @TypedParam('inputId') inputId: string,
  ): Promise<any> {
    try {
      const inputData = await this.storageService.getInputData(inputId);
      return JSON.parse(inputData);
    } catch {
      throw new NotFoundException(`Input data with ID ${inputId} not found.`);
    }
  }

  /**
   * @summary Retrieves the aggregated output results for a completed job
   */
  @TypedRoute.Get('/scram/output/:jobId')
  public async getAggregatedOutput(
    @TypedParam('jobId') jobId: string,
  ): Promise<JobOutputResponse> {
    try {
      return await this.storageService.getAggregatedJobOutput(jobId);
    } catch {
      throw new NotFoundException(`Job with ID ${jobId} not found.`);
    }
  }

  /**
   * @summary Retrieves performance statistics and timing information for a job (includes child job statistics for distributed jobs)
   */
  @TypedRoute.Get('/scram/stats/:id')
  public async getJobStats(@TypedParam('id') id: string): Promise<{
    sentAt?: number;
    receivedAt?: number;
    stats?: {
      idleTime?: number;
      executionTime?: number;
      startedAt?: number;
      endedAt?: number;
      analysisSeconds?: number;
      probability?: number;
      products?: number;
      // Core adaptive quantification fields (5 essentials)
      originalProducts?: number;
      exactProbability?: number;
      approximateProbability?: number;
      relativeError?: number;
    };
    childStats?: Array<{
      jobId: string;
      sentAt?: number;
      receivedAt?: number;
      stats?: {
        idleTime?: number;
        executionTime?: number;
        startedAt?: number;
        endedAt?: number;
        analysisSeconds?: number;
        probability?: number;
        products?: number;
        // Core adaptive quantification fields (5 essentials)
        originalProducts?: number;
        exactProbability?: number;
        approximateProbability?: number;
        relativeError?: number;
      };
    }>;
  }> {
    try {
      const result = await this.storageService.getJobStats(id);

      // Helper to remove totalSeconds and reportWriteTimeMs from stats
      const cleanStats = (stats: any) => {
        if (!stats) return undefined;

        // Calculate analysisSeconds from totalSeconds if missing
        const analysisSeconds = stats.analysisSeconds ?? stats.totalSeconds;

        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const { totalSeconds, reportWriteTimeMs, ...rest } = stats;
        return { ...rest, analysisSeconds };
      };

      return {
        ...result,
        stats: cleanStats(result.stats),
        childStats: result.childStats?.map((child) => ({
          ...child,
          stats: cleanStats(child.stats),
        })),
      };
    } catch {
      throw new NotFoundException(`Job stats with ID ${id} not found.`);
    }
  }
}
