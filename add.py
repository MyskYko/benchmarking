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

import evaluate

def add():
    apath = os.path.join('results', add.tag)
    if os.path.exists(apath):
        print('Error: tag', add.tag, 'already exists')
        sys.exit(1)
    os.mkdir(apath)
    with open(os.path.join(apath, 'command.txt'), 'w') as f:
        f.write(' '.join(add.command))
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
            stats = evaluate.evaluate()
            stats['time'] = elapsed_time
            return stats
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
    data = []
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
                stats = run(inpath)
                stats['path'] = path
                stats['name'] = basename
                data.append(stats)
        for subindex in index['dirs']:
            traverse(path=path, index=subindex)
    traverse()
    df = pandas.DataFrame(data)
    df.to_csv(os.path.join(apath, 'data.csv'))
add.test = None
add.index = {}
add.command = []
add.tag = None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str)
    parser.add_argument('-t', '--tag', type=str, required=True)
    args = parser.parse_args()
    with open('settings.json', 'r') as f:
        settings = json.load(f)
        add.test = settings['test']
    with open('index.json', 'r') as f:
        add.index = json.load(f)
    if args.command.startswith('.'):
        commands = args.command.split()
        add.command = [os.path.abspath(commands[0])] + commands[1:]
    else:
        add.command = [args.command]
    add.tag = args.tag
    add()
    
