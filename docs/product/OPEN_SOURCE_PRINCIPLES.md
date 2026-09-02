# Open Source and Sustainability Principles

Ragdoll is built to become useful to its maintainer first and to remain inexpensive to operate if adoption grows.

## Core sustainability invariant

More open-source users MUST NOT require proportionally more maintainer-operated infrastructure.

Default architecture therefore prefers:

- user-owned local storage;
- user-owned compute;
- user-selected local or cloud LLM providers;
- no mandatory Ragdoll account;
- no mandatory Ragdoll backend;
- no maintainer-subsidized model access;
- optional integrations that can use user-owned infrastructure.

## Dogfood before monetization

Development priority is:

```text
solve real maintainer pain
-> use Ragdoll on real product work
-> measure recurring failures
-> improve the open-source core
-> earn community adoption
-> consider commercial services only after real demand exists
```

Do not build billing, hosted dashboards, enterprise administration, or managed cloud infrastructure before the open-source workflow is independently valuable.

## Future commercial boundary

If commercial features are introduced later, prefer monetizing managed hosting, synchronization, collaboration, organization-scale knowledge, governance, and convenience. Do not intentionally cripple local ownership of project context or user-generated project history to force payment.

This document is a product principle, not a promise that any commercial feature will be built.
