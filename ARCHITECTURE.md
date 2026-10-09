# System Architecture

The private implementation separates market observation, setup evaluation, order ownership, and reporting. This overview intentionally omits entry thresholds and detailed trading rules.

## Market observation

Historical requests and streaming observations feed a bounded local data layer. It tracks data age and whether candles have completed. Gaps and stream reconnections invalidate dependent observations where required; missing trades are not silently replaced with fabricated candles.

## Setup evaluation

Opening, scalp, and ordinary intraday candidates are labeled separately. Evaluators use market structure, participation, and executable-price checks before proposing an order. Proposal is not confirmation of execution.

## Single order owner

The paper execution process owns order submission and position state. It checks the sandbox environment and account identity, then reconciles owned broker orders and cumulative fills. Ambiguous placement, cancellation, or replacement results require reconciliation instead of blind retries.

The public fill-accounting sample belongs to this layer but has no ability to place an order.

## Operations and recovery

A calendar-aware local watchdog can check process health independently of the chat application. Duplicate-launch locks, deliberate pause controls, and unresolved-order checks limit recovery. Code execution does not require an AI model to decide every tick.

## Read-only reporting

The dashboard consumes state and recorded events. Active unrealized P/L and completed-trade realized P/L are distinct. Broker-reported totals are not silently equated with a locally reconstructed fill ledger.

Feedback analytics preserve versioned cohorts and evaluate later recorded trades against frozen hypotheses. They do not automatically deploy new strategy rules.

## Testing boundaries

Offline tests use synthetic observations and mocked broker responses. The public sample covers cumulative fills, partial exits, missing prices, long/short accounting, and inconsistent broker responses. The private project contains additional strategy, lifecycle, dashboard, and recovery tests.

Offline tests do not validate real exchange fills, guarantee stop execution, or establish a strategy's expected return.
