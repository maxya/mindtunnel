"""CLI argument errors never echo owner-supplied paths or values."""
import argparse


class LocalArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, 'Rejected: invalid_arguments\n')
