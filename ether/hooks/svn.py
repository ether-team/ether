#!/usr/bin/env python -tt

"""SVN hooks APIs."""

import os
from ether.hooks import get_repo_url


def _svnlook(what, repos, rev, exe="svnlook"):
    """Wrapper around svnlook tool."""

    with os.popen("%s %s -r %s %s" % \
                  (exe, what, rev, repos), "r") as handler:
        return handler.readlines()


class SvnHook:
    """SVN hooks API. Gets hook data, creates hook payload
       and calls sender.send_payload.
    """

    def __init__(self, sender, config):
        self._sender = sender
        self._config = config

    def _get_commits(self, repos, rev):
        """Get commit info from svn revision using svnlook."""

        # collect the info
        changed = _svnlook("changed", repos, rev)
        log = _svnlook("log", repos, rev)
        author = _svnlook("author", repos, rev)
        date = _svnlook("date", repos, rev)

        # prepare hook payload in the github payload format
        changes = {"A": [], "U": [], "D": []}
        paths = []
        for line in changed:
            oper, path = line.split()
            # Used oper[0] to work with 'UU' operation
            if oper[0] in changes:
                changes[oper[0]].append(path)
                paths.append(os.path.join(repos, path))

        url = get_repo_url(paths, self._config)

        return url, [{
            "author": {"name": author, "email": ""},
            "id": rev,
            "added": changes["A"],
            "modified": changes["U"],
            "removed": changes["D"],
            "message": log,
            "timestamp": date
        }]

    def postcommit(self, repos, rev):
        """Postcommit hook."""

        url, commits = self._get_commits(repos, rev)

        self._sender.send_payload({
            "repository": {
                "name": "",
                "url": url,
                "owner": ""
            },
            "commits": commits
        })
