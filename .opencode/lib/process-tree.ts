import { execFile, type ChildProcess } from "node:child_process";
export function stopTree(p: ChildProcess) {
  if (!p.pid) return;
  if (process.platform === "win32") {
    if (p.exitCode === null) execFile("taskkill",["/PID",String(p.pid),"/T","/F"],()=>{});
    return;
  }
  try { process.kill(-p.pid,"SIGTERM"); } catch { return; }
  const escalation=setTimeout(()=>{ try { process.kill(-p.pid!,"SIGKILL"); } catch {} },2000);
  escalation.unref();
}
