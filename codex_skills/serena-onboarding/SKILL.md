---
name: serena-onboarding
description: Onboard or refresh a project in Serena with evidence-backed code maps, symbol relationships, execution flows, and change/test navigation. Use when asked for Serena onboarding, project initialization, or richer structural memories for an already onboarded codebase.
---

# Serena project onboarding

Build a navigable explanation of the codebase for its next reader. The reader should be able to locate an entry point, follow work across components, identify the source of a contract, and choose the code and tests relevant to a change. Project activation, an index, or a README summary alone does not meet this outcome.

Onboarding updates project memories, translations, supported Serena configuration/indexes, cache inspection helpers, and the project-local `.gitignore` rule described below. Record implementation issues for later work; changing application code, global agent rules, or other repository tracking policy requires its own task scope.

## Establish the project and existing knowledge

- Resolve the requested root; default to the current working directory even when it is nested inside another repository or registered Serena project. Read Serena's initial instructions once per session and activate that exact absolute path. Treat sibling repositories and external toolchains as boundaries, not additional onboarding roots.
- Before generating Serena files, ensure `<root>/.gitignore` contains an effective rule ignoring the root's entire `.serena/` directory, including memories, Korean counterparts, configuration, and caches. Add `/.serena/` if an equivalent local rule is absent; create `.gitignore` if needed, preserve existing entries, and avoid duplicate rules on repeated onboarding. Edit the requested directory's `.gitignore`, including for a nested project, rather than a parent or global ignore file. Apply this on both initial onboarding and refresh; keep the rule even if Git has not been initialized yet.
- When the root is inside a Git repository, verify the effective ignore rules for representative `.serena` paths with `git check-ignore -v --no-index`, accounting for negation rules. Check for already tracked `.serena` files with `git ls-files`: `.gitignore` does not untrack them. Report any tracked paths and the remaining tracking issue; do not automatically remove files from the index or rewrite history.
- Inspect project instructions, Serena configuration, existing memory names, `core`, and the applicable project/global `memory_maintenance` policy before writing. Read relevant existing memories and their Korean counterparts. Preserve useful notes, user edits, read-only/ignored memory rules, and existing organization.
- For a new project, use the available onboarding tool and follow its instructions. For an existing project, refresh missing or stale structural knowledge; the presence of memories or an "already onboarded" result is not evidence that the map is adequate. Avoid regenerating unchanged memories.
- Discover the installed tool surface rather than assuming a client/version. Some versions expose individual tools; others expose `serena_repl` with `s.lsp`, `s.fs`, and `s.mem`. In the latter, use `s.info(...)` for the operations and result types you actually need. Honor the client's file/shell tools and project command wrappers.
- Use the configuration and memory locations supported by this installation, normally `<root>/.serena/project.yml` and `<root>/.serena/memories/`. Confirm configured language servers cover the project's languages. Report missing backends/dependencies; do not create a second root-level `project.yml` or copy unverified settings from tutorials.
- If Serena is unavailable, state what cannot be verified and the needed integration/setup. File-based exploration may still produce useful partial notes, but do not call it successful Serena onboarding or semantic indexing.

## Survey responsibilities before reading implementations

Read the root documentation, build/package manifests, test configuration, and a shallow directory inventory. Follow links into relevant subsystem documentation. Separate first-party source, tests, generated/vendor code, build outputs, and external dependencies; respect existing ignore rules.

Build a working coverage map of the major first-party subsystems: responsibility, source roots, entry points/public interfaces, dependencies, tests, and analysis status. Group by responsibility rather than making a file inventory. Identify the project's actual shape: application, library, monorepo, firmware, simulator, data pipeline, or a combination.

Use this map to select representative paths through the code. Prioritize startup/registration, public APIs, orchestration, state or data ownership, cross-component interfaces, and the tests that exercise them. Follow additional files when a relationship is unresolved. Large repositories need a broad map plus focused depth at important boundaries; small repositories may need just a few connected notes.

