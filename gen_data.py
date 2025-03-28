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

def gen_data():
    apath = os.path.join('results', gen_data.tag)
    data = []
    def traverse(path = '', index = gen_data.index):
        path = os.path.join(path, index['name'])
        cpath = os.path.join(apath, path)
        for name in index['files']:
            basename, _ = os.path.splitext(name)
            cpath = os.path.join(apath, path, basename)
            with contextlib.chdir(cpath):
                if os.path.exists('time.txt'):
                    with open('time.txt') as f:
                        elapsed_time = f.readline()
                    stats = evaluate.evaluate()
                    stats['time'] = elapsed_time
                    stats['path'] = os.path.join(path, basename)
                    data.append(stats)
        for subindex in index['dirs']:
            traverse(path=path, index=subindex)
    traverse()
    df = pandas.DataFrame(data).set_index('path').sort_index()
    df.to_csv(os.path.join(apath, 'data.csv'))
gen_data.index = {}
gen_data.tag = None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tag', type=str, required=True)
    args = parser.parse_args()
    with open('index.json', 'r') as f:
        gen_data.index = json.load(f)
    gen_data.tag = args.tag
    gen_data()
    
