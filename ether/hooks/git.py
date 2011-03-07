#!/usr/bin/env python -tt

"""GIT hooks APIs.

Loosely modelled after the excellent contrib hook
/usr/share/doc/git/contrib/hooks/post-receive-email
"""

import os, re
from datetime import datetime



#EMAIL_RE = re.compile("^(.*) <(.*)>$")
ALLZEROS_RE = re.compile("0+$")


def _parse_revinfo(revinfo):
    """Parses two lines of rev info

    :param revinfo: two lines describing a rev
    :type revinfo: string
    :returns: {}
    """
    commit_part , info_part = revinfo.split("\n")
    rev = commit_part.split(" ")[1]
    author, email, date, message = info_part.split("|")

    #basetime = datetime.strptime(date[:-6],"%a %b %d %H:%M:%S %Y")
    #tzstr = date[-5:]
    #date = basetime.strftime('%Y-%m-%dT%H:%M:%S') + tzstr

    return {
               'id': rev,
               'message' : message,
               'date' : date,
               'name' : author,
               'email' : email
           }


def _get_revlistinfo(rev):
    """Executes "git rev-list" with rev

    :param old: old commit hashsum
    :type old: string
    :param new: newer commit hashsum
    :type new: string
    :returns: command output
    """
    with os.popen("git rev-list --pretty=format:'%%an|%%ae|%%ad|%%s%%n' %s"\
            % (rev), "r") as handler:
        return handler.read()


def _get_revtype(rev):
    """Executes "git cat-file -t" with a rev

    :param rev: commit hashsum
    :type rev: string
    :returns: command output
    """
    with os.popen("git cat-file -t %s" % (rev), "r") \
            as handler:
        return handler.read()


def _get_types(old, new, ref):
    """
    :param old: old commit hashsum
    :type old: string
    :param new: newer commit hashsum
    :type new: string
    :param ref: ref name
    :type ref: string
    :returns: change_type, ref_type 
    """
    change_type = ref_type = None

    if ALLZEROS_RE.match(old):
        change_type = "create"
        rev_type = _get_revtype(new).strip()
    elif ALLZEROS_RE.match(new):
        change_type = "delete"
        rev_type = _get_revtype(old).strip()
    else:
        change_type = "update"
        rev_type = _get_revtype(new).strip()

    if rev_type == "tag" and ref.startswith("refs/tags/"):
        ref_type = "annotated tag"
    elif rev_type == "commit":
        if ref.startswith("refs/tags/"):
            ref_type = "unannotated tag"
        elif ref.startswith("refs/heads/"):
            ref_type = "branch"
        else:
            ref_type = "unknown"

    return change_type, ref_type


def _get_ataginfo(ref):
    """
    :param ref: ref name
    :type ref: string
    :returns: string
    """
    fmt = "'%(*authorname)|%(*authoremail)|%(*authordate)|%(*subject)'"
    with os.popen("git for-each-ref --format=%s %s" % \
            (fmt, ref), "r") as handler:
        return handler.read()


def _parse_ataginfo(ref):
    """
    :param ref: ref name
    :type ref: string
    :returns: {
               'id' : tag name,
               'message' : message,
               'date' : date,
               'name' : author,
               'email' : email
              }
    """
    author, email, date, message = _get_ataginfo(ref).split("|")
    tagname = ref.replace("refs/tags/", "")

    return {
               'id' : tagname,
               'message' : message,
               'date' : date,
               'name' : author,
               'email' : email
           }


