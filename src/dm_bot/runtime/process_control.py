from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path


def launch_detached_process(
    *,
    executable: str,
    args: list[str],
    cwd: Path,
    env: dict[str, str] | None = None,
    stdout_log: Path | None = None,
    stderr_log: Path | None = None,
) -> int | None:
    if os.name == "nt":
        return _launch_detached_process_windows(
            executable=executable,
            args=args,
            cwd=cwd,
            env=env,
            stdout_log=stdout_log,
            stderr_log=stderr_log,
        )

    stdout_handle = stdout_log.open("w", encoding="utf-8") if stdout_log else subprocess.DEVNULL
    stderr_handle = stderr_log.open("w", encoding="utf-8") if stderr_log else subprocess.DEVNULL
    popen_env = dict(os.environ)
    if env:
        popen_env.update(env)

    kwargs: dict[str, object] = {"cwd": str(cwd), "env": popen_env, "start_new_session": True}

    try:
        process = subprocess.Popen(
            [executable, *args],
            stdout=stdout_handle,
            stderr=stderr_handle,
            **kwargs,
        )
        return process.pid
    except OSError:
        return None
    finally:
        if hasattr(stdout_handle, "close"):
            stdout_handle.close()
        if hasattr(stderr_handle, "close"):
            stderr_handle.close()


def _launch_detached_process_windows(
    *,
    executable: str,
    args: list[str],
    cwd: Path,
    env: dict[str, str] | None,
    stdout_log: Path | None,
    stderr_log: Path | None,
) -> int | None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pid", dir=str(cwd)) as handle:
        pid_file = Path(handle.name)

    env_lines = []
    for key, value in (env or {}).items():
        escaped = value.replace("'", "''")
        env_lines.append(f"$env:{key}='{escaped}';")
    stdout_escaped = str(stdout_log).replace("'", "''") if stdout_log else ""
    stderr_escaped = str(stderr_log).replace("'", "''") if stderr_log else ""
    executable_escaped = executable.replace("'", "''")
    cwd_escaped = str(cwd).replace("'", "''")
    pid_escaped = str(pid_file).replace("'", "''")
    redirect_out = f"-RedirectStandardOutput '{stdout_escaped}'" if stdout_log else ""
    redirect_err = f"-RedirectStandardError '{stderr_escaped}'" if stderr_log else ""
    quoted_args = ", ".join("'" + arg.replace("'", "''") + "'" for arg in args)
    command = (
        "".join(env_lines)
        + f"$p = Start-Process -FilePath '{executable_escaped}' "
        + f"-ArgumentList @({quoted_args}) "
        + f"-WorkingDirectory '{cwd_escaped}' "
        + f"{redirect_out} {redirect_err} -PassThru; "
        + f"Set-Content -Path '{pid_escaped}' -Value $p.Id"
    )
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
        )
        if result.returncode != 0 or not pid_file.exists():
            return None
        try:
            return int(pid_file.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            return None
    finally:
        if pid_file.exists():
            pid_file.unlink(missing_ok=True)
