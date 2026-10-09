# Trading Bot Engineering Portfolio

A personal, AI-assisted software project exploring real-time market data, guarded paper execution, and trade observability. Built around a Webull sandbox stock bot with a local read-only dashboard.

This repository is a **public engineering showcase**, not the complete trading system. The strategy implementation, execution integration, and experiment configurations are maintained separately in a private repository. No credentials, account records, or broker data are included here.

## What the project explores

- **Streaming data:** aggregate observed trades into short-interval candles, distinguish completed from forming bars, and reject stale observations.
- **Execution reliability:** reconcile cumulative fills, track owned orders, and handle uncertainty without assuming an order request succeeded.
- **Operational safeguards:** sandbox account isolation, duplicate-process protection, market-session boundaries, and a standalone Windows watchdog.
- **Observability:** a read-only dashboard for active positions, completed trades, scanner candidates, rejection reasons, and process health.
- **Controlled evaluation:** versioned experiments and advisory trade-feedback analysis, with historical results separated from changed rules.

## A small code sample

[`examples/fill_accounting.py`](examples/fill_accounting.py) is an isolated accounting component from the project. It has no broker client, network calls, credentials, or entry signals. It demonstrates cumulative-fill reconciliation and gross realized P/L calculation without guessing missing fill prices.

The accompanying tests use entirely synthetic orders. With Python 3.10 or later, run from this repository's root:

```text
python -B -m unittest discover -s examples -p "test_*.py" -v
```

The examples cannot place orders. Passing tests demonstrate these specific accounting behaviors, not profitability or production readiness.

## Engineering decisions worth discussing

1. **Detection is not execution.** A scanner candidate, a qualified setup, a submitted order, and a confirmed fill are separate events.
2. **Unknown is not zero.** Missing exit evidence must not become a fabricated zero-profit trade.
3. **Repeated observations must be safe.** Receiving the same cumulative fill twice must not double the position or realized result.
4. **Recovery must preserve ownership.** A restart must not cancel unrelated orders or assume an ambiguous account is flat.
5. **Metrics need context.** Paper fills, before-fee P/L, and synthetic tests are labeled separately from live-market evidence.

See [Architecture](ARCHITECTURE.md) for the system boundaries and [Publication and security](SECURITY.md) for what stays private.

## Current status and limitations

This is an evolving personal project. The existing implementation is being preserved while a simpler day-trading and scalping strategy is planned. Strategy performance is **not established**, and this portfolio makes no claim of reliable returns or live-money readiness. Paper fills do not establish achievable live fills, slippage, fees, or future returns.

Trade feedback proposes comparisons for review; it is not an autonomous model that learns a profitable strategy or silently rewrites trading rules. Extended-hours software exits are not equivalent to native broker-stop protection.

## Project authorship

Project owner: [amberwalshh](https://github.com/amberwalshh). Developed iteratively with AI coding assistance. The portfolio highlights the design requirements, implementation tradeoffs, testing, and operational lessons rather than claiming that every line was manually authored.

## Reuse

No open-source license is granted. See [NOTICE](NOTICE). Public material is necessarily visible and can be copied; sensitive implementation is kept private rather than relying on a notice to keep it secret.
