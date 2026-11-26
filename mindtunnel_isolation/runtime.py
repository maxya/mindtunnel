"""Trusted startup for the fixed Python worker selected by the host launcher."""
import resource
import runpy
import sys

entry, output_limit = sys.argv[1:]
for kind, limit in ((resource.RLIMIT_AS, 256 * 1024 * 1024), (resource.RLIMIT_CPU, 10),
                    (resource.RLIMIT_CORE, 0), (resource.RLIMIT_FSIZE, int(output_limit))):
    resource.setrlimit(kind, (limit, limit))
sys.path.insert(0, "/app")
runpy.run_path(entry, run_name="__main__")
