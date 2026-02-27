export interface PraxisNodeOptions {
  /** Resolve mode. If true, strict; otherwise compatible. */
  strict?: boolean;

  /** Execution backend. Defaults to 'cpu'. */
  backend?: 'cpu' | 'cuda';

  /** MC seed (u64). */
  seed?: number;

  /** Monte Carlo layout params. Defaults match Checkpoint 1 parity config. */
  iterations?: number;
  batches?: number;
  bitpacksPerBatch?: number;
  omega?: number;

  /** Whether to show watch/progress output (if supported by backend). */
  watch?: boolean;
}

/**
 * PRAXIS quantification request envelope.
 *
 * `model` must be OpenPRA MEF JSON (object form) and will be stringified for the addon.
 */
export interface PraxisQuantRequest {
  _id?: string;
  engine: 'praxis';
  settings?: PraxisNodeOptions;
  model?: unknown;
}
