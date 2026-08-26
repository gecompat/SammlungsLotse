# Repository AI Instructions

<!-- AI_REPOSITORY_FOUNDATION:BEGIN v1 -->
## AI Repository Foundation baseline

Before project work, read `.ai/foundation/FOUNDATION_RULESET.md` and then only the Foundation rule files relevant to the current scope. Project-specific instructions in this repository remain the source of truth for project facts, domain rules, architecture, state, and selected overrides.

Active project-specific governance must be transitively discoverable from this root `AGENTS.md`. If this repository keeps authoritative project rules elsewhere, preserve or add a concise project-owned discovery section outside this managed Foundation block that points to their canonical entrypoints or documents the scoped-`AGENTS.md` convention. Do not copy project rule text into this Foundation block. Active authority that cannot be discovered is an integration defect.

The current explicit task authorizes ordinary, reasonably expected and proportionate operations inside the project's authorization envelope. Do not create repeated confirmation gates for normal work. Escalate only for unresolved handling/authorization boundaries, unexpected material scope/effects, or destructive/irreversible effects lacking exact authority.

Foundation `REQUIRED` rules are a minimum protected floor; a project may intentionally be stricter. Foundation `DEFAULT` rules may be intentionally overridden by project-specific rules. Use `.ai/foundation/SEMANTIC_INTEGRATION_POLICY.md` to classify overlaps instead of replacing richer project governance.

Tool-specific adapters must lead back to this repository entry point and may not define parallel governance. When an existing adapter contains unique project rules, preserve/rehome those rules before thinning the adapter.

Foundation validation covers Foundation integration integrity only. Preserve and use the target repository's existing semantic validators, static contracts, tests, reviews, and manual validation when their contracts are affected. A green Foundation validator is not evidence that the entire project is validated.

Chat history, memory, prior scratchpads, and vendor-specific project prompts are not durable project truth.
<!-- AI_REPOSITORY_FOUNDATION:END -->

## Project-owned authority

Before project work, read docs/governance/PROJECT_RULES.md. That document
routes to the project sources required for the current scope.

Project facts, product boundaries, terminology, state, decisions and planning
authority are owned by the documents under docs/ and .ai/artifact_registry.json.
Foundation rules remain the protected baseline and do not replace those
project-owned sources.
