import pathlib


def assertIsFile(path):
    if not pathlib.Path(path).resolve().is_file():
        raise AssertionError("File does not exist: %s" % str(path))
