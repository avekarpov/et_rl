from os import listdir
from os.path import isfile, join


def list_dir(path):
    return [join(path, f) for f in listdir(path) if isfile(join(path, f))]

def list_dir_regex(path, regex):
    return [f for f in list_dir(path) if regex.match(f)]