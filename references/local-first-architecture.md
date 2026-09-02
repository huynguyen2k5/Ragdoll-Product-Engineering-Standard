# Local-First and Sustainable Architecture

Use this reference when a design choice could create mandatory hosted infrastructure, maintainer-paid compute/storage, provider lock-in, or unnecessary operational cost.

## Core invariant

Ragdoll should scale primarily by using user-owned environments rather than by increasing maintainer-operated infrastructure.

```text
more open-source users
!=
proportionally larger Ragdoll infrastructure bill
```

## Defaults

Prefer:

1. local files and SQLite before hosted databases;
2. standard library or small mature dependencies before large services;
3. user-selected local/cloud LLMs before bundled model access;
4. BYO credentials/providers before maintainer-subsidized APIs;
5. optional user-owned sync/storage adapters before mandatory Ragdoll cloud;
6. rebuildable derived indexes before irreplaceable managed indexes.

Do not introduce a hosted service merely because it is convenient during development.

## History economics

Project History should keep canonical text/events locally. Large logs and binary artifacts may use content-aware retention tiers and compression, but cold storage MUST NOT mean automatic deletion.

Semantic/vector retrieval is optional. SQLite metadata and FTS are the baseline so routine local use does not depend on paid embedding APIs or a dedicated vector database.

## Future commercial boundary

Commercial services MAY later provide managed sync, collaboration, organization-scale knowledge, governance, hosted intelligence, or other convenience. The open-source core SHOULD remain independently useful and SHOULD NOT intentionally lock user-generated Project Context or local Project History behind a paid service.

Do not build commercial infrastructure before personal dogfooding proves recurring value.
