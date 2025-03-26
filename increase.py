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

def increase():
    apath = os.path.join('results', increase.tag)
    if not os.path.exists(apath):
        print('Error: tag', increase.tag, 'does not exist')
        sys.exit(1)
    with open(os.path.join(apath, 'command.txt'), 'r') as f:
        command = f.readline().strip()
        print(command)
    bpath = os.path.abspath('.')
    def run(inpath):
        print(inpath)
        try:
            start = time.time()
            result = subprocess.run(' '.join([command, inpath]), shell=True, capture_output=True, text=True, check=True)
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
    data = []
    def traverse(path = '', index = increase.index):
        path = os.path.join(path, index['name'])
        cpath = os.path.join(apath, path)
        if not os.path.exists(cpath):
            os.mkdir(cpath)
        for name in index['files']:
            basename, _ = os.path.splitext(name)
            cpath = os.path.join(apath, path, basename)
            if os.path.exists(cpath):
                continue
            os.mkdir(cpath)
            with contextlib.chdir(cpath):
                inpath = os.path.join(bpath, path, name)
                stats = run(inpath)
                stats['path'] = os.path.join(path, basename)
                data.append(stats)
        for subindex in index['dirs']:
            traverse(path=path, index=subindex)
    traverse()
    if not data:
        print('everything is already added')
        return
    dpath = os.path.join(apath, 'data.csv')
    df1 = pandas.read_csv(dpath, index_col='path')
    df2 = pandas.DataFrame(data).set_index('path')
    df = pandas.concat([df1, df2]).sort_index()
    df.to_csv(dpath)
increase.index = {}
increase.tag = None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tag', type=str, required=True)
    args = parser.parse_args()
    with open('index.json', 'r') as f:
        increase.index = json.load(f)
    increase.tag = args.tag
    increase()
    
