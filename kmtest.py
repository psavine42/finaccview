import kmapper as km
from sklearn import datasets
import argparse
import test1 as ts


def random(args):
    data, labels = datasets.make_circles(n_samples=5000, noise=0.03, factor=0.3)

    # Initialize
    mapper = km.KeplerMapper(verbose=1)

    # Fit to and transform the data
    projected_data = mapper.fit_transform(data, projection=[0, 1]) # X-Y axis

    # Create dictionary called 'graph' with nodes, edges and meta-information
    graph = mapper.map(projected_data, data, nr_cubes=10)

    # Visualize it
    mapper.visualize(graph, path_html="out/{}.html".format(args.action),
                     title="make_circles(n_samples=5000, noise=0.03, factor=0.3)")





if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('-a', '--action', type=str, default='r')
    args = p.parse_args()
    if args.action == 'r':
        random(args)



