import os
import array
import argparse
import pyaig

def evaluate(path = ''):
    stats = {}
    aig = pyaig.read_aiger(os.path.join(path, 'out.aig'))
    stats['size'] = aig.n_ands()
    def get_level():
        a = array.array('i', (-1 for _ in range(len(aig))))
        for i, n in enumerate(aig._nodes):
            if n.is_and():
                l = a[n.get_left() >> 1]
                r = a[n.get_right() >> 1]
                assert l >= 0 and r >= 0
                a[i] = max(l, r) + 1
            elif n.is_pi():
                a[i] = 0
        return max(a)
    stats['level'] = get_level()
    with open(os.path.join(path, 'stdout.txt')) as f:
        for line in f:
            if line.startswith('#'):
                words = line[1:].split(':')
                stats[words[0].strip()] = words[1].strip()
    return stats

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str)
    args = parser.parse_args()
    print(evaluate(args.path))

