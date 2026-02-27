'use strict';

// eslint-disable-next-line @typescript-eslint/no-var-requires
const { parentPort, workerData } = require('node:worker_threads');
// eslint-disable-next-line @typescript-eslint/no-var-requires
const { existsSync } = require('fs');
// eslint-disable-next-line @typescript-eslint/no-var-requires
const { join, resolve } = require('path');

const addonPath = (() => {
  const cwd = process.cwd();
  const candidates = [
    // When PRAXIS is checked out at RAPTOR repo root.
    join(cwd, 'target', 'release', 'praxis.node'),
    join(cwd, 'target', 'debug', 'praxis.node'),

    // When running from dist/ (nest build output) with repo-root cwd.
    join(cwd, '..', 'target', 'release', 'praxis.node'),
    join(cwd, '..', 'target', 'debug', 'praxis.node'),

    // Relative to this file (dist/runtime layouts).
    resolve(__dirname, '../../../../target/release/praxis.node'),
    resolve(__dirname, '../../../../target/debug/praxis.node'),
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
    const { quantRequest } = workerData ?? {};

    const modelJson = JSON.stringify(quantRequest?.model ?? {});
    const settingsJson = JSON.stringify(quantRequest?.settings ?? {});

    const rendered = await Promise.resolve(
      addon.quantify_openpra_json_with_settings(modelJson, settingsJson),
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
