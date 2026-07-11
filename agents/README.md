# Agent Registry

This folder contains operational agent definitions for the Power Trading application.

Agents are maintained like software:

- registered;
- versioned;
- scoped;
- reviewed;
- validated;
- retired when obsolete.

## Folder structure

```text
agents/
  registry.yaml
  README.md
  schemas/
    agent.schema.json
  codebase-qc/
    AGENT.md
    checklist.md
    memory.md
    changelog.md
```

## Context loading model

Agents should not load every document every time. Use layered context:

```text
Always loaded:
  AGENTS.md
  agents/registry.yaml

Loaded by trigger:
  agents/<agent-id>/AGENT.md

Loaded for validation:
  agents/<agent-id>/checklist.md

Loaded only when useful:
  agents/<agent-id>/memory.md
  planning/*
  docs/*
  archive/*
```

## Adding a new agent

1. Create `agents/<agent-id>/`.
2. Add `AGENT.md`, `checklist.md`, `memory.md`, and `changelog.md`.
3. Register it in `agents/registry.yaml`.
4. Keep scope narrow.
5. Define forbidden actions.
6. Define quality gates.
7. Commit as a normal code change.

## Agent lifecycle

```text
proposed → active → deprecated → retired
```

No agent should remain active without:

- owner;
- purpose;
- scope;
- trigger rules;
- validation checklist.