## Follow symbols and prove the relationships

Use a structure-first loop for each selected path:

1. Locate candidate files with directory/pattern search. Get symbol overviews of the relevant source files with `get_symbols_overview`; start shallow.
2. Select the entry point and important types/functions with scoped `find_symbol` queries. Use `relative_path` and the returned `name_path`; retrieve structure/signatures before bodies. Read bodies only to understand decisions, calls, data transformations, and side effects.
3. Use `find_referencing_symbols` on important interfaces to identify consumers and test usage. These are incoming references, not an outgoing call graph. Inspect the selected body's calls and resolve their definitions to establish downstream steps. Use declaration/implementation lookup when the installed backend supports it and dispatch makes it necessary.
4. Trace representative behavior from trigger/input through orchestration and domain logic to output, storage, device, or external service. Cover the main boundaries and materially different execution modes. Include state ownership, configuration selection, and failure/completion handling where they change the flow.
5. Verify both sides of cross-language, process, plugin, or hardware boundaries using registrations, bindings, schemas, ABI headers, IPC/message definitions, build rules, or focused text search. LSP references alone cannot establish these relationships. For string routes, reflection, macros, generated glue, and unsupported files, record the fallback evidence and unresolved links.
6. Locate representative tests and the declared commands that exercise the path. Record the working directory, required environment/toolchain, and whether each command was actually run. Missing tests and tests outside the root are explicit findings; do not invent validation or run expensive builds just to fill the guide.

Batch independent reads; keep evidence-dependent steps sequential. Narrow oversized queries rather than dumping the repository. Once a whole file has been read, avoid retrieving the same content again through symbol tools. An empty reference result is not proof of dead code, and a successful index is not proof of a complete dependency graph.

Keep a compact evidence ledger while exploring: `claim -> relative/path + symbol or config key -> relationship -> verified/inferred/unresolved`. Verify architecture claims against code rather than repeating documentation as fact. Record material doc/code discrepancies. Prefer stable path-plus-symbol locators in memories; volatile line numbers and tool transcripts belong outside durable notes. If displaying line numbers, check the tool's indexing convention before making editor links.

## Write a connected codebase guide

Follow the installed memory maintenance policy. Keep `core` a concise entry point and put rediscovery-heavy findings in focused memories linked from it. The following are content responsibilities, not a mandatory file count or a reason to replace existing names. Merge them for a small project; use topic memories for substantial subsystems.

| Memory/topic | Content that makes the next investigation easier |
| --- | --- |
| `core` | Purpose and root boundaries; a short ordered reading route; links explaining which question each memory answers; significant coverage gaps. |
| `architecture` | Major components, responsibility and dependency direction; runtime/build boundaries; authoritative contracts and state ownership; a small Mermaid or text diagram with meaningful edge labels. |
| `code_map` | A curated source map: `area/path -> responsibility -> entry/key symbols -> collaborators -> tests`. Distinguish implementations from compatibility wrappers, generated code, or externally owned behavior when relevant. |
| `execution_flows` | Representative end-to-end flows, grounded in actual paths and symbols: trigger, call/dispatch steps, important data/control transfers, result, and relevant failure/completion path. Label unverified edges instead of filling gaps. |
| `change_guide` | Common project-specific changes or symptoms mapped to first files/symbols to inspect, coupled contracts/consumers, and appropriate tests/commands. Include a recommended reading order for a new contributor. |
| Existing stack/commands/conventions/completion notes | Actual toolchains, prerequisites, working directories, verified versus unrun commands, and project-specific invariants. Include the substance of important team rules along with source links. |
| Optional subsystem topics, such as `<area>/core` | Deeper maps only where the component warrants them; connect from the parent map and link to related contracts/flows instead of duplicating them. |

Describe what a component does and how it connects to its neighbors. A directory label such as "backend code" or "utilities" is insufficient. A change-guide entry must identify a real starting symbol and relevant contract or test, not simply say "follow existing patterns."

