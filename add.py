import os
import shutil
import sys
import time
import subprocess
import contextlib
import datetime
import argparse
import json
import pandas

def add():
    identifier = datetime.datetime.now().strftime('%Y%m%d%H%M%S_%f')
    apath = os.path.join('results', identifier)
    os.mkdir(apath)
    rpath = os.path.join(apath, 'command.txt')
    with open(rpath, 'w') as f:
        f.write(' '.join(add.command))
    with open(os.path.join('results', 'tag.csv'), 'a') as f:
        f.write(','.join([identifier, add.tag]))
        f.write('\n')
    bpath = os.path.abspath('.')
    def run(inpath):
        print(inpath)
        try:
            start = time.time()
            result = subprocess.run(' '.join(add.command + [inpath]), shell=True, capture_output=True, text=True, check=True)
            elapsed_time = time.time() - start
            with open('stdout.txt', 'w') as f:
                f.write(result.stdout)
            with open('stderr.txt', 'w') as f:
                f.write(result.stderr)
            with open('time.txt', 'w') as f:
                f.write(str(elapsed_time))
        except subprocess.CalledProcessError as e:
            print('Error: command failed with exit code', e.returncode)
            print('stdout:', e.stdout)
            print('stderr:', e.stderr)
            with open('stdout.txt', 'w') as f:
                f.write(e.stdout)
            with open('stderr.txt', 'w') as f:
                f.write(e.stderr)
            sys.exit(1)
    if add.test:
        cpath = os.path.join(apath, 'test')
        os.mkdir(cpath)
        with contextlib.chdir(cpath):
            inpath = os.path.join(bpath, add.test)
            run(inpath)
    def traverse(path = '', index = add.index):
        path = os.path.join(path, index['name'])
        cpath = os.path.join(apath, path)
        os.mkdir(cpath)
        for name in index['files']:
            basename, _ = os.path.splitext(name)
            cpath = os.path.join(apath, path, basename)
            os.mkdir(cpath)
            with contextlib.chdir(cpath):
                inpath = os.path.join(bpath, path, name)
                run(inpath)
        for subindex in index['dirs']:
            traverse(path=path, index=subindex)
    traverse()
add.test = None
add.index = {}
add.command = []
add.tag = None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str)
    parser.add_argument('-t', '--tag', type=str, required=True)
    with open('settings.json', 'r') as f:
        settings = json.load(f)
        add.test = settings['test']
    with open('index.json', 'r') as f:
        add.index = json.load(f)
    args = parser.parse_args()
    if args.command.startswith('.'):
        commands = args.command.split()
        add.command = [os.path.abspath(commands[0])] + commands[1:]
    else:
        add.command = [args.command]
    add.tag = args.tag
    try:
        df = pandas.read_csv(os.path.join('results', 'tag.csv'), names=['id', 'key'], index_col='key')
        if add.tag in df.index:
            print('Error: tag', add.tag, 'already exists')
            sys.exit(1)
    except FileNotFoundError:
        pass
    except pandas.errors.EmptyDataError:
        pass
    add()
    
