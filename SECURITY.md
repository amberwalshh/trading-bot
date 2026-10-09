# Publication and Security

## Public material

This repository contains curated project documentation and a small broker-independent accounting sample with synthetic tests. It does not expose the full strategy, execution integration, live dashboard, private repository contents, or trading records.

## Kept outside public source control

Credentials, tokens, account identifiers and fingerprints, environment files, raw logs, order and trade records, local state, cached market data, backups, virtual environments, and screenshots containing account information are excluded. Secrets and runtime account data are also excluded from the private source repository.

The private source snapshot is not a recovery image of a broker account. Safe restoration requires a separate review of local credentials, account isolation, open orders, and process ownership.

## No automatic deployment

Publishing or editing this portfolio does not start a trader, change a strategy, or authorize an order. There is no workflow connecting public commits to broker execution.

## Public visibility is not secrecy

No open-source license is being granted, but a public repository remains viewable and forkable under GitHub's terms. Keeping the full implementation private is the primary disclosure boundary. See [GitHub's licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).

Do not submit account credentials or trade logs in public issues or pull requests.