For each documented flow, make the chain readable, for example:

```text
trigger/config
  -> relative/path::EntrySymbol [input/selection]
  -> relative/path::WorkerSymbol [transformation or dispatch]
  -> relative/path::ContractType [boundary and owner]
  -> output/completion [observer and relevant test]
```

Replace every example locator with observed project facts; do not force this exact shape on a library or firmware. Distinguish call, import, registration, message, and build dependencies. A static dependency diagram and an execution sequence answer different questions. Retain concise text explanations so the guide works without a diagram renderer.

Use backticked `mem:` references with actual memory names, such as `mem:execution_flows`. The referring memory explains when the linked topic is useful. Each major mapped subsystem must be reachable from `core`; avoid isolated files and a single oversized summary. Store durable relationships and non-obvious constraints, not every symbol, copied source bodies, generic framework advice, or one-off investigation logs. Record a concise reviewed revision/date and coverage note for the structural map; mark unresolved areas explicitly.

## Maintain Korean counterparts

For every project memory Markdown file, create or update its counterpart under `<root>/.serena/memory_ko/`, preserving relative paths and filenames: `.serena/memories/topic/core.md` becomes `.serena/memory_ko/topic/core.md`. Keep translations outside Serena's active memory directory unless the installation explicitly supports a separate translation location.

Translate explanatory prose, table descriptions, and diagram labels into Korean while retaining technical terms (for example, `in-order`), code, commands, paths, identifiers, and `mem:` references. Preserve the structure and meaning. Review existing counterparts before editing and preserve user-maintained additions. If source and translated edits conflict, reconcile against the code or report the unresolved conflict instead of silently discarding either. Keep unchanged translations; translate newly created/updated content and fill missing counterparts. On renames or removals, check counterparts and links without blindly deleting user notes. Do not copy global memories into the project merely to translate them.

## Add an interactive cache inspector

After indexing, place one loader at `<root>/.serena/cache/document_symbols_load.py`, on initial onboarding and refresh. Copy [assets/cache_load.py](assets/cache_load.py) to that path. The loader searches recursively for processed `document_symbols.pkl` files below its own directory by default, independently of the shell's working directory; `--directory DIR` selects another search root. Do not generate per-language or per-pickle loaders. Preserve user-customized helpers; remove superseded generated `cache/*/*_load.py` companions only after confirming they match the previous template. Do not create fake caches when indexing is unavailable.

With no positional file argument, show a terminal selection menu of relative processed-cache paths. Exclude `raw_document_symbols.pkl` and other internal caches from discovery and reject them as explicit inspection inputs. Preserve those internal pickle files for Serena; do not generate raw CSVs. Up/Down must wrap between the first and last entries; Enter loads the selected file and saves a readable CSV beside the loader, printing only the saved path and row count; q/Escape/Ctrl-C cancels with terminal settings restored. Loading a pickle that needs the Serena interpreter must retain the selection rather than showing the menu again. Without a terminal, require an explicit file path and give an actionable error.

An explicit `document_symbols.pkl` path bypasses the menu and also defaults to CSV export. Name default outputs `<language>_<cache-stem>.csv` (for example, `cpp_document_symbols.csv`) in the loader's own directory so different language caches do not overwrite each other. CSV rows represent symbols, with columns for source file, hierarchical symbol path, name, readable LSP kind, parent, depth, start/end line and column, and signature/detail. Do not export `cache_file` or `cache_hash` columns. Walk root/child symbol edges only, never parent back-references; keep a file row for empty symbol lists. Support Serena `DocumentSymbols` objects and compatible processed-cache representations; raw cache exports are outside this human-facing view. Convert LSP positions to 1-based values and explain that end positions remain exclusive. Write UTF-8 with BOM using Python's csv writer so Korean, commas and quotes survive spreadsheet import.

