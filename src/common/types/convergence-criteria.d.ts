/**
 * Convergence criteria for adaptive ZBDD quantification
 */
export interface ConvergenceCriteria {
  /**
   * Relative error tolerance (0-1)
   */
  relativeErrorTolerance?: number;

  /**
   * Minimum truncation (cut-off) probability to evaluate
   */
  minCutOff?: number;

  /**
   * Maximum truncation (cut-off) probability to evaluate
   */
  maxCutOff?: number;

  /**
   * Threshold for consecutive result variation (0-1)
   * Stop if improvement is less than this threshold
   */
  consecutiveVariationThreshold?: number;

  /**
   * Method to obtain the initial point estimate
   */
  initialEstimator?: 'monteCarlo' | 'bdd';
}
