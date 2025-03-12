import os
import pandas
import numpy

def create_table(path = 'results'):
    df_list = []
    names = []
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_dir():
                fpath = os.path.join(entry.path, 'data.csv')
                if os.path.isfile(fpath):
                    df = pandas.read_csv(fpath, index_col='path')
                    df_list.append(df)
                    names.append(entry.name)
    df = pandas.concat(df_list, axis=1, keys=names).swaplevel(0, 1, axis=1).sort_index(axis=1)
    if create_table.use_name:
        index_list = df.index.to_list()
        index_list = [os.path.split(index)[1] for index in index_list]
        df.index = index_list
        df.index.name = 'name'
    if create_table.add_gmean:
        gmeans = {}
        for col in df.columns:
            gmeans[col] = numpy.exp(numpy.log(df[col]).mean())
        gmean_df = pandas.DataFrame([gmeans], index=['gmean']).round(2).map(lambda x: '{0:.2f}'.format(x))
        df = pandas.concat([df, gmean_df])
    pandas.set_option('display.max_rows', None)
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.max_colwidth', None)
    print(df['size'])
create_table.use_name = True
create_table.add_gmean = True

if __name__ == '__main__':
    create_table()
