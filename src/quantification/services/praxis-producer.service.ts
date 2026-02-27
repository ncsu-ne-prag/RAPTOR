import {
  Injectable,
  Logger,
  OnApplicationBootstrap,
  OnApplicationShutdown,
} from '@nestjs/common';
import { Channel, ChannelModel } from 'amqplib';
import typia from 'typia';
import { v4 as uuidv4 } from 'uuid';
import { RpcException } from '@nestjs/microservices';
import {
  MinioService,
  QueueConfig,
  QueueConfigFactory,
  QueueService,
  RabbitMQChannelModelService,
} from '../../shared';
import type { PraxisQuantRequest } from '../../common/types/praxis-quantify-request';

@Injectable()
export class PraxisProducerService
  implements OnApplicationBootstrap, OnApplicationShutdown
{
  private readonly logger = new Logger(PraxisProducerService.name);
  private readonly quantQueueConfig: QueueConfig;
  private channelModel: ChannelModel | null = null;
  private channel: Channel | null = null;

  constructor(
    private readonly queueService: QueueService,
    private readonly rabbitmqService: RabbitMQChannelModelService,
    private readonly queueConfigFactory: QueueConfigFactory,
    private readonly minioService: MinioService,
  ) {
    this.quantQueueConfig = this.queueConfigFactory.createQuantJobQueueConfig();
  }

  async onApplicationBootstrap(): Promise<void> {
    this.logger.debug('Connecting to the broker');
    this.channelModel = await this.rabbitmqService.getChannelModel(
      PraxisProducerService.name,
    );
    this.channel = await this.rabbitmqService.getChannel(
      this.channelModel,
      PraxisProducerService.name,
    );
    await this.queueService.setupQueue(this.quantQueueConfig, this.channel);
    this.logger.debug('Initialized quant queue and ready to send PRAXIS jobs');
  }

  public async createAndQueuePraxisQuant(
    quantRequest: PraxisQuantRequest,
  ): Promise<string> {
    const jobId = uuidv4();
    quantRequest._id = jobId;

    const inputId = await this.minioService.storeInputData(quantRequest);

    const sentAt = Date.now();
    await this.minioService.createJobMetadata(jobId, inputId, {
      sentAt,
      tool: 'praxis',
    });

    const modelsData = ((): string => {
      try {
        return typia.json.assertStringify<PraxisQuantRequest>(quantRequest);
      } catch {
        throw new RpcException(`Invalid schema: JobID <${jobId}>`);
      }
    })();

    try {
      this.logger.debug('Queueing PRAXIS quantification job');
      await this.channel?.checkExchange(this.quantQueueConfig.exchange.name);
      this.channel?.publish(
        this.quantQueueConfig.exchange.name,
        this.quantQueueConfig.exchange.routingKey,
        Buffer.from(modelsData),
        { persistent: true },
      );
    } catch {
      throw new RpcException(
        `${this.quantQueueConfig.exchange.name} does not exist.`,
      );
    }

    return jobId;
  }

  async onApplicationShutdown(): Promise<void> {
    try {
      await this.channel?.close();
      await this.channelModel?.close();
    } catch {
      throw new RpcException(
        `${PraxisProducerService.name} failed to stop RabbitMQ services.`,
      );
    }
  }
}
