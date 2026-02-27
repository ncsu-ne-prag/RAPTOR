import {
  Controller,
  InternalServerErrorException,
  NotFoundException,
} from '@nestjs/common';
import { TypedBody, TypedParam, TypedRoute } from '@nestia/core';
import type { PraxisQuantRequest } from '../../common/types/praxis-quantify-request';
import {
  JobOutputResponse,
  JobStatusIds,
  StorageService,
} from '../services/storage.service';
import type { JobMetadata } from '../../shared/minio.service';
import { PraxisProducerService } from '../services/praxis-producer.service';

@Controller()
export class PraxisController {
  constructor(
    private readonly producerService: PraxisProducerService,
    private readonly storageService: StorageService,
  ) {}

  @TypedRoute.Post('/praxis')
  public async createAndQueuePraxisQuant(
    @TypedBody() quantRequest: Omit<PraxisQuantRequest, '_id' | 'engine'> & {
      settings?: PraxisQuantRequest['settings'];
      model?: PraxisQuantRequest['model'];
    },
  ): Promise<{ jobId: string }> {
    try {
      const jobId = await this.producerService.createAndQueuePraxisQuant({
        engine: 'praxis',
        settings: quantRequest.settings,
        model: quantRequest.model,
      });
      return { jobId };
    } catch {
      throw new InternalServerErrorException(
        'Server encountered a problem while queueing PRAXIS quantification job.',
      );
    }
  }

  @TypedRoute.Get('/praxis')
  public async getPraxisReports(): Promise<JobMetadata[]> {
    try {
      const all = await this.storageService.getQuantifiedReports();
      return all.filter((m) => m.tool === 'praxis');
    } catch {
      throw new NotFoundException(
        'Server was unable to find the requested list of PRAXIS reports.',
      );
    }
  }

  @TypedRoute.Get('/praxis/:jobId')
  public async getJobStatus(
    @TypedParam('jobId') jobId: string,
  ): Promise<JobStatusIds> {
    try {
      return await this.storageService.getJobStatus(jobId);
    } catch {
      throw new NotFoundException(`Job with ID ${jobId} not found.`);
    }
  }

  @TypedRoute.Get('/praxis/input/:inputId')
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

  @TypedRoute.Get('/praxis/output/:jobId')
  public async getOutput(
    @TypedParam('jobId') jobId: string,
  ): Promise<JobOutputResponse> {
    try {
      return await this.storageService.getAggregatedJobOutput(jobId);
    } catch {
      throw new NotFoundException(`Job with ID ${jobId} not found.`);
    }
  }
}
