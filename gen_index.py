import os
import json

def gen_index(path = 'benchmarks'):
    data = {}
    data['name'] = os.path.basename(path)
    data['files'] = []
    data['dirs'] = []
    with os.scandir(path) as it:
        for entry in it:
            if entry.name.startswith('.'):
                continue
            basename, _ = os.path.splitext(entry.path)
            if basename in gen_index.exclude:
                continue
            if entry.is_dir():
                data['dirs'].append(gen_index(entry.path))
            elif entry.name.endswith(gen_index.extension):
                data['files'].append(entry.name)
    return data
gen_index.extension = ''
gen_index.exclude = set()

if __name__ == '__main__':
    with open('settings.json', 'r') as f:
        settings = json.load(f)
        gen_index.extension = settings['extension']
        for exclude in settings['benchmarks']['exclude']:
            gen_index.exclude.add(os.path.normpath(os.path.join('benchmarks', exclude)))
    data = gen_index()
    json_object = json.dumps(data, indent=1)
    with open('index.json', 'w') as f:
        f.write(json_object)

