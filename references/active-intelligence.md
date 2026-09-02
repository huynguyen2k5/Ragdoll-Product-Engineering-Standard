# Active Engineering Intelligence

This skill operates in **Active Intelligence** mode. During a real engineering task, the agent MAY discover and evaluate current open-source tools, repositories, engineering articles, specifications, and senior-engineer guidance when that can materially improve correctness, design quality, delivery speed, security, or maintainability.

Active discovery is not permission to chase novelty. Treat external knowledge as candidate evidence until evaluated.

## Trigger conditions

Consider active discovery when one or more apply:

- the repository lacks a clear solution for a non-trivial need;
- a task would benefit from specialized static analysis, testing, security, accessibility, performance, migration, documentation, or design tooling;
- the agent is uncertain about current ecosystem best practice;
- the installed solution appears stale, unsafe, or poorly maintained;
- the user explicitly asks for current/trending/proven OSS options;
- an implementation would otherwise require substantial custom infrastructure;
- a design decision has meaningful long-term cost and external evidence could reduce uncertainty.

Do not search externally for trivial tasks that can be solved safely with existing repository capabilities.

## Runtime discovery loop

1. **Define the problem** in product/engineering terms before searching for a tool.
2. **Inspect existing capabilities**: dependencies, scripts, framework utilities, CI, internal libraries, and repository conventions.
3. **Search current primary sources**: official docs, canonical repositories, specifications, release notes, maintainer guidance.
4. **Build a small candidate set**. Do not collect dozens of repos without purpose.
5. **Evaluate candidates** using `references/tool-selection.md`.
6. **Check integration cost**: dependencies, runtime footprint, configuration, CI time, lock-in, migration cost, license, and security surface.
7. **Prefer an experiment** for uncertain/high-impact choices. Use a branch, isolated command, benchmark, spike, or minimal proof before broad adoption.
8. **Adopt only if the net benefit is clear** compared with existing code and simpler alternatives.
9. **Validate the result** with the tool and with product-level behavior; do not equate tool success with product correctness.
10. **Record durable learning** when a candidate becomes a repeated project/standard recommendation.

## Search discipline

Active Intelligence MUST respect `llm-execution-policy.md`. Model locality and network access are separate permissions. A local LLM may use current web/GitHub discovery when network access is enabled; fully local/offline mode MUST NOT use remote discovery.

When web/GitHub access is available:

- Prefer canonical repositories and official project documentation.
- Prefer current release notes and recently maintained docs for version-sensitive claims.
- Search for known limitations, migration pain, security issues, abandoned forks, and credible counterexamples.
- Check whether the repository is actively maintained; stars alone are insufficient.
- Distinguish real production adoption from demo/tutorial popularity.
- Use trending lists only to discover candidates, never as automatic approval.

When external access is unavailable:

- use repository-local evidence and the curated catalog in `references/tool-catalog.md`;
- clearly state that current maintenance/status could not be verified;
- do not invent latest versions, star counts, release dates, or compatibility.

## Evidence labels for runtime decisions

Classify external findings as:

- **Normative**: specification, security standard, language/platform contract.
- **Established**: maintained guidance or OSS practice with broad real-world use.
- **Contextual**: useful pattern tied to a specific stack or operational model.
- **Experimental**: promising but insufficiently proven for default adoption.
- **Rejected**: poor fit, stale, unsafe, excessive complexity, problematic license, or no material advantage.

A trending repository starts as **Experimental** unless stronger evidence exists.

## Active-use safety rules

The agent MUST NOT:

- install or execute arbitrary code solely because a repository is popular;
- pipe remote install scripts directly to a privileged shell without explicit need and review;
- grant broad secrets, filesystem, network, cloud, or production access to a new tool by default;
- replace an established repository toolchain without a demonstrated benefit;
- introduce a large framework to solve a small local problem;
- hide new transitive dependencies or license implications;
- persist a candidate as a standard recommendation without provenance.

## Product-first rule

External tooling exists to improve the product engineering outcome. If a tool increases ceremony, dependency risk, build time, or cognitive load more than it improves quality, do not adopt it.

