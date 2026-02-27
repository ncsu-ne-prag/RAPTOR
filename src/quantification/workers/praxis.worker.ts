import { parentPort, workerData } from 'node:worker_threads';
import { existsSync } from 'fs';
import * as path from 'path';
import type { PraxisQuantRequest } from '../../common/types/praxis-quantify-request';

interface PraxisWorkerData {
  quantRequest: Omit<PraxisQuantRequest, '_id'>;
}

const data = workerData as PraxisWorkerData;

const addonPath = (() => {
  const cwd = process.cwd();
  const repoRootFromDist = path.resolve(__dirname, '../../../../../');
  const candidates = [
    // When PRAXIS is checked out at RAPTOR repo root.
    path.join(cwd, 'target', 'release', 'praxis.node'),
    path.join(cwd, 'target', 'debug', 'praxis.node'),

    // When PRAXIS is vendored under RAPTOR/praxis.
    path.join(cwd, 'praxis', 'target', 'release', 'praxis.node'),
    path.join(cwd, 'praxis', 'target', 'debug', 'praxis.node'),

    // When running from a nested service directory.
    path.join(cwd, '..', 'target', 'release', 'praxis.node'),
    path.join(cwd, '..', 'target', 'debug', 'praxis.node'),

    path.join(cwd, '..', 'praxis', 'target', 'release', 'praxis.node'),
    path.join(cwd, '..', 'praxis', 'target', 'debug', 'praxis.node'),

    // Relative to this file (dist/runtime layouts).
    path.join(repoRootFromDist, 'target', 'release', 'praxis.node'),
    path.join(repoRootFromDist, 'target', 'debug', 'praxis.node'),
    path.join(repoRootFromDist, 'praxis', 'target', 'release', 'praxis.node'),
    path.join(repoRootFromDist, 'praxis', 'target', 'debug', 'praxis.node'),
  ];

  for (const candidate of candidates) {
    if (existsSync(candidate)) {
      return candidate;
    }
  }

  throw new Error(
    'Unable to locate praxis.node. Build it with `cargo build --features napi-rs` (and `cuda` if needed).',
  );
})();

// eslint-disable-next-line @typescript-eslint/no-var-requires
const addon = require(addonPath);

(async () => {
  try {
    const modelJson = JSON.stringify(data.quantRequest?.model ?? {});
    const settingsJson = JSON.stringify(data.quantRequest?.settings ?? {});

    const quantifyFn =
      addon.quantifyOpenpraJsonWithSettings ??
      addon.quantify_openpra_json_with_settings;
    if (typeof quantifyFn !== 'function') {
      throw new Error(
        'praxis.node is missing quantifyOpenpraJsonWithSettings export (expected from napi-rs bindings)',
      );
    }

    const rendered: string = await Promise.resolve(
      quantifyFn(modelJson, settingsJson),
    );

    const result = JSON.parse(rendered);
    parentPort?.postMessage({ result });
  } catch (err) {
    const error = err instanceof Error ? err : new Error(String(err));
    parentPort?.postMessage({
      error: error.message,
      stack: error.stack,
    });
  }
})();
