import os, sys, tempfile

import nose, coverage

from distutils.core import setup
from setuptools import find_packages

from ether import VERSION_STR

MINIMAL_COVERAGE = 90 # percents


if len(sys.argv) > 1:
    if sys.argv[1] == "build":
        out = sys.stderr
        sys.stderr = tempfile.TemporaryFile()
        result = nose.run(module="ether",
                          defaultTest="tests.tests",
                          argv=[sys.argv[0]])
        sys.stderr.seek(0)
        data = sys.stderr.read()
        sys.stderr = out
        percentage = 0
        for line in data.split("\n"):
            if line.find("TOTAL") >= 0:
                percentage = int(line.split()[3].strip().replace("%", ""))
        print data # Print the results as usually
        if not result:
            print "****************"
            print "Testing failure."
            print "****************"
            sys.exit(1)
        if percentage < MINIMAL_COVERAGE:
            print "****************"
            print "Code coverage is %d%%. It has to be at least %d%%." % \
                    (percentage, MINIMAL_COVERAGE)
            print "****************"
            sys.exit(1)


setup(
    setup_requires=['nose>=0.11.1'],
    test_suite = 'nose.collector',
    name="ether",
    version=VERSION_STR,
    url='https://github.com/ether-team/ether',
    author='BIFH & OBS teams',
    author_email='bifh-team@nokia.com',
    packages=find_packages(),
    data_files=[
        ('share/vcs-hooks/', ['hooks/root_hook.sh']),
        ('share/vcs-hooks/svn', ['hooks/svn/ether-post-commit']),
        ('share/vcs-hooks/git', ['hooks/git/ether-post-receive']),
        ('/etc/ether', [
            'configs/basic.conf', 'configs/common.conf',
            'configs/git_postreceive.conf', 'configs/github.conf',
            'configs/svn_postcommit.conf', 'configs/test_consumer.conf',
            'configs/test_publisher.conf']
         )
    ],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)

setup(
    setup_requires=['nose>=0.11.1'],
    test_suite = 'nose.collector',
    name="ether-hookman",
    version=VERSION_STR,
    url='https://github.com/ether-team/ether',
    author='BIFH & OBS teams',
    author_email='bifh-team@nokia.com',
    packages=["ether.hooks"],
    data_files=[
        ('share/ether/hookman/', ['hooks/root_hook.sh']),
        ('share/ether/hookman/svn', ['hooks/svn/ether-post-commit']),
        ('share/ether/hookman/git', ['hooks/git/ether-post-receive']),
    ],
    entry_points={
        "console_scripts": ["hookman = ether.hookman.hookman:main"],
        "ether.hookman": ["svn = ether.hookman.svn:SvnHookAPI",
                          "git = ether.hookman.git:GitHookAPI"]
                          #"hg = ether.hookman.hg:HgHookAPI"
    },
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
