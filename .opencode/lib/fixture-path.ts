import fs from "node:fs";
import path from "node:path";

// Client restriction for disposable evaluations; server MCP authority is separate.
export function fixturePath(directory: string, requested = "fixtures"): string {
  const workspace = fs.realpathSync(directory);
  const expected = process.env.KODI_EVAL_PROJECT_ROOT;
  if (expected && workspace !== fs.realpathSync(expected))
    throw new Error("Evaluation workspace changed; refuse access outside the disposable project");
  const fixtures = path.join(workspace, "fixtures");
  if (fs.lstatSync(fixtures).isSymbolicLink() || fs.realpathSync(fixtures) !== fixtures)
    throw new Error("Fixture root must be a real directory within the workspace");
  const candidate = path.resolve(workspace, requested);
  const relative = path.relative(fixtures, candidate);
  if (relative === ".." || relative.startsWith(".." + path.sep) || path.isAbsolute(relative))
    throw new Error("Addon must stay within disposable fixtures");
  let current = fixtures;
  try {
    for (const part of relative.split(path.sep).filter(Boolean)) {
      current = path.join(current, part);
      if (fs.lstatSync(current).isSymbolicLink() || fs.realpathSync(current) !== current)
        throw new Error("Linked fixture paths are forbidden");
    }
    if (!fs.statSync(current).isDirectory()) throw new Error("Addon path must be a directory");
    return current;
  } catch (error) {
    throw new Error("Requested fixture path is unavailable or linked. Use kodi_validate with operation=discover and omit addon_dir once; select an existing returned addon_dir. " + (error as Error).message);
  }
}
