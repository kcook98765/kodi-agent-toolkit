import { tool } from "@opencode-ai/plugin";
import { fixturePath } from "../lib/fixture-path";
import { spawn } from "node:child_process";
import { stopTree } from "../lib/process-tree";

export default tool({
  description: "Discover existing fixture roots, files and manifest entry points; or run offline static Kodi validation. No addon execution, downloads or deployment.",
  args: {
    operation: tool.schema.enum(["discover", "validate"]).default("validate"),
    addon_dir: tool.schema.string().optional().describe("Project-relative addon directory inside fixtures. For discovery omit to enumerate actual paths."),
    branch: tool.schema.enum(["matrix","nexus","omega","piers"]).default("nexus")
  },
  async execute(args, context) {
    const operation = args.operation ?? "validate";
    if (operation === "validate" && !args.addon_dir) throw new Error("addon_dir is required for validation; discover first if unknown");
    const addon = fixturePath(context.worktree || context.directory, args.addon_dir ?? "fixtures");
    const python = process.env.KODI_TOOLKIT_PYTHON;
    const script = process.env.KODI_TOOLKIT_CLI;
    const cache = process.env.KODI_TOOLKIT_INDEX_CACHE;
    if (!python || !script) throw new Error("Explicit local Python/CLI environment is required");
    if (operation === "validate" && !cache) throw new Error("Explicit validation cache is required");
    return await new Promise<string>((resolve, reject) => {
      const argv = operation === "discover" ? [script, "discover", addon] : [script, "validate", addon, "--branch", (args.branch ?? "nexus"), "--cache", cache!];
      const p = spawn(python, argv,
        {env: process.env, cwd: context.directory, shell: false, detached: process.platform !== "win32"});
      let out = "", err = "", timedOut = false;
      p.stdout.on("data", b => out += b.toString());
      p.stderr.on("data", b => err += b.toString());
      p.on("error", reject);
      p.on("close", code => {
        let compact = out;
        try {
          if (operation === "discover") throw new Error("Keep full discovery output");
          const result = JSON.parse(out);
          const checks: Record<string,unknown> = {};
          for (const [name,value] of Object.entries(result.checks ?? {})) {
            const stage = value as Record<string,unknown>;
            checks[name] = Object.fromEntries(["status","passed","reason","errors","warnings","stdout","stderr","exit_code","completed","error_count","warning_count","stub_version","mypy_version","online_url_checks","infrastructure_errors"].filter(k=>k in stage).map(k=>[k,stage[k]]));
          }
          const checkerFailure = result.checks?.official_checker?.replay?.failure;
          if (checkerFailure && checks.official_checker) (checks.official_checker as Record<string,unknown>).infrastructure_failure = checkerFailure;
          const cacheEvidence = result.checks?.official_checker?.replay?.cache;
          compact = JSON.stringify({passed:result.passed,returncode:result.returncode,branch:result.branch,source_snapshot:result.source_snapshot,checks,config_input:result.config_input,coverage_limits:result.coverage_limits,cache:cacheEvidence ? {fetched_at:cacheEvidence.fetched_at,manifest_sha256:cacheEvidence.manifest_sha256} : null});
        } catch { /* Preserve the complete stream on infrastructure/non-JSON failure. */ }
        resolve(JSON.stringify({process_exit:code,output:compact,stderr:err,full_cli_bytes:Buffer.byteLength(out),compact_payload_bytes:Buffer.byteLength(compact),timed_out:timedOut}));
      });
      const timer = setTimeout(() => {timedOut=true;stopTree(p);}, 90000);
      p.on("close", () => clearTimeout(timer));
    });
  }
});