def _gen_commit(change_type, ref_type, props):
    """
    :param change_type: create, delete or update
    :type change_type: string
    :param ref_type: branch, annotated tag, unannotated tag
    :type ref_type: string
    :param props: dict of properties as returned by _parse_ataginfo or 
    :type ref: dictionary
    :returns:
        {
          "id": "commit hashsum",
          "operation": "update, create, delete",
          "ref_type": "annotated tag, unannotated tag, branch, unknown"
          "author": "commit author",
          "message": "commit message",
          "timestamp": "timestamp in github format"
        }
    """
    return {
               'id': props['id'],
               'operation' : change_type,
               'ref_type' : ref_type,
               'author': {
                             'name': props['name'], 
                             'email': props['email']
                         },
               'message': props['message'].strip(),
               'timestamp': props['date']
            }


def _get_allbranches():
    """
    :returns: string
    """
    with os.popen("git for-each-ref --format='%(refname)' refs/heads/", \
                  "r") as handler:
        return handler.read()


def _get_notcommits(other_branches):
    """
    :param ref: branch names
    :type ref: string
    :returns: string
    """
    with os.popen("git rev-parse --not %s" % (other_branches), \
                  "r") as handler:
        return handler.read()


class GitHook(object):
    """GIT hook."""

    def __init__(self, sender):
        """Constructor.

        :param sender: a class that is supposed to send the message
            has to implement 'send_payload' method
        """
        self._sender = sender

    @staticmethod
    def _get_commits(old, new, ref):
        """
        :param old: old commit hashsum
        :type old: string
        :param new: newer commit hashsum
        :type new: string
        :param ref: ref name
        :type ref: string
        :returns:
            [{
              "id": "commit hashsum",
              "operation": "update, create, delete",
              "ref_type": "annotated tag, unannotated tag, branch, unknown"
              "author": "commit author",
              "message": "commit message",
              "timestamp": "timestamp in github format"
            }]
        """
        commits = []

        change_type, ref_type = _get_types(old, new, ref)

        if not change_type or not ref_type:
            return commits

        if ref_type == "annotated tag":
            # Annotated tags have their own info
            if change_type == "delete":
                # we care only which tag was deleted and when
                props = {
                    'id' : ref.replace("refs/tags/", ""),
                    'message' : '',
                    'date' : datetime.now().strftime('%a %b %d %H:%M:%S %Y'),
                    'name' : '',
                    'email' : ''
                }
            else:
                # we want a little more info about tag create and update
                props = _parse_ataginfo(ref)

            commits.append(_gen_commit(change_type, ref_type, props))

        elif ref_type == "unannotated tag":
            return commits

        elif ref_type == "branch":
            if change_type == "delete":
                # we care only which branch was deleted and when
                props = {
                    'id' : ref.replace("refs/heads/", ""),
                    'message' : '',
                    'date' : datetime.now().strftime('%a %b %d %H:%M:%S %Y'),
                    'name' : '',
                    'email' : ''
                }
                commits.append(_gen_commit(change_type, ref_type, props))
                return commits

            elif change_type == "update":
                # branch updates can contain multiple commits
                revlistinfo = _get_revlistinfo("%s..%s" %  \
                                               (old, new)).split("\n\n")

            elif change_type == "create":
                # branch creates can contain multiple commits as well
                # but we need to find the commits that are in this branch only
                other_branches = _get_allbranches().split("\n")
                other_branches.remove(ref)
                not_commits = _get_notcommits(" ".join(other_branches))
                revlistinfo = _get_revlistinfo("%s %s" %  \
                                               (new, not_commits)).split("\n\n")

            for revinfo in revlistinfo:
                if revinfo.strip() != "":
                    props = _parse_revinfo(revinfo)
                    commits.append(_gen_commit(change_type, ref_type, 
                                               props))

        return commits

    def postreceive(self, commits):
        """Postcommit hook."""
        # Get command line arguments
        for commit in commits:
            old, new, ref = commit

        # Send the payload
            self._sender.send_payload({
                "before": old,
                "after": new,
                "ref": ref,
                "repository": {
                    "url": "",
                    "name": "",
                    "description": "",
                    "owner": {
                        "email": "",
                        "name": ""
                    }
                },
                "commits": self._get_commits(old, new, ref),
            })
