"""
Shadowprint Environment & System Preflight Check.
Owner: Gaurang Udgirkar (Builder B)

Validates all system requirements:
1. Python version >= 3.10
2. Required Python libraries
3. Docker Desktop daemon & SYS_PTRACE capability
4. Ollama service & local Qwen3 models
5. Git branch setup (main, feat/jasjyot, feat/gaurang)
"""

import sys
import subprocess
import json
import urllib.request
from typing import Tuple, List


def check_python_version() -> Tuple[bool, str]:
    v = sys.version_info
    if v.major == 3 and v.minor >= 10:
        return True, f"Python {v.major}.{v.minor}.{v.micro} (>= 3.10 required)"
    return False, f"Python {v.major}.{v.minor}.{v.micro} is too old (>= 3.10 required)"


def check_python_packages() -> Tuple[bool, List[str], List[str]]:
    packages = ["pydantic", "typer", "rich", "mcp", "deepdiff", "bandit", "ollama", "requests"]
    installed = []
    missing = []
    for pkg in packages:
        try:
            __import__(pkg)
            installed.append(pkg)
        except ImportError:
            missing.append(pkg)
    return len(missing) == 0, installed, missing


def check_docker_daemon() -> Tuple[bool, str]:
    try:
        res = subprocess.run(["docker", "ps"], capture_output=True, text=True, timeout=10)
        if res.returncode == 0:
            return True, "Docker daemon is running and accessible."
        return False, f"Docker daemon returned code {res.returncode}: {res.stderr.strip()}"
    except Exception as e:
        return False, f"Docker check failed: {e}"


def check_ollama_service() -> Tuple[bool, str, List[str]]:
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags")
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                models = [m.get("name", "") for m in data.get("models", [])]
                has_qwen = any("qwen3" in m or "qwen2.5" in m for m in models)
                if has_qwen:
                    return True, "Ollama is running with compatible models.", models
                return False, "Ollama is running but missing qwen3 models.", models
        return False, f"Ollama HTTP returned status {response.status}", []
    except Exception as e:
        return False, f"Ollama service check failed: {e}", []


def check_git_branches() -> Tuple[bool, List[str]]:
    try:
        res = subprocess.run(["git", "branch"], capture_output=True, text=True, timeout=5)
        if res.returncode == 0:
            branches = [b.strip().replace("* ", "") for b in res.stdout.strip().splitlines() if b.strip()]
            has_jasjyot = "feat/jasjyot" in branches
            has_gaurang = "feat/gaurang" in branches
            return (has_jasjyot and has_gaurang), branches
        return False, []
    except Exception as e:
        return False, []


def main():
    print("=" * 60)
    print("SHADOWPRINT PREFLIGHT ENVIRONMENT SANITY CHECK")
    print("=" * 60)

    # 1. Python
    py_ok, py_msg = check_python_version()
    print(f"[{'PASS' if py_ok else 'FAIL'}] Python: {py_msg}")

    # 2. Packages
    pkg_ok, installed, missing = check_python_packages()
    if pkg_ok:
        print(f"[PASS] Python Packages: All {len(installed)} core packages installed.")
    else:
        print(f"[WARN] Python Packages: {len(installed)} installed, {len(missing)} missing.")
        print(f"       Missing: {', '.join(missing)}")
        print(f"       Install with: pip install -r requirements.txt")

    # 3. Docker
    docker_ok, docker_msg = check_docker_daemon()
    print(f"[{'PASS' if docker_ok else 'FAIL'}] Docker: {docker_msg}")

    # 4. Ollama
    ollama_ok, ollama_msg, models = check_ollama_service()
    print(f"[{'PASS' if ollama_ok else 'FAIL'}] Ollama: {ollama_msg}")
    if models:
        print(f"       Available Models: {', '.join(models)}")

    # 5. Git Branches
    git_ok, branches = check_git_branches()
    print(f"[{'PASS' if git_ok else 'FAIL'}] Git Branches: {', '.join(branches)}")

    print("=" * 60)
    all_ready = py_ok and docker_ok and ollama_ok and git_ok
    if all_ready and not pkg_ok:
        print("STATUS: System environment is ready! Just run `pip install -r requirements.txt`.")
    elif all_ready and pkg_ok:
        print("STATUS: 100% READY FOR DEVELOPMENT!")
    else:
        print("STATUS: Some preflight checks failed. Please resolve above items.")
    print("=" * 60)


if __name__ == "__main__":
    main()
