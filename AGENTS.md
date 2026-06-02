# AGENTS.md

## Project Overview

`openwisp-network-topology` is the OpenWISP Django app for collecting, storing, visualizing, and comparing network topology data.

Core code lives in `openwisp_network_topology/`:

- `base/` contains abstract models and core topology/snapshot behavior.
- `api/`, `visualizer/`, `integrations/`, `tasks.py`, `signals.py`, `consumers.py`, and `routing.py` provide API, graph visualization, integrations, background jobs, and websocket behavior.
- `management/`, `fixtures/`, `templates/`, and `static/` support imports, demo data, UI, and assets.
- Tests live in `openwisp_network_topology/tests/` and `tests/`.

## Source of Truth

- Use `docs/developer/installation.rst` and `docs/developer/index.rst` for local setup, services, and baseline test commands.
- Use `.github/workflows/ci.yml` for CI-tested dependencies, QA/test commands, env vars, and supported Python/Django versions.
- Use GitHub issue/PR templates when asked to open issues or PRs.

If instructions conflict, repository config and CI workflows win first, official docs next, and this file is supplemental.

## Development Notes

- Keep changes focused. Avoid unrelated refactors and formatting churn.
- Preserve public APIs, migrations, swappable models, topology parser behavior, graph data formats, snapshot semantics, and integration points unless explicitly required.
- Mark user-facing strings for translation with Django i18n helpers in Django code.
- Avoid unnecessary blank lines inside function and method bodies.
- Update docs when behavior, settings, public APIs, setup steps, topology formats, or supported versions change.

## Testing and QA

- Add or update tests for every behavior change.
- For bug fixes, write the regression test first, run it against the unfixed code, confirm it fails for the expected reason, then implement the fix.
- Use targeted tests while iterating, then run the documented full test command before considering the change complete.
- Run `openwisp-qa-format` after editing when available.
- Run `./run-qa-checks` when present. Treat failures as blocking unless confirmed unrelated and reported.
- Prefer in-process tests so coverage tools can measure changed code.

## Django Notes

- Preserve tenant isolation and object-level permissions for organizations, topologies, links, nodes, snapshots, and related integrations.
- Be careful with queryset filtering, serializers, admin behavior, signals, Celery tasks, websocket consumers, graph snapshots, and parser integrations.
- When changing APIs, include tests for permissions, validation, filtering, pagination, and tenant boundaries.

## Security Notes

- Watch for cross-tenant data leaks, permission bypasses, malformed topology input, unsafe graph data, unsafe redirects, and secrets.
- Preserve validation around topology payloads, parser output, graph JSON, integrations, snapshots, URLs, and imported data.
- Write comments and docstrings only when they explain why code is shaped a certain way. Put comments before the relevant code block instead of scattering them inside it.

## Troubleshooting

- If setup, QA, or tests fail, check docs first, then compare with CI. If commands diverge, follow CI.
