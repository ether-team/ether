from distutils.core import setup
from setuptools import find_packages

from ether import VERSION_STR

setup(
    name="ether",
    version=VERSION_STR,
    url='https://github.com/ether-team/ether',
    author='BIFH & OBS teams',
    author_email='bifh-team@nokia.com',
    packages=find_packages(exclude=['ez_setup']),
    data_files=[('share/vcs-hooks/svn', ['hooks/svn/ether-post-commit']),
                ('share/vcs-hooks/git', ['hooks/git/ether-post-receive'])],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
