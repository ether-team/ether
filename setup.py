import os, sys

from distutils.core import setup
from setuptools import find_packages

from ether import VERSION_STR

MINIMAL_COVERAGE = 90 # percents

class TestExecutionFailure(Exception):
    pass


class CoverageFailure(Exception):
    pass


if len(sys.argv) > 1:
    if sys.argv[1] == "test":
        from ether import runtests
        results, coverage_percents = runtests.run()
        if results.errors or results.failures:
            n_failures = (len(results.errors) + len(results.failures))
            desc = "test was"
            if n_failures > 1:
                desc += "tests were"
            raise TestExecutionFailure(
                "%d %s not passed successfully." % \
                    (n_failures, desc))
        if coverage_percents < MINIMAL_COVERAGE:
            raise CoverageFailure(
                "Code coverage is %d%%, is has to be at least %d%%" % \
                    (coverage_percents, MINIMAL_COVERAGE))


setup(
    name="ether",
    version=VERSION_STR,
    url='https://github.com/ether-team/ether',
    author='BIFH & OBS teams',
    author_email='bifh-team@nokia.com',
    packages=find_packages(),
    data_files=[
        ('share/vcs-hooks/svn', ['hooks/svn/ether-post-commit']),
        ('share/vcs-hooks/git', ['hooks/git/ether-post-receive']),
    ],
    scripts = ['examples/test_consumer', 'examples/test_publisher'],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
