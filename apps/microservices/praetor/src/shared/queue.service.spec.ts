import { Test, TestingModule } from '@nestjs/testing';
import { QueueService } from './queue.service';
import { RpcException } from '@nestjs/microservices';

describe('QueueService', () => {
  let service: QueueService;

  const mockChannel = {
    assertExchange: vi.fn(),
    assertQueue: vi.fn(),
    bindQueue: vi.fn(),
    prefetch: vi.fn(),
  };

  const mockQueueConfig = {
    name: 'test-queue',
    durable: true,
    messageTtl: 1000,
    maxLength: 100,
    prefetch: 10,
    exchange: {
      name: 'test-exchange',
      type: 'topic',
      durable: true,
      bindingKey: 'key',
      routingKey: 'key',
    },
    deadLetter: {
      name: 'dlq',
      durable: true,
      exchange: {
        name: 'dlx',
        type: 'topic',
        durable: true,
        bindingKey: 'dlk',
        routingKey: 'dlk',
      },
    },
  };

  beforeEach(async () => {
    vi.clearAllMocks();
    const module: TestingModule = await Test.createTestingModule({
      providers: [QueueService],
    }).compile();

    service = module.get<QueueService>(QueueService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('setupQueue', () => {
    it('should setup queue and dead letter queue successfully', async () => {
      await service.setupQueue(mockQueueConfig as any, mockChannel as any);

      // Verify Dead Letter Setup
      expect(mockChannel.assertExchange).toHaveBeenCalledWith('dlx', 'topic', {
        durable: true,
      });
      expect(mockChannel.assertQueue).toHaveBeenCalledWith('dlq', {
        durable: true,
      });
      expect(mockChannel.bindQueue).toHaveBeenCalledWith('dlq', 'dlx', 'dlk');

      // Verify Main Queue Setup
      expect(mockChannel.assertExchange).toHaveBeenCalledWith(
        'test-exchange',
        'topic',
        { durable: true },
      );
      expect(mockChannel.assertQueue).toHaveBeenCalledWith(
        'test-queue',
        expect.objectContaining({
          durable: true,
          messageTtl: 1000,
          deadLetterExchange: 'dlx',
          deadLetterRoutingKey: 'dlk',
          maxLength: 100,
        }),
      );
      expect(mockChannel.prefetch).toHaveBeenCalledWith(10);
      expect(mockChannel.bindQueue).toHaveBeenCalledWith(
        'test-queue',
        'test-exchange',
        'key',
      );
    });

    it('should throw RpcException if exchange assertion fails', async () => {
      mockChannel.assertExchange.mockRejectedValueOnce(new Error('Failed'));
      // First call is for DLX, let's make the second one fail (main exchange)
      mockChannel.assertExchange.mockResolvedValueOnce(undefined);
      mockChannel.assertExchange.mockRejectedValueOnce(new Error('Failed'));

      await expect(
        service.setupQueue(mockQueueConfig as any, mockChannel as any),
      ).rejects.toThrow(RpcException);
    });

    it('should throw RpcException if queue assertion fails', async () => {
      mockChannel.assertQueue.mockRejectedValueOnce(new Error('Failed'));
      // First call is for DLQ, let's make the second one fail (main queue)
      mockChannel.assertQueue.mockResolvedValueOnce(undefined);
      mockChannel.assertQueue.mockRejectedValueOnce(new Error('Failed'));

      await expect(
        service.setupQueue(mockQueueConfig as any, mockChannel as any),
      ).rejects.toThrow(RpcException);
    });

    it('should throw RpcException if binding fails', async () => {
      mockChannel.bindQueue.mockRejectedValueOnce(new Error('Failed'));
      // First call is for DLQ binding, let's make the second one fail (main binding)
      mockChannel.bindQueue.mockResolvedValueOnce(undefined);
      mockChannel.bindQueue.mockRejectedValueOnce(new Error('Failed'));

      await expect(
        service.setupQueue(mockQueueConfig as any, mockChannel as any),
      ).rejects.toThrow(RpcException);
    });
  });
});
