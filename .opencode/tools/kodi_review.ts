import { tool } from "@opencode-ai/plugin";
import path from "node:path";
import fs from "node:fs";
import { fixturePath } from "../lib/fixture-path";
import os from "node:os";
import { spawn } from "node:child_process";
import { stopTree } from "../lib/process-tree";

export default tool({
  description: "Read bounded numbered addon sources and the review schema, or verify a review JSON's source locations/quotes. Compose reruns static checks and derives checker records without trusting model claims. Prefer the structured report argument to avoid nested JSON escaping. Never proves semantic truth or executes addon code.",
  args: {
    addon_dir: tool.schema.string().describe("Relative addon directory within disposable fixtures"),
    operation: tool.schema.enum(["context","verify","compose"]),
    branch: tool.schema.enum(["matrix","nexus","omega","piers"]).default("nexus"),
    report: tool.schema.object({
      model_findings: tool.schema.array(tool.schema.object({}).passthrough()),
      deterministic_findings: tool.schema.array(tool.schema.object({}).passthrough()).optional(),
      coverage: tool.schema.object({scope:tool.schema.string(),complete:tool.schema.boolean(),reviewed_files:tool.schema.array(tool.schema.string())}).passthrough(),
      limitations: tool.schema.array(tool.schema.string())
    }).passthrough().optional().describe("Preferred for verify/compose: complete structured draft matching the context schema, not the context envelope"),
    report_json: tool.schema.string().optional().describe("Legacy alternative: JSON-encoded draft string. Prefer report object; never supply both.")
  },
  async execute(args, context) {
    const addon = fixturePath(context.worktree || context.directory, args.addon_dir);
    const python = process.env.KODI_TOOLKIT_PYTHON, script = process.env.KODI_TOOLKIT_CLI;
    if (!python || !script) throw new Error("Explicit trusted validation environment is required");
    let temporary: string | undefined;
    try {
      let argv = [script, "review-context", addon];
      if (args.operation !== "context") {
        if (args.report !== undefined && args.report_json !== undefined) throw new Error("Use report object or legacy report_json, never both");
        if (args.report === undefined && !args.report_json) throw new Error("A complete report object is required for verify/compose");
        const draft = args.report === undefined ? JSON.parse(args.report_json!) : args.report;
        if (!draft || typeof draft !== "object" || Array.isArray(draft)) throw new Error("Review draft must be an object");
        const serialized = JSON.stringify(draft);
        temporary = fs.mkdtempSync(path.join(os.tmpdir(), "kodi-review-report-"));
        const report = path.join(temporary,"report.json");
        fs.writeFileSync(report, serialized, {mode:0o600});
        argv = [script,args.operation === "compose" ? "review-compose" : "review-validate",addon,report];
        if (args.operation === "compose") {
          const cache=process.env.KODI_TOOLKIT_INDEX_CACHE;
          if (!cache) throw new Error("Explicit checker cache required for composition");
          argv.push("--branch",(args.branch ?? "nexus"),"--cache",cache);
        }
      }
      return await new Promise<string>((resolve,reject) => {
        const p=spawn(python,argv,{env:process.env,cwd:context.directory,shell:false,detached:process.platform !== "win32"});
        let out="",err="",timedOut=false;
        p.stdout.on("data",b=>out+=b.toString());p.stderr.on("data",b=>err+=b.toString());
        p.on("error",reject);
        p.on("close",code=>resolve(JSON.stringify({process_exit:code,output:compactReview(out,args.operation),stderr:err,timed_out:timedOut})));
        const timer=setTimeout(()=>{timedOut=true;stopTree(p);},90000);p.on("close",()=>clearTimeout(timer));
      });
    } finally { if (temporary) fs.rmSync(temporary,{recursive:true,force:true}); }
  }
});

function compactReview(raw: string, operation: string): string {
  if (operation === "context") {
    try {
      const result = JSON.parse(raw);
      // A JSON Schema is a specification, not report data. Keep it available
      // in the CLI, but give agents a compact data-shaped empty draft instead.
      delete result.report_schema;
      result.report_template = {model_findings:[],coverage:{scope:result.coverage?.scope,complete:false,reviewed_files:result.coverage?.reviewed_files ?? []},limitations:["Static source only; runtime and general semantics remain unverified."]};
      result.finding_fields = {path:"relative string from the numbered files",line:"one-based integer",quote:"literal single-line string",title:"brief string",category:["privacy","api","packaging","submission","correctness"],reason:"conditional consequence string",mechanism:"concrete source operation string",severity:["material","advisory","blocker"],confidence:["source-supported","unresolved","demonstrated"],related_evidence:"optional array of {path,line,quote,role}; role support/counterevidence/context",requirement_basis:"optional documented rule ID; an identified source does not prove applicability",reproduction:"omit for static claims; demonstrated requires actual steps/observed/expected, still unverified until independently tested"};
      result.report_instructions = "Submit actual scalar values, not JSON Schema type/const/properties objects. Empty findings are valid. Material needs independent support; blocker never follows from anchors alone.";
      return JSON.stringify(result);
    } catch { return raw; }
  }
  if (operation !== "compose") return raw;
  try {
    const result=JSON.parse(raw);
    return JSON.stringify({passed:result.passed,static_passed:result.static_passed,contract_passed:result.contract_passed,status:result.status,passed_scope:result.passed_scope,returncode:result.returncode,semantic_verification:result.semantic_verification,finding_categories:result.finding_categories,source_snapshot:result.validation_report?.source_snapshot,model_findings:result.model_findings,deterministic_findings:result.deterministic_findings,discarded_unverified_checker_claims:result.discarded_unverified_checker_claims,contract_report:{passed:result.contract_report?.passed,errors:result.contract_report?.errors,rejected_findings:result.contract_report?.rejected_findings,coverage:result.contract_report?.coverage},validation_checks:Object.fromEntries(Object.entries(result.validation_report?.checks ?? {}).map(([k,v])=>[k,{status:(v as any).status,passed:(v as any).passed,reason:(v as any).reason,exit_code:(v as any).exit_code,completed:(v as any).completed,errors:(v as any).errors,warnings:(v as any).warnings,stdout:(v as any).stdout,stderr:(v as any).stderr,infrastructure_errors:(v as any).infrastructure_errors}]))});
  } catch {return raw;}
}
