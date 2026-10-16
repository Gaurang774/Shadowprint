"""
Shadowprint MCP State Mutator.
Enables user-driven demonstration of baseline approval, code tampering, and rug-pull mutation.
"""

import sys
import shutil
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VARIANTS_DIR = PROJECT_ROOT / "scripts" / "variants"


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/mutate_mcp.py [clean|mutate] <path_to_mcp_dir>")
        print("Example: python scripts/mutate_mcp.py clean tests/final_test_mcp_1")
        print("         python scripts/mutate_mcp.py mutate tests/final_test_mcp_1")
        sys.exit(1)

    action = sys.argv[1].lower()
    target_dir = Path(sys.argv[2]).resolve()

    if not target_dir.exists():
        print(f"Error: Target directory '{target_dir}' does not exist.")
        sys.exit(1)

    server_name = target_dir.name
    variants_subdir = VARIANTS_DIR / server_name

    clean_src = variants_subdir / "clean.py"
    malicious_src = variants_subdir / "malicious.py"
    dest = target_dir / "server.py"

    db_path = PROJECT_ROOT / "shadowprint.db"

    # Remove extra leftover variant files from target directory so S0 only scans server.py
    for extra in ["server_clean.py", "server_malicious.py"]:
        extra_file = target_dir / extra
        if extra_file.exists():
            extra_file.unlink()

    if action == "clean":
        if not clean_src.exists():
            print(f"Error: {clean_src} not found.")
            sys.exit(1)
        shutil.copyfile(clean_src, dest)

        # Clear any prior baseline pin from shadowprint.db so user starts completely clean
        if db_path.exists():
            with sqlite3.connect(str(db_path)) as conn:
                conn.execute("DELETE FROM pins WHERE server_name = ?", (server_name,))
                conn.commit()

        print(f"[OK] '{server_name}' reset to CLEAN state.")
        print(f"  * Current code: Pure benign arithmetic server.")
        print(f"  * Database state: Cleared from shadowprint.db.")
        print(f"  * Next Step: Run 'python -m shadowprint.cli approve {sys.argv[2]}' to pin your baseline.")

    elif action == "mutate":
        if not malicious_src.exists():
            print(f"Error: {malicious_src} not found.")
            sys.exit(1)
        shutil.copyfile(malicious_src, dest)
        print(f"[MUTATED] Successfully mutated '{server_name}'!")
        print(f"  * Code injected with: S0 AST exploits, S1 prompt injections, and S2 runtime exfiltration.")
        print(f"  * Schema mutated: Added 'covert_flag' parameter and changed tool descriptions.")
        print(f"  * Next Step: Run 'python -m shadowprint.cli audit {sys.argv[2]}' to see all engines catch it!")

    else:
        print(f"Unknown action '{action}'. Use 'clean' or 'mutate'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
