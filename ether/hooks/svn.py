#!/usr/bin/env python -tt

"""SVN hooks APIs."""

import os, sys

class SvnHookError(Exception):
    """Custom exception."""
    pass

def _svnlook(what, repos, rev):
    """Wrapper around svnlook tool."""

    with os.popen("svnlook %s -r %s %s" % \
                  (what, rev, repos), "r") as handler:
        return handler.readlines()

def get_repo_url(paths, config):
    """
    Get svn repo url from the list of paths.
    :param paths: list of changed paths
    :ptype paths: list
    :param config: configuration object which maps repository paths to urls
    :ptype config: list of tuples (<path>, <url>)
    :returns: repository url
    :rtype: string
    """

    result = None
    for path in paths:
        for upath, url in config:
            if path.startswith(upath):
                # check if we previously got the same url
                if result and result != url:
                    raise SvnHookError("get_repo_url got 2 different results: "
                                        "%s and %s" % (result, url))
                if not result:
                    result = url
                break
    if not result:
        raise SvnHookError("get_repo_url: Can't get repo url")
    return result

class SvnHook:
    """SVN hooks API. Gets hook data, creates hook payload
       and calls sender.send_payload.
    """

    def __init__(self, sender, config):
        self._sender = sender
        self._config = config

    def _get_commits(self, repos, rev):
        # collect the info
        changed = _svnlook("changed", repos, rev)
        log = _svnlook("log", repos, rev)
        author = _svnlook("author", repos, rev)
        date = _svnlook("date", repos, rev)

        # prepare hook payload in the github payload format
        changes = {"A": [], "U": [], "D": []}
        for line in changed:
            oper, path = line.split()
            # Used oper[0] to work with 'UU' operation
            if oper[0] in changes:
                changes[oper[0]].append(path)

        url = get_repo_url(changes["A"] + changes["U"] + changes["D"],
                           self._config)

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
            "data": {},
            "payload": {
                "repository": {
                    "name": "",
                    "url": url,
                    "owner": ""
                    },
                "commits": commits
            }
        })

