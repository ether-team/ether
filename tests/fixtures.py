# Data for testing git hook

all_branchs = """\
refs/heads/master
refs/heads/test
"""

not_commits = "^0db3f7da89cfb8ef301c1f4a5cb1d8cfcad13684"

ataginfo = """\
Some One|<some.one@example.com>|Sat Feb 19 14:27:55 2011 +0200|changelog updated
"""

revlistinfo = """\
commit 9442f7cdd33e93e7cf0add43bd9bc4be1bfbdb72
Some One|<some.one@example.com>|Thu Mar 3 16:21:11 2011 +0200|Commit 1

commit ee43557cdc68039e13bdddb3dd270028334eb5a1
Some One|<some.one@example.com>|Thu Mar 3 14:21:46 2011 +0200|Commit 2"""

githook_payload = {
    'commits': [],
    'after': '68f7abf4e6f922807889f52bc043ecd31b79f814',
    'ref': 'refs/heads/master',
    'repository': {
        'url': 'ssh://git@some.site.org/git/',
        'owner': {
            'email': '',
            'name': ''},
        'name': '',
        'description': ''},
    'before': 'aa453216d1b3e49e7f6f98441fa56946ddcd6a20'}

# Data for testing svn hook

svnhook_payload = {
    'data': {},
    'payload': {
        'commits': [
            {'added': [],
             'author': {
                 'name': ['ed\n'],
                 'email': ''},
             'timestamp': ['2011-02-10 11:33:32 +0200 (Thu, 10 Feb 2011)\n'],
             'modified': ['test'],
             'message': ['commit 20\n'],
             'removed': [],
             'id': '/var/svn/repo'}], 
        'repository': {
            'url': 'https://some.site.org/svn/',
            'owner': '',
            'name': ''}}}
