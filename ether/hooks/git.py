#!/usr/bin/env python -tt

import os, re, sys
from datetime import datetime

"""GIT hooks APIs."""


EMAIL_RE = re.compile("^(.*) <(.*)>$")


def _get_revlist(old, new):
    """This method was moved out of the GitHook class to simplify testing.

    Executes "git rev-list"

    :param old: old commit hashsum
    :type old: string
    :param new: newer commit hashsum
    :type new: string
    :returns: command output
    """
    with os.popen("git rev-list --pretty=medium %s..%s" % (old, new), "r") as handler:
        return handler.read()


def _get_terminal_input():
    """This method was moved out of the GitHook class to simplify testing.

    :returns: a tuple of three strings:
        - the old commit hashsum
        - newer commit hashsum
        - reference (e.g. refs/heads/master"
    """
    return (sys.argv[1], sys.argv[2], sys.argv[3])


class GitHook(object):

    def __init__(self, sender):
        """Constructor.

        :param sender: a class that is supposed to send the message
            has to implement 'send_payload' method
        """
        self._sender = sender
        self.old, self.new, self.ref = _get_terminal_input()

    @property
    def commits(self):
        """
        Property that holds a dictionary of a format:
            {"id": "commit hashsum",
             "author": "commit author",
             "message": "commit message",
             "timestamp": "timestamp in github format"}
        """
        if not hasattr(self, "__commits"):
            revlist = _get_revlist(self.old, self.new)
            sections = revlist.split('\n\n')[:-1]
            self.__commits = []
            index = 0
            while index < len(sections):
                lines = sections[index].split('\n')

                # first line is 'commit HASH\n'
                props = {'id': lines[0].strip().split(' ')[1]}

                # read the header
                for line in lines[1:]:
                    key, val = line.split(' ', 1)
                    props[key[:-1].lower()] = val.strip()

                # read the commit message
                props['message'] = sections[index+1]

                # use github time format
                basetime = datetime.strptime(props['date'][:-6], "%a %b %d %H:%M:%S %Y")
                tzstr = props['date'][-5:]
                props['date'] = basetime.strftime('%Y-%m-%dT%H:%M:%S') + tzstr

                # split up author
                author = EMAIL_RE.match(props['author'])
                if author:
                    props['name'] = author.group(1)
                    props['email'] = author.group(2)
                else:
                    props['name'] = 'unknown'
                    props['email'] = 'unknown'
                del props['author']

                # increment the counter
                index += 2

                self.__commits.append({
                    'id': props['id'],
                    'author': {'name': props['name'], 'email': props['email']},
                    'message': props['message'].strip(),
                    'timestamp': props['date']
                })
        return self.__commits

    def postreceive(self):
        """Postcommit hook."""
        self._sender.send_payload({
            "before": self.old,
            "after": self.new,
            "ref": self.ref,
            "repository": {
                "url": "",
                "name": "",
                "description": "",
                "owner": {
                    "email": "",
                    "name": ""
                }
            },
            "commits": self.commits,
        })
