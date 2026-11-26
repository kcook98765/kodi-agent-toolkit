# Disposable managed-v2 integration smoke

Start with a disposable packaged site, available reviewed Omega image, two small approved dependency fixtures, and a Trusted Managed Lab credential scoped to that site. Use a private OpenCode configuration with only the managed connection enabled. Keep the actual provider configuration and unrelated sessions out of the test changes.

```sh
opencode --version
opencode debug skill --pure
opencode debug agent kodi-managed-lab --pure
opencode mcp list --pure
```

Check authenticated `tools/list` against the allowlist. Use an actual model session to prepare and start Omega, validate and admit a small add-on, install it natively, and verify fresh execution and its resolved dependencies. Include a direct source edit and deploy, one higher version and one changed-content same-version replacement, then a snapshot/Reset/Load round trip. Give explicit authority for replacing the disposable working profile. A brief switch to an available prepared Matrix or Nexus checks the same ownership and generation contract.

Ask for targeted logs, UI, native version/Bridge and a screenshot as needed. Export from the exact tool-call attachment when the client preserves it. [Screenshot artwork requirements](screenshots.md)

Record per-scenario MCP tool events and elapsed time. Inspect actual server results and fresh native observations independently of the model's summary. Mark authorization refusals, unavailable steps and dispatch-only outcomes explicitly. A native operation left unconfirmed needs operator review. Stop and release only the owned disposable runtime at the end.

## Handoff to the qualification run owner

Before starting, record the run ID, disposable site and runtime, source commit
and worktree, and the operator responsible for the site's infrastructure. At
closeout, record the actual outcome, unresolved operations, Stop and release
results, and any unique fixtures or logs needed for reproduction. Give that
private evidence to the exact run owner and verify the saved manifest.

The run owner rechecks the disposable Docker and containerd endpoints, child
socket mounts, and the site's ownership before infrastructure teardown. They
retire only the exact run-owned resources and record the closeout result,
including on failure, cancellation or a verified stale run. A retained
environment needs an owner, reason, scope and review date. Reassess the hold on
that date and obtain an explicit decision before clearing it. An open issue
can point to preserved evidence without keeping the entire execution environment.
