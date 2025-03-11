import pyaig
import array
import argparse

def evaluate(path):
    stats = {}
    aig = pyaig.read_aiger(path)
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
    return stats

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str)
    args = parser.parse_args()
    print(evaluate(args.path))

