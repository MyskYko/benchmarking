import argparse
import os
import pandas
import numpy
import json
import re

def create_table(path = 'results'):
    df_list = []
    names = []
    with os.scandir(path) as it:
        for entry in it:
            if entry.name in create_table.exclude:
                continue
            if entry.is_dir():
                fpath = os.path.join(entry.path, 'data.csv')
                if os.path.isfile(fpath):
                    df = pandas.read_csv(fpath, index_col='path')
                    df_list.append(df)
                    names.append(entry.name)
    df = pandas.concat(df_list, axis=1, keys=names)
    if df.isna().any().any(): # sort if na is there
        df.sort_index(inplace = True)
    if create_table.tags:
        tags = []
        for tag in create_table.tags:
            if '*' in tag:
                r = re.compile(tag)
                keys = list(filter(r.match, df.columns.levels[0]))
                tags += keys
            else:
                tags.append(tag)
        df = df[tags]
        print(len(tags))
        print(tags)
    df = df.swaplevel(0, 1, axis=1)
    #df.sort_index(axis=1, inplace=True)
    #print(df)
    df.drop(index=[item for item in create_table.benchmarks_exclude if item in df.index], inplace=True)
    if create_table.use_name: # otherwise it's path
        index_list = df.index.to_list()
        index_list = [os.path.split(index)[1] for index in index_list]
        df.index = index_list
        df.index.name = 'name'
    if create_table.get_stats:
        df2 = pandas.DataFrame()
        #add min mean stddiv
        for key in df.columns.levels[0]:
            df2[(key, 'min')] = df[key].min(axis=1)
            df2[(key, 'mean')] = df[key].mean(axis=1)
            df2[(key, 'max')] = df[key].max(axis=1)
            df2[(key, 'std')] = df[key].std(axis=1)
            df2[(key, 'low')] = df2[(key, 'mean')] - 1.645 * df2[(key, 'std')]
        df2.sort_index(axis=1, inplace=True)
        df2.columns = pandas.MultiIndex.from_tuples(df2.columns)
        gmeans = {}
        for col in df2.columns:
            gmeans[col] = numpy.exp(numpy.log(df2[col]).mean())
        gmean_df = pandas.DataFrame([gmeans], index=['gmean']).map(lambda x: '{0:.1f}'.format(x))
        df2 = df2.swaplevel(0, 1, axis=1)
        for metric in ['min', 'max']:
            df2[metric] = df2[metric].map(lambda x: '{0:.0f}'.format(x))
        for metric in ['mean', 'std', 'low']:
            df2[metric] = df2[metric].map(lambda x: '{0:.1f}'.format(x))
        df2 = df2.swaplevel(0, 1, axis=1)
        df2 = pandas.concat([df2, gmean_df])
        print(df2['size'])
        print(df2['time'])
        print(df2)
    if create_table.add_gmean:
        gmeans = {}
        for col in df.columns:
            gmeans[col] = numpy.exp(numpy.log(df[col]).mean())
        gmean_df = pandas.DataFrame([gmeans], index=['gmean']).map(lambda x: '{0:.1f}'.format(x))
        for metric in create_table.integer_metrics:
            if metric in df:
                df[metric] = df[metric].map(lambda x: '{0:.0f}'.format(x))
        df = pandas.concat([df, gmean_df])
    else:
        for metric in create_table.integer_metrics:
            df[metric] = df[metric].map(lambda x: '{0:.0f}'.format(x))
    pandas.set_option('display.max_rows', None)
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.max_colwidth', None)
    pandas.set_option('display.width', None)
    #print(df.columns.levels[0])
    #print(df['size'])
    #print(df['time'].astype(float).map(lambda x: '{0:.4f}'.format(x)))
    #print(df)
    #print(pandas.concat([df['size'], df['time'].astype(float).map(lambda x: '{0:.1f}'.format(x))], keys=['size', 'time'], axis=1))
    #print(pandas.concat([df['size'], df['time'].astype(float).map(lambda x: '{0:.1f}'.format(x)), df['iteration']], keys=['size', 'time', 'iteration'], axis=1))
create_table.benchmarks_exclude = []
create_table.integer_metrics = []
create_table.use_name = True
create_table.add_gmean = True
create_table.get_stats = True
create_table.tags = []
create_table.exclude = []

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tags', nargs='+')
    parser.add_argument('-e', '--exclude', nargs='+')
    args = parser.parse_args()
    with open('settings.json', 'r') as f:
        settings = json.load(f)
        create_table.benchmarks_exclude = [os.path.join('benchmarks', item) for item in settings['benchmarks']['exclude']]
        create_table.integer_metrics = settings['integer_metrics']
    if args.tags:
        create_table.tags = args.tags
    if args.exclude:
        create_table.exclude = args.exclude
    create_table()
