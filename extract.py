import os
import shutil
import argparse
import contextlib

def extract():
    dpath = os.path.abspath(extract.tag)
    if not os.path.exists(dpath):
        os.mkdir(dpath)
    def traverse(path = '.'):
        spath = os.path.join(dpath, path)
        if not os.path.exists(spath):
            os.mkdir(spath)
        with os.scandir(path) as it:
            for entry in it:
                if entry.name.startswith('.'):
                    continue
                if entry.is_file():
                    continue
                epath = os.path.join(entry.path, 'out.aig')
                if os.path.exists(epath):
                    name = entry.name + '.aig'
                    fpath = os.path.join(spath, name)
                    shutil.copy(epath, fpath)
                else:
                    traverse(entry.path)
    with contextlib.chdir(os.path.join('results', extract.tag, 'benchmarks')):
        traverse()
extract.tag = None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tag', type=str, required=True)
    args = parser.parse_args()
    extract.tag = args.tag
    extract()

