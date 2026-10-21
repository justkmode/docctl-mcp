# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About this project

docctl-mcp is a portfolio project: a local AI document controller for construction projects (ISO 19650 naming + document register checks), exposed as an MCP server. Clients: Claude Desktop, a local Ollama agent, and (planned) an n8n scheduled audit that writes to Notion. Planned next: GitHub Actions CI, model eval (Ollama + Hugging Face), README with architecture diagram + demo GIF. No cloud, no paid services.

## How I work

- I'm a platform engineer, not a programmer. I review code, I don't type all of it.
- Small steps: one change → run `uv run pytest` → stop and show me.
- Never commit or push without asking me.
- For new tasks, start with a plan I can approve before changing files.

## Comments in code

- Every function gets a docstring: what it does, in plain language.
- Add a short comment above each logical block explaining WHAT and WHY.
- Don't comment every single line. Skip obvious lines like `return result`.

## After every task, end with

- 👀 **Look at:** 1–3 places (file + line) I should read to understand the change.
- 📚 **Learn:** one concept from this task, explained simply, and why it matters for my path: platform engineering → enterprise architecture.

## Commands

All commands use [uv](https://docs.astral.sh/uv/) and must run from the repo root (some tests and scripts use paths relative to the cwd).

```bash
uv sync                                    # install deps (incl. dev group: pytest, ruff)
uv run pytest                              # full test suite
uv run pytest tests/test_naming.py::test_bad_revision -v   # single test
uv run ruff check .                        # lint (no ruff config; defaults apply)
uv run python scripts/generate_sample.py   # regenerate sample_project/ (21 files + register.csv)
uv run python -m docctl_mcp.server         # run the MCP server over stdio
uv run python scripts/check_folder.py      # quick non-MCP naming check of the sample folder
uv run python scripts/agent_mcp.py         # local Ollama agent driving the server as an MCP client
```

`scripts/generate_sample.py` **deletes everything** in `sample_project/documents/` before recreating it. The sample files are committed, so only run it if you intend to reset them.

The Ollama scripts (`scripts/agent*.py`) need a local `ollama serve` with the `qwen2.5:3b` model pulled.

## Architecture

Three layers, deliberately separated so the naming standard stays data rather than code:

1. **`naming.py` — rules engine.** `parse_filename()` splits a filename into the 9 fields of the convention (`NVN-JKR-ZZ-00-DR-A-0001_P01.pdf` = Project-Originator-Volume-Level-Type-Role-Number_Revision.Extension) and raises `ValueError` on anything it can't split into 7 dash-fields. `check_naming()` validates each field against the `PATTERNS` (regex) and `ALLOWED` (set membership) tables and returns a *list of all* human-readable errors — it never raises and never short-circuits on the first problem. **To change the naming standard, edit `PATTERNS`, `ALLOWED`, `DOC_TYPES`, `ROLES`, `EXTENSIONS` — not the validation logic.** `DocName.doc_number` is the filename minus revision and extension; it is the join key to the register.

2. **`register.py` — folder vs. register reconciliation.** `load_register()` reads a CSV keyed on `doc_number`. `compare_folder_to_register()` takes plain filename strings (not paths) plus that dict and returns three buckets: `not_in_register`, `missing_files`, `revision_mismatch`. It **silently skips** unparseable filenames — reporting those is `check_naming`'s job, so the two concerns never overlap.

3. **`server.py` — MCP surface.** Exposes `check_naming`, `list_documents`, and `audit_folder` (the composite: naming issues + all three register buckets in one call). The project folder is hardcoded: `PROJECT_ROOT` resolves to `sample_project/` relative to the source file, with `DOCS` and `REGISTER` under it. Any work on multi-project support starts here.

Nothing above layer 1 re-implements parsing; both `register.py` and `server.py` import from `naming.py`.

### MCP SDK v2

This uses the **v2** MCP Python SDK API (`from mcp.server.mcpserver import MCPServer`), not the older `FastMCP`. Tool schemas come back as `tool.input_schema` (snake_case), as seen in `scripts/agent_mcp.py` — v1 examples found online use `inputSchema` and will not work here.

Tools are plain sync functions returning JSON-serializable dicts/lists; the docstring is what the model reads to decide when to call them, so treat tool docstrings as part of the interface.

### Agent scripts

`scripts/agent.py` imports the tool functions directly from `server.py` (in-process, no MCP). `scripts/agent_mcp.py` is the real path: it spawns the server over stdio, translates the MCP tool list into Ollama's function-calling format, executes the requested calls, and feeds the results back for a single final answer. Prefer extending `agent_mcp.py` — it exercises the actual protocol.

## Testing notes

`tests/test_register.py::test_load_register_reads_sample_csv` reads `sample_project/register.csv` via a relative path and asserts on specific revisions seeded by `generate_sample.py` (e.g. `NVN-JKR-ZZ-00-DR-A-0001` is `P01` in the register but `P02` on disk — a deliberate mismatch). Changing the generator's `GOOD` list or its intentional register problems will break that test.

The sample folder intentionally contains broken names (lowercase, unknown type `XY`, missing field, revision `R1`, `.exe` extension, `Ground floor plan FINAL v2.pdf`) — they are fixtures, not bugs to clean up.