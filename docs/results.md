# Local prototype evaluation - 2026-10-13

This is a working locally validated prototype, with partial agent reliability. OpenCode 1.19.0 actually loaded skills, repaired a copied add-on, ran the official checker/stubs, inspected a managed Kodi 20.5 target over authenticated HTTP MCP, and produced source-anchored review candidates. The deterministic tools work without Kodi Lab. No remote repository was created.

**Executable qualification.** 75 regression tests pass on Ubuntu 24.04 WSL2/Python 3.12. A fresh isolated offline installation of all 24 hash-locked dependencies and the editable toolkit passes pip check and actual fixture validation. Kodistubs 20.0.1 and mypy 2.4.0 detect the intentionally wrong string logging argument. Official kodi-addon-checker 0.0.36 accepts the valid fixture with two warnings, rejects malformed XML (including its original traceback), and retains failures/coverage accurately. The review composer runs validation itself and separates literal checker records from model judgments.

**Agent coverage.** All five portable skills are discovered with valid frontmatter. Development, debugging and validation skills were actually loaded by models. Full-catalog trials selected validation from all five skills. The MCP-testing and version-compatibility bodies are available but were not separately qualified through deployment/multi-version runtime trials. No runtime add-on deployment, Kodi settings change or screenshot trial was performed in this phase; earlier verified visual delivery remains workstation evidence.

**Pilot scope.** 42 retained toolkit trials: 10 PASS, 23 PARTIAL and 9 FAIL by task/grounding criteria. These heterogeneous trials include initial harness defects, instruction variants and deliberate boundary rejection. They are not an accuracy estimate or model ranking. Review grades below are Codex artifact judgments, not a user's human sign-off. All summaries, usage, skill loads and automatic gates are in [pilot-results.json](../evaluation/pilot-results.json); original transcripts stay private. Skill availability alone did not ensure loading. Later conditions explicitly request a native skill load first.

| Trial | Result | Completed / failed tool events | First domain action / total s | Input / cached read / output |
|---|---|---:|---:|---:|
| coder-debug-baseline | PARTIAL | 3 / 0 | 16.487 / 30.611 | 1875 / 3161 / 598 |
| coder-debug-skill-v4 | PASS | 4 / 0 | 17.071 / 30.809 | 2721 / 9550 / 563 |
| mellum-debug-baseline | PARTIAL | 3 / 0 | 12.351 / 30.457 | 1865 / 5745 / 2123 |
| mellum-debug-skill-v4 | PASS | 5 / 0 | 13.231 / 25.205 | 3179 / 14178 / 1412 |
| coder-api-fix-baseline-v2 | FAIL | 9 / 0 | 29.037 / 83.939 | 16045 / 53513 / 1086 |
| coder-api-fix-skill-v2 | PARTIAL | 7 / 0 | 29.232 / 63.001 | 12307 / 31248 / 700 |
| coder-api-fix-nexus-skill-v5 | PASS | 7 / 1 | 28.735 / 51.133 | 5340 / 27835 / 784 |
| mellum-api-fix-baseline-v2 | PARTIAL | 10 / 0 | 44.52 / 61.284 | 7783 / 43033 / 4264 |
| mellum-api-fix-skill-v2 | FAIL | 6 / 0 | 24.435 / 41.511 | 7981 / 24501 / 2336 |
| mellum-api-fix-contract-baseline-v4 | PASS | 7 / 1 | 43.554 / 66.193 | 4556 / 39055 / 4949 |
| mellum-api-fix-contract-skill-v4 | PARTIAL | 10 / 3 | 51.035 / 65.321 | 5803 / 76093 / 4477 |
| coder-review-bounded-baseline-v4 | FAIL | 3 / 0 | 13.734 / 52.771 | 6112 / 12280 / 1235 |
| coder-review-bounded-skill-v4 | PASS | 6 / 0 | 20.821 / 71.426 | 8099 / 30682 / 1806 |
| coder-review-composed-skill-v5 | PARTIAL | 4 / 0 | 17.461 / 53.012 | 7466 / 17432 / 837 |
| spark-xml-skill-v3 | PARTIAL | 5 / 0 | 23.729 / 63.292 | 13179 / 0 / 2453 |
| spark-xml-bounded-skill-v4 | PASS | 4 / 1 | 21.707 / 47.652 | 14047 / 0 / 1520 |
| coder-xml-full-catalog-v4 | PARTIAL | 2 / 0 | 21.149 / 25.565 | 3330 / 4491 / 135 |
| coder-xml-full-catalog-v5 | PASS | 3 / 0 | 20.253 / 27.696 | 3627 / 7973 / 207 |

Completed tool events can return failed validation, wrong-branch coverage or infrastructure errors. Failed events count denied operations, bad arguments and bad paths. The deliberate outside-fixture denial is an expected security PASS. First domain action excludes native skill loading; legacy first-completed-tool timing is also retained in JSON. Token columns are cumulative SDK reports, with repeated cached context separate, not unique prompt sizes or billing. No manual intervention occurred inside these trials; routing, permission/adapter fixes and bounded tasks were operator interventions between trials.

**Paired observations and limitations.**
- Both initial health/UI baselines mishandled unknown selection; early available-skill conditions also skipped loading. After explicit loading and a focused debugging instruction, Coder and Mellum each passed grounded inspection. This combines routing and skill changes, not pure skill causality.
- The original edit allow-pattern failed closed; repaired relative permissions were rerun for both conditions. Coder's baseline then produced a type-valid but semantically wrong numeric log level. Its skill run made the correct INFO repair but fabricated intermediate constant mappings. Mellum's first skill run removed the level, changing behavior; a clearer contract improved the repair but repeated path errors remained.
- Explicit Nexus target and installed-stub evidence resolved a branch-guess failure. Coder's final end-to-end skill run reproduced the type error, made the minimal LOGINFO correction, and reran all checks; independent AST and validation acceptance passed.
- Coder bounded review improved from an invented deterministic rule to one source-supported potential privacy flow, corrected rejected coordinates, and kept real warnings separate. This does not prove runtime exploitability.
- Canonical composition successfully prevents invented checker rules in the deterministic section. The composed model draft still claimed unsupported blocker severity and stdout behavior, so overall review remains PARTIAL despite functional composition PASS. Evidence coordinates cannot establish semantic truth.
- Spark's repaired endpoint works with actual OpenCode/MCP. Long XML/review answers still hit its existing output budget. A bounded XML task completed after recovering from an invalid skill argument, without reconfiguring the server or changing the output budget.
- One focused skill change required reading a reported manifest line. The full-catalog rerun changed from missing the exact tag to a correct source-backed correction. These one-off trials do not establish repeatability across add-ons.

**Context and small models.** Short skill bodies are 175-265 words including frontmatter; references load on demand. Full versus narrow API task tool schemas measured 8242 versus 5943 compact JSON bytes with a skill, about 27.9% lower. Full versus narrow review schemas were 5900 versus 3601 bytes before the compose extension; final narrow compose schema was 3794 bytes. Native skill metadata adds overhead, and schema bytes are not token costs. Compact validation output retains original diagnostics/errors, removes duplicated streams and per-index metadata, and records full_cli_bytes/compact_payload_bytes. Full provenance remains available through the CLI. Fewer tools help scope but do not eliminate path guesses, wrong arguments, repeated reads, output exhaustion or unsupported claims.

**Security and licensing.** Server-side target-scoped read-only authority was preserved, alongside client filtering. Properly framed missing/invalid MCP credentials return 401; generic malformed modern probes returned 400 and are framing errors. Only the broker retains the Docker socket; Web/Kodi containers are non-privileged and have no Docker socket. No shell, deployments, settings changes, production access or model-server changes were granted. All credentials/transcripts/caches/venvs/media are excluded from this repository. Original code/skills/fixtures are MIT; installed GPL dependencies remain separate. KodiAI is proprietary: only original implementations of general review concepts were made, with no code/prompts copied. A local heuristic and known-token scan passed; public sharing still needs candidate/license review.

**Open items.** Other OS runtimes, Python versions, Kodi 19/21/22 runtimes/stub environments and Pyright are unqualified. Kodi 22 evidence is pre-release; no published 22 stubs were found. Raw logs and screenshots are not exposed by the narrow debugging trial. A package archive builder, deployment/runtime smoke qualification and comprehensive submission policy coverage remain future work. Checkers/static types cannot detect every semantic API mistake or certify a review's severity.

**Reproduce.** Install and explicitly fetch indexes as documented in [validation.md](validation.md), then use existing authorized private providers/MCP. Historical workstation aliases are not shipped. Use your verified private provider/model ID:
~~~sh
cd PATH_TO_TOOLKIT
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m kodi_agent_toolkit.cli validate fixtures/valid/script.toolkit.sample --branch nexus --cache .local/index-cache
.venv/bin/python -m kodi_agent_toolkit.cli validate fixtures/invalid-api/script.toolkit.sample --branch nexus --cache .local/index-cache
KODI_EVAL_TOOL_SCOPE=narrow .venv/bin/python evaluation/run.py --model PROVIDER/MODEL_API_ID --task api-fix-nexus --condition skill --label NEW-INFO-REPAIR
KODI_EVAL_TOOL_SCOPE=narrow .venv/bin/python evaluation/run.py --model PROVIDER/MODEL_API_ID --task xml --condition baseline --label NEW-XML-BASELINE
KODI_EVAL_TOOL_SCOPE=narrow KODI_EVAL_SKILL_CATALOG=all .venv/bin/python evaluation/run.py --model PROVIDER/MODEL_API_ID --task xml --condition skill --label NEW-XML-SKILL
.venv/bin/python evaluation/run.py --model PROVIDER/MODEL_API_ID --task debug --condition skill --label NEW-MELLUM-DEBUG
KODI_EVAL_TOOL_SCOPE=narrow .venv/bin/python evaluation/run.py --model PROVIDER/MODEL_API_ID --task review-composed --condition skill --label NEW-REVIEW
.venv/bin/python evaluation/assess.py NEW-INFO-REPAIR NEW-XML-BASELINE NEW-XML-SKILL NEW-MELLUM-DEBUG NEW-REVIEW
python3 scripts/secret-scan.py
~~~
Use fresh labels and an explicit provider/model ID on another machine. Invalid fixtures intentionally return nonzero. Inspect final transcripts and semantic acceptance even if automatic gates pass. Index snapshots change over time; compare manifest hashes to reproduce historical checker findings.
