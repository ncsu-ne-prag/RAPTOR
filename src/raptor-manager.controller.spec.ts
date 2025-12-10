import { Test, TestingModule } from '@nestjs/testing';
import { RaptorManagerController } from './raptor-manager.controller';
import { RaptorManagerService } from './raptor-manager.service';
import { NotFoundException } from '@nestjs/common';

vi.mock('@nestia/core', () => ({
  TypedRoute: {
    Get: () => () => {},
    Post: () => () => {},
  },
  TypedQuery: () => () => {},
  TypedParam: () => () => {},
  TypedBody: () => () => {},
}));

describe('RaptorManagerController', () => {
  let controller: RaptorManagerController;

  const mockService = {
    getJobTypes: vi.fn(),
    getProcessingJobs: vi.fn(),
    getRunningJobs: vi.fn(),
    getCompletedJobs: vi.fn(),
    getPartialJobs: vi.fn(),
    getFailedJobs: vi.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [RaptorManagerController],
      providers: [
        {
          provide: RaptorManagerService,
          useValue: mockService,
        },
      ],
    }).compile();

    controller = module.get<RaptorManagerController>(RaptorManagerController);
  });

  it('should be defined', () => {
    expect(controller).toBeDefined();
  });

  describe('getJobTypes', () => {
    it('should return job types', () => {
      const result = { services: [{ name: 'Test', endpoint: '/test' }] };
      mockService.getJobTypes.mockReturnValue(result);
      expect(controller.getJobTypes()).toBe(result);
    });

    it('should throw NotFoundException on error', () => {
      mockService.getJobTypes.mockImplementation(() => {
        throw new Error();
      });
      expect(() => controller.getJobTypes()).toThrow(NotFoundException);
    });
  });

  describe('getProcessingJobs', () => {
    it('should return processing jobs', async () => {
      const result = { jobs: [] };
      mockService.getProcessingJobs.mockResolvedValue(result);
      expect(await controller.getProcessingJobs()).toBe(result);
    });

    it('should throw NotFoundException on error', async () => {
      mockService.getProcessingJobs.mockRejectedValue(new Error());
      await expect(controller.getProcessingJobs()).rejects.toThrow(
        NotFoundException,
      );
    });
  });

  describe('getRunningJobs', () => {
    it('should return running jobs', async () => {
      const result = { jobs: [] };
      mockService.getRunningJobs.mockResolvedValue(result);
      expect(await controller.getRunningJobs()).toBe(result);
    });

    it('should throw NotFoundException on error', async () => {
      mockService.getRunningJobs.mockRejectedValue(new Error());
      await expect(controller.getRunningJobs()).rejects.toThrow(
        NotFoundException,
      );
    });
  });

  describe('getCompletedJobs', () => {
    it('should return completed jobs', async () => {
      const result = { jobs: [] };
      mockService.getCompletedJobs.mockResolvedValue(result);
      expect(await controller.getCompletedJobs()).toBe(result);
    });

    it('should throw NotFoundException on error', async () => {
      mockService.getCompletedJobs.mockRejectedValue(new Error());
      await expect(controller.getCompletedJobs()).rejects.toThrow(
        NotFoundException,
      );
    });
  });

  describe('getPartialJobs', () => {
    it('should return partial jobs', async () => {
      const result = { jobs: [] };
      mockService.getPartialJobs.mockResolvedValue(result);
      expect(await controller.getPartialJobs()).toBe(result);
    });

    it('should throw NotFoundException on error', async () => {
      mockService.getPartialJobs.mockRejectedValue(new Error());
      await expect(controller.getPartialJobs()).rejects.toThrow(
        NotFoundException,
      );
    });
  });

  describe('getFailedJobs', () => {
    it('should return failed jobs', async () => {
      const result = { jobs: [] };
      mockService.getFailedJobs.mockResolvedValue(result);
      expect(await controller.getFailedJobs()).toBe(result);
    });

    it('should throw NotFoundException on error', async () => {
      mockService.getFailedJobs.mockRejectedValue(new Error());
      await expect(controller.getFailedJobs()).rejects.toThrow(
        NotFoundException,
      );
    });
  });
});
