#!/usr/bin/env python3
"""
MUR IDE smoke test (без подключения к роботу/симулятору).

Проверяет:
1) запуск Python-скрипта из IDE;
2) вывод stdout/stderr в лог IDE;
3) простые файловые операции.
"""

import os
import platform
import sys
import tempfile
import time
from pathlib import Path


def main() -> int:
    print("=== MUR IDE smoke test ===", flush=True)
    print(f"Python: {sys.version.split()[0]}", flush=True)
    print(f"Platform: {platform.platform()}", flush=True)
    print(f"Executable: {sys.executable}", flush=True)
    print(f"CWD: {os.getcwd()}", flush=True)

    # Шаги с задержкой удобны, чтобы проверить кнопку Stop в IDE.
    for i in range(1, 6):
        print(f"[step {i}/5] running...", flush=True)
        time.sleep(0.7)

    # Проверка stderr: строка должна появиться в логе ошибок IDE.
    print("[stderr] test message", file=sys.stderr, flush=True)

    # Проверка файловой системы.
    temp_dir = Path(tempfile.gettempdir())
    out_file = temp_dir / "mur_ide_smoke_test.txt"
    out_file.write_text("ok\n", encoding="utf-8")
    content = out_file.read_text(encoding="utf-8").strip()
    print(f"Temp file: {out_file}", flush=True)
    print(f"Temp file content: {content}", flush=True)

    print("SMOKE_TEST_OK", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
    
    
    
    
    
    
    
    
