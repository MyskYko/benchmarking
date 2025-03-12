import os
import shutil
import pandas

def fix_data(path = 'results'):
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_dir():
                fpath = os.path.join(entry.path, 'data.csv')
                if os.path.isfile(fpath):
                    df = pandas.read_csv(fpath, index_col=0)
                    if 'name' not in df.columns:
                        print('skipping', entry.name)
                        continue
                    df['path'] = df['path'] + '/' + df['name']
                    df.set_index('path', inplace=True)
                    df.sort_index(inplace=True)
                    df.drop('name', axis=1, inplace=True)
                    shutil.copy(fpath, os.path.join(entry.path, 'data.csv.old'))
                    df.to_csv(fpath)

if __name__ == '__main__':
    fix_data()
