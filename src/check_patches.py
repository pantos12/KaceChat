import platform
import subprocess


def check_patch_status(cve_id: str):
    """
    Placeholder: map CVE -> patch KB/vendor update first, then check local system.
    This function currently returns None (unknown).
    """
    return None


# Windows-only helper: check if a specific KB is installed
# Example usage: is_kb_installed("KB5034441")

def is_kb_installed(kb_id: str) -> bool:
    if platform.system().lower() != "windows":
        return False
    try:
        cmd = ["powershell", "-NoProfile", "-Command", f"Get-HotFix -Id {kb_id}"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return result.returncode == 0
    except Exception:
        return False
