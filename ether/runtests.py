#!/usr/bin/python


def run():
    """Project wide testrunner."""
    import os, sys
    DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(DIRECTORY))
    from ether.tests import runner
    return runner.run(DIRECTORY, ["ether.tests.tests"],
                      ["ether.configs", "__init__", "tests"])


if __name__ == "__main__":
    run()
