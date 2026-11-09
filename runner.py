"""Runs student code (Python, C, C++, Java, JavaScript) in a separate process with a timeout.
C/C++/Java/JS need gcc, g++, javac/java, node installed. If missing, running is skipped
and the AI analyses the code without executing it. Local learning tool only."""
import os
import re
import shutil
import subprocess
import sys
import tempfile


def _run(cmd, timeout, cwd):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return {"stdout": p.stdout, "stderr": p.stderr, "returncode": p.returncode, "note": ""}
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": f"TimeoutError: ran longer than {timeout}s (infinite loop?)",
                "returncode": -1, "note": ""}


def _skip(tool):
    return {"stdout": "", "stderr": "", "returncode": None,
            "note": f"{tool} is not installed on this computer, so the code was not executed. "
                    f"The AI will analyse it without running."}


def run_code(code: str, language: str = "Python", timeout: int = 10) -> dict:
    if os.getenv("DISABLE_CODE_RUN"):
        return {"stdout": "", "stderr": "", "returncode": None,
                "note": "Code execution is disabled in the online version. The AI will still analyse your code."}
    lang = language.lower()
    exe_ext = ".exe" if os.name == "nt" else ""
    with tempfile.TemporaryDirectory() as d:
        if lang == "python":
            path = os.path.join(d, "main.py")
            open(path, "w", encoding="utf-8").write(code)
            return _run([sys.executable, path], timeout, d)

        if lang in ("c", "c++"):
            compiler, src = ("gcc", "main.c") if lang == "c" else ("g++", "main.cpp")
            if not shutil.which(compiler):
                return _skip(compiler)
            open(os.path.join(d, src), "w", encoding="utf-8").write(code)
            out = "main" + exe_ext
            c = _run([compiler, src, "-o", out], timeout, d)
            if c["returncode"] != 0:
                c["stderr"] = "COMPILATION ERROR:\n" + c["stderr"]
                return c
            return _run([os.path.join(d, out)], timeout, d)

        if lang == "java":
            if not (shutil.which("javac") and shutil.which("java")):
                return _skip("Java JDK (javac)")
            m = re.search(r"public\s+class\s+(\w+)", code) or re.search(r"class\s+(\w+)", code)
            cls = m.group(1) if m else "Main"
            open(os.path.join(d, cls + ".java"), "w", encoding="utf-8").write(code)
            c = _run(["javac", cls + ".java"], timeout, d)
            if c["returncode"] != 0:
                c["stderr"] = "COMPILATION ERROR:\n" + c["stderr"]
                return c
            return _run(["java", "-cp", d, cls], timeout, d)

        if lang == "javascript":
            if not shutil.which("node"):
                return _skip("Node.js")
            path = os.path.join(d, "main.js")
            open(path, "w", encoding="utf-8").write(code)
            return _run(["node", path], timeout, d)

    return {"stdout": "", "stderr": f"Unsupported language: {language}", "returncode": None, "note": ""}