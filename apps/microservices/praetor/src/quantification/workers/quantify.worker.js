'use strict';

// eslint-disable-next-line @typescript-eslint/no-var-requires
const { parentPort, workerData } = require('node:worker_threads');
// eslint-disable-next-line @typescript-eslint/no-var-requires
const { QuantifyModel } = require('scram-node');

(async () => {
  try {
    const { quantRequest } = workerData ?? {};
    const result = await Promise.resolve(
      QuantifyModel(quantRequest?.settings, quantRequest?.model),
    );
    parentPort?.postMessage({ result });
  } catch (err) {
    const error = err instanceof Error ? err : new Error(String(err));
    parentPort?.postMessage({
      error: error.message,
      stack: error.stack,
    });
  }
})();
