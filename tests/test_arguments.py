"""Product argument errors preserve help and avoid echoing private values."""
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import unittest

from mindtunnel.cli import main
from mindtunnel_planner.cli import main as planner_main
from mindtunnel_isolation.linux import main as isolated_main


class ArgumentPrivacy(unittest.TestCase):
    def test_argument_errors_are_generic(self):
        cases = [(main,['--unknown','SYNTHETIC_ARGUMENT_CANARY']),
                 (main,['run','--data','SYNTHETIC_PATH_CANARY']),
                 (planner_main,['approve','--ttl','SYNTHETIC_ARGUMENT_CANARY']),
                 (isolated_main,['--unknown','SYNTHETIC_ARGUMENT_CANARY'])]
        for entry, arguments in cases:
            with self.subTest(entry=entry.__module__):
                stdout, stderr = StringIO(), StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as exit:
                        entry(arguments)
                self.assertEqual(exit.exception.code,2)
                self.assertEqual(stdout.getvalue(),'')
                self.assertEqual(stderr.getvalue(),'Rejected: invalid_arguments\n')

    def test_help_remains_available(self):
        for entry in [main,planner_main,isolated_main]:
            with self.subTest(entry=entry.__module__):
                stdout = StringIO()
                with redirect_stdout(stdout), self.assertRaises(SystemExit) as exit:
                    entry(['--help'])
                self.assertEqual(exit.exception.code,0)
                self.assertIn('usage:',stdout.getvalue())
        stdout = StringIO()
        with redirect_stdout(stdout), self.assertRaises(SystemExit):
            main(['--help'])
        self.assertIn('Print public request for owner review',stdout.getvalue())
        stdout = StringIO()
        with redirect_stdout(stdout), self.assertRaises(SystemExit):
            main(['request','--help'])
        self.assertIn('Print the public request for owner review before manual transfer.',stdout.getvalue())
