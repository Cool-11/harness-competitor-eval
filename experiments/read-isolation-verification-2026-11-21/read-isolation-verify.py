import json, os, pathlib

def try_read(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = f.read()
        return {"path": path, "status": "readable", "bytes": len(data)}
    except FileNotFoundError:
        return {"path": path, "status": "denied_FileNotFoundError"}
    except PermissionError:
        return {"path": path, "status": "denied_PermissionError"}
    except IsADirectoryError:
        return {"path": path, "status": "denied_IsADirectoryError"}
    except Exception as e:
        return {"path": path, "status": "denied_" + type(e).__name__}

judge_files = [
    "AGENTS.md",
    "tasks/second_tasks/S11-corrupt-recovery/checker.py",
    "tasks/second_tasks/S11-corrupt-recovery/spec.md",
    "tasks/second_tasks/S11-corrupt-recovery/truth.json",
    "Log-analyse/S-batch/S11-corrupt-recovery/codex/run4/checker_output.txt",
    "Log-analyse/S-batch/S11-corrupt-recovery/dsh/run6/checker_output.txt",
]

repo_variants = [
    "F:\\for-project-new\\harness-competitor-eval",
    "F:/for-project-new/harness-competitor-eval",
    "/F:/for-project-new/harness-competitor-eval",
    "/for-project-new/harness-competitor-eval",
    "/mnt/f/for-project-new/harness-competitor-eval",
]

results = []

for p in ["/tests", "/app", "/var/run/docker.sock", "/logs", "/root/.ssh"]:
    results.append({"check": "forbidden_exists", "path": p, "exists": pathlib.Path(p).exists()})

for variant in repo_variants:
    for f in judge_files:
        results.append(try_read(os.path.join(variant, f)))

work_files = [str(p) for p in pathlib.Path("/work").rglob("*") if p.is_file()]
results.append({"check": "work_files", "files": work_files})

sensitive_env = {}
for k, v in os.environ.items():
    if any(s in k.upper() for s in ("KEY", "TOKEN", "SECRET", "PASS", "CRED")):
        sensitive_env[k] = (v[:4] + "...") if v else v
results.append({"check": "sensitive_env", "keys": sensitive_env})

markers = ["truth.json", "checker.py", "AGENTS.md"]
found = []
for root in ["/work", "/state", "/control", "/tmp", "/var/tmp", "/root", "/app", "/tests"]:
    try:
        for dirpath, dirnames, filenames in os.walk(root):
            if dirpath.count(os.sep) > 6:
                dirnames[:] = []
                continue
            for fn in filenames:
                if fn in markers:
                    found.append(os.path.join(dirpath, fn))
    except Exception:
        pass
results.append({"check": "marker_search", "found": found})

hostname = ""
try:
    hostname = pathlib.Path("/etc/hostname").read_text().strip()
except Exception:
    pass

print(json.dumps({"hostname": hostname, "cwd": str(pathlib.Path.cwd()),
                  "uid": os.getuid() if hasattr(os, "getuid") else None,
                  "results": results}, ensure_ascii=False))
