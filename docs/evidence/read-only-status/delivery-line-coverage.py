"""Source-only stdlib trace measurement; never a runtime qualification."""
import json
import runpy
import sys
import sysconfig
import trace
from pathlib import Path

root = Path.cwd()
destination = Path(sys.argv[1])
targets = [root / "research/status_view.py", root / "research/review_report.py"]
tracer = trace.Trace(count=True, trace=False,
                     ignoredirs=list(set(sysconfig.get_paths()[key]
                                         for key in ("stdlib", "purelib", "platlib"))))
exit_code = 0
try:
    tracer.runctx('runpy.run_path("tests/unit_capstone_backend_suite.py", run_name="__main__")',
                  {"runpy": runpy}, {})
except SystemExit as exc:
    exit_code = exc.code if isinstance(exc.code, int) else int(exc.code is not None)
counts = tracer.results().counts
measurements = []
for target in targets:
    executable = set(trace._find_executable_linenos(str(target)))
    hit = {line for (filename, line), count in counts.items()
           if filename == str(target) and count > 0} & executable
    measurements.append({"path": str(target.relative_to(root)),
                         "executed_lines": len(hit), "executable_lines": len(executable),
                         "percent": round(100 * len(hit) / len(executable), 2)})
denominator = sum(item["executable_lines"] for item in measurements)
numerator = sum(item["executed_lines"] for item in measurements)
result = {"source_only": True, "method": "stdlib trace executable-line hits",
          "python": sys.version.split()[0], "suite_exit_code": exit_code,
          "modules": measurements, "combined_executed_lines": numerator,
          "combined_executable_lines": denominator,
          "combined_percent": round(100 * numerator / denominator, 2),
          "limits": "Two in-process modules only; not branch or subprocess CLI coverage, not runtime qualification"}
destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, sort_keys=True))
raise SystemExit(exit_code)
