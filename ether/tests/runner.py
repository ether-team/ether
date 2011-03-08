"""Python unittests together with python code coverage."""

import unittest, os, coverage, fnmatch


def locate(pattern, root=os.curdir):
    """Find all the files according to the search pattern in a directory.

    :param pattern: pattern to match. To find all python sources use *.py
    :type pattern: string
    :param root: directory where to perform the search
    :type root: string
    :returns: iterator through the absolute file names
    """
    for path, _, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)


def load_module(module_name):
    """Loads the module by string name.

    :param module_name: string name of the module
    :returns: python module
    """
    return __import__(module_name, globals(), locals(), [""])


class TestsNotRunError(BaseException):
    """If the report is accessed before the tests were run."""

    def __str__(self):
        return "Test cases were not executed. You didn't call the 'run' method."


class DummyTestCase(unittest.TestCase):
    """A test case that provides an easy way to mock the modules."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(DummyTestCase, self).__init__(*args, **kwargs)
        self.originals = {}

    def mock(self, module_imported, original, dummy):
        """Mocks the module.

        :param module_imported: module where the substitution has to occur
        :param original: string name of the module to substitute
        :param dummy: a module that is supposed to take place of the original
        """
        if not self.originals.has_key(module_imported):
            self.originals[module_imported] = {}
        if not self.originals[module_imported].has_key(original):
            self.originals[module_imported][original] = \
                    getattr(module_imported, original)
        setattr(module_imported, original, dummy)

    def unmock(self):
        """Unmocks the modules. Sets everything to initial condition."""
        for module_imported, originals in self.originals.iteritems():
            for original_name, module in originals.iteritems():
                setattr(module_imported, original_name, module)
        self.originals = {}

    def tearDown(self):
        """Unmocks the modules."""
        self.unmock()


class TestRunner(object):
    """Class for executing testcases with coverage."""

    def __init__(self, project_directory, test_modules, ignored_modules=None):
        """Constructor.

        :param ignored_modules: list of string module names to ignore e.g.
            ["module.abs.dfg"]
        :param testcases: a list of testcase classes
        :param ignored_modules: list of string module names to ignore e.g.
            ["module.abs.dfg.tests"]
        """

        self._project_directory = project_directory
        self._test_modules = test_modules
        if not ignored_modules:
            ignored_modules = []
        self._ignored_modules = ignored_modules
        self._executed = False

    @property
    def _suite(self):
        """Creates a testsuite out of a list of testcase classes."""
        suites = []
        for test_module in self._test_modules:
            module = load_module(test_module)
            for item in dir(module):
                if item.startswith("Test"):
                    case = getattr(module, item)
                    suites.append(
                        unittest.TestLoader().loadTestsFromTestCase(case))
        return unittest.TestSuite(suites)

    @property
    def _coverable_modules(self):
        """Returns a list of modules to check via testcoverage."""
        modules = []
        for tdir in locate("*.py", self._project_directory):
            to_ignore = False
            tdir = tdir.replace(os.path.dirname(self._project_directory), "")
            if tdir.startswith(os.path.sep):
                tdir = tdir[1:].replace(".py", "")
            module_name = tdir.replace(os.path.sep, ".")
            for ignored_module in self._ignored_modules:
                if module_name.find(ignored_module) >= 0:
                    to_ignore = True
                    break
            if not to_ignore:
                module = load_module(module_name)
                modules.append(module)
        return modules

    @property
    def report(self):
        """Returns a dictioanry as a report about the execution."""
        if not self._executed:
            raise TestsNotRunError()
        raise NotImplementedError

    def run(self):
        """Runs unittests with coverage."""
        coverage.start()
        unittest.TextTestRunner(verbosity=1).run(self._suite)
        coverage.stop()
        coverage.report(self._coverable_modules)
        coverage.erase()
        self._executed = True


def run(project_directory, test_modules, ignored_modules=None):
    """Short way to instanciate the TestRunner and call the "run" method."""
    TestRunner(project_directory, test_modules, ignored_modules).run()
