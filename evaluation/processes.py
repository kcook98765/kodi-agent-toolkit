"""Stop only an evaluation process tree that this harness created."""
import os
import signal
import subprocess
import threading

def launch_options():
    return {"start_new_session": True} if os.name != "nt" else {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}

def stop_tree(process, grace=2.0):
    if os.name == "nt":
        if process.poll() is None:
            subprocess.run(["taskkill","/PID",str(process.pid),"/T","/F"],
                           stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=10,check=False)
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    def force():
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    # Child pipes may outlive their parent; escalation targets the created group.
    timer=threading.Timer(grace,force);timer.daemon=True;timer.start()