Retain `--summary`, `--match TEXT` for cached source paths, and optional `--full` JSON on stdout. `--output FILE.csv` selects a CSV destination; `--output FILE.json` explicitly exports complete JSON. Reject other output extensions and protect cache/loader files from overwrite. Shared/cyclic objects in JSON use `$ref` path markers. Load real Serena objects and, when necessary, retry with the interpreter named by the installed `serena` executable's shebang. Report missing modules/runtime rather than installing dependencies or substituting placeholder classes. Only load trusted local Serena caches: pickle loading can execute code.

Validate Up/Down wrapping, selection/Enter CSV creation, cancellation and terminal restoration in a PTY. Check the default search root by invoking from outside the project, and verify runtime fallback does not repeat selection. Verify raw caches are absent from the menu and explicit raw input is rejected. Open every discovered processed cache with an explicit file argument; parse the resulting CSV with csv.DictReader, inspect representative nested symbols and 1-based source positions, and verify UTF-8 BOM/quoted-field round trips. Check filtered exports and retain validation of optional JSON export. Confirm original pickle contents are unchanged. Report inspection failures separately from indexing, and provide `python .serena/cache/document_symbols_load.py` as the interactive example (honor project command wrappers). Keep this helper under the ignored `.serena/` tree; it is not application source or proof of complete semantic coverage.

## Backfill inspectors across existing projects

Only when the user explicitly requests a multi-project backfill, search the requested base (for example `~/prj`) for `.serena` directories, pruning each `.serena` from further traversal and avoiding symlink loops. A configuration, cache or `memory_maintenance` alone does not establish onboarding: inspect a nonempty project `memories/core.md` (or an established equivalent overview) plus substantive project memories. Classify roots as onboarded, not onboarded, or unclear; report the evidence and skip unclear roots rather than creating onboarding notes just to qualify them.

For onboarded roots, install the same `cache/document_symbols_load.py` template and validate available processed caches. Preserve custom loaders and report conflicts instead of overwriting them blindly; known previous generated templates may be upgraded. A project with onboarding memories but no processed caches may receive the helper, but report that actual loading could not be tested. Keep application files, internal pickle caches, existing memories and other projects' tracking rules intact. Do not activate, reindex or re-onboard every root merely to distribute this helper. Remove old raw CSVs only when confirmed to be prior generated inspector output, preserving unrelated/user-edited files. Report updated/skipped/failed roots and validation results.

## Index and validate the result

Index supported symbols with the installed CLI if available; inspect `serena project index --help` and target the exact root. Index earlier if it helps exploration, or afterward to warm the cache. Respect ignore/workspace settings and avoid redundant full indexing within the run. Do not silently change models or install toolchains to make indexing appear complete.

Verify the map rather than only checking file creation:

- Read back `core` and the new/changed memories. Follow their references and spot-check key source paths/symbols and diagram edges. Reuse gathered evidence, making fresh queries where an ambiguity remains.
- Try a short navigation exercise using the written guide: locate a real entry point, follow one representative cross-component flow, then locate the code, contract, and test/command for a plausible change. Fix vague or missing directions. Repeat for materially different subsystems when one path would leave the map untested.
- Check that every major first-party subsystem from the survey is mapped or explicitly marked as partial/excluded with a reason. Distinguish semantic coverage, text-only inspection, external boundaries, and unresolved work.
- Compare project memory paths with Korean counterparts and review meaning, links, tables, and diagrams in the changed pairs.
- If supported, run `serena memories check` for the exact project and inspect its report. Some versions always exit zero, including when stale references are reported; exit status alone is insufficient. A reference check does not verify architecture facts.
- Report index results separately from memory quality: actual supported languages, processed/skipped/failed files when available, and remaining backend/setup problems. Do not claim whole-project understanding from cache creation.

Finish in the user's language with a compact codebase orientation: the main components and one important flow using real names, useful findings or structural pitfalls, and clickable paths to the starting guide and its Korean counterpart. Give the recommended reading order, what was verified, and any material gaps. File counts and an "onboarding complete" message alone are insufficient. Memories remain reviewable context; unresolved evidence should stay visible to the next reader.
