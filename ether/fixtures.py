def mock_get_revlist(old, new):
    return """commit e3b0f9c9a0945b0efa9a9295b24cf6108a6f97bb
Author: Anton Berezin <anton.berezin@nokia.com>
Date:   Wed Mar 2 14:13:14 2011 +0200

    C1

commit ad45a931e70e62bde1f3f03e34c27613c85d07d8
Author: Anton Berezin <anton.berezin@nokia.com>
Date:   Wed Mar 2 14:11:14 2011 +0200

    Took Ed's comments converning not modifying the code to ease the tests.

commit 0161cca7fec8a4b5c9ca9fccf7a393a32222da99
Author: Anton Berezin <anton.berezin@nokia.com>
Date:   Wed Mar 2 11:58:45 2011 +0200

     * Simplified GitHook logic
     * Documented the code
     * Made GitHook code easy to test

"""

git_postreceive_expected_output = {
  'commits': [
  { 'timestamp': '2011-03-02T14:13:14+0200',
    'message': 'C1',
    'id': 'e3b0f9c9a0945b0efa9a9295b24cf6108a6f97bb',
    'author': {'name': 'Anton Berezin', 'email': 'anton.berezin@nokia.com'}},
  { 'timestamp': '2011-03-02T14:11:14+0200',
    'message': "Took Ed's comments converning not modifying the code to ease the tests.",
    'id': 'ad45a931e70e62bde1f3f03e34c27613c85d07d8',
    'author': {'name': 'Anton Berezin', 'email': 'anton.berezin@nokia.com'}},
  { 'timestamp': '2011-03-02T11:58:45+0200',
    'message': '* Simplified GitHook logic\n     * Documented the code\n     * Made GitHook code easy to test',
    'id': '0161cca7fec8a4b5c9ca9fccf7a393a32222da99',
    'author': {'name': 'Anton Berezin', 'email': 'anton.berezin@nokia.com'}}
  ],
  'after': 'e3b0f9c9a0945b0efa9a9295b24cf6108a6f97bb',
  'ref': 'refs/head/master',
  'repository': {
      'url': '',
      'owner': {'email': '', 'name': ''},
      'name': '',
      'description': ''
      },
  'before': '0161cca7fec8a4b5c9ca9fccf7a393a32222da99'
  }

def mock_svnlook(what, repos, rev):
    data = {
        "changed": "U   test\n",
        "log": "commit 20\n",
        "author": "ed\n",
        "date": "2011-02-10 11:33:32 +0200 (Thu, 10 Feb 2011)\n"
    }
    return [data[what]]

svn_postcommit_expected_output = {
  'commits': [{
    'added': [],
    'author': {'name': ['ed\n'], 'email': ''},
    'timestamp': ['2011-02-10 11:33:32 +0200 (Thu, 10 Feb 2011)\n'],
    'modified': ['test'],
    'message': ['commit 20\n'],
    'removed': [],
    'id': '/var/svn/repo'}]}
