import { Worker } from 'node:worker_threads';
import { existsSync } from 'fs';
import { join } from 'path';
import type { PraxisQuantRequest } from '../../common/types/praxis-quantify-request';

interface PraxisWorkerMessage {
  result?: unknown;
  error?: string;
  stack?: string;
}

const workerPath = (() => {
  const candidates = [
    join(__dirname, 'praxis.worker.js'),
    join(__dirname, 'workers', 'praxis.worker.js'),
    join(__dirname, 'quantification', 'workers', 'praxis.worker.js'),
    join(process.cwd(), 'quantification', 'workers', 'praxis.worker.js'),
  ];

  for (const candidate of candidates) {
    if (existsSync(candidate)) {
      return candidate;
    }
  }

  throw new Error('Unable to locate praxis.worker.js for PRAXIS quantification.');
})();

export function runPraxisQuantificationWithWorker(
  quantRequest: Omit<PraxisQuantRequest, '_id'>,
): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const worker = new Worker(workerPath, {
      workerData: { quantRequest },
    });

    let settled = false;

    const finalize = () => {
      settled = true;
      worker.removeAllListeners();
    };

    const terminateSafely = async () => {
      try {
        await worker.terminate();
      } catch {
        // ignore
      }
    };

    worker.once('message', async (message: PraxisWorkerMessage) => {
      if (settled) return;

      finalize();

      if (message?.error) {
        const err = new Error(message.error);
        if (message.stack) err.stack = message.stack;
        await terminateSafely();
        reject(err);
        return;
      }

      await terminateSafely();
      if (!('result' in (message ?? {}))) {
        reject(new Error('PRAXIS quantification worker returned no result.'));
        return;
      }
      resolve(message.result);
    });

    worker.once('error', async (error: unknown) => {
      if (settled) return;

      finalize();
      await terminateSafely();
      reject(error);
    });

    worker.once('exit', (code: number) => {
      if (settled) return;

      finalize();
      if (code === 0) {
        reject(
          new Error('PRAXIS quantification worker exited before returning a result.'),
        );
      } else {
        reject(new Error(`PRAXIS quantification worker exited with code ${code}`));
      }
    });
  });
}
