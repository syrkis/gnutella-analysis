# metrics.py
#   plotter class for gnutella analysis
# by: Noah Syrkis

"""
general purpose gnutella plotting
"""

# imports
import networkx as nx
from construct import S
from collections import Counter
from centrality import centrality
from matplotlib import pyplot as plt
from tqdm import tqdm
from attacker import Attack
import os
import json


# class
class Metric:

    def __init__(self, G, data={}):
        self.G = G
        self.name = G.name
        self.data = data

    def build(self):
        self.__setup(self.G)

    def save(self):
        json_data = json.dumps(self.data, indent=4)
        with open(f'../data/dumps/{self.name}.json', 'w') as json_file:
            json_file.write(json_data)

    def attack(self):
        A = Attack(self.G)
        ps = [0.05 * i for i in range(0,20)]
        rs, ds, es, pagerank = [], [], [], []
        for p in ps:
            r = A.random(p)
            d = A.degrees(p)
            e = A.eigen(p)
            pa = A.pagerank(p)
            rs.append(self.__connectivity(r))
            ds.append(self.__connectivity(d))
            es.append(self.__connectivity(e))
            pagerank.append(self.__connectivity(pa))
        plt.plot(ps, rs, 'b', label='random')
        plt.plot(ps, ds, 'r', label='degree')
        plt.plot(ps, es, 'g', label='eigenv')
        plt.plot(ps, pagerank, 'y', label='pagerank')
        plt.xlabel('fraction attacked'); plt.ylabel('frac. of nodes in largest comp.')
        plt.legend(); plt.title(f"attack plot of {self.G.name}"); plt.show()

    def __connectivity(self, G):
        L = self.__component(G)
        return len(L.nodes) / len(G.nodes)

    def __component(self, G):
        components = sorted(nx.strongly_connected_components(G), key=len)[::-1]
        L = G.subgraph(components[0])
        return L

    def __setup(self, G):
        # degree distribution
        G_degs = self.__degfreq(G)
        self.data['degs'] = {'in': G_degs[0], 'out': G_degs[1],
                             'ccdf_in': G_degs[2], 'ccdf_out': G_degs[3]}
        # centrality measures, clustering, knn
        self.data['centrality'] = centrality(G)
        self.data['clustering'] = self.__clustering(G)
        knn = nx.k_nearest_neighbors(G)
        self.data['knn'] = [list(knn.keys()), list(knn.values())]

        # configuration metrics
        C = self.__config(G)
        knn = nx.k_nearest_neighbors(C)
        self.data['C'] = {'centrality': centrality(C),
                          'clustering': self.__clustering(C),
                          'knn': [list(knn.keys()), list(knn.values())]}


    def __degfreq(self, G):
        in_freq = Counter(dict(G.in_degree).values())
        in_x = list(in_freq.keys())
        in_y = list(in_freq.values())
        out_freq = Counter(dict(G.out_degree).values())
        out_x = list(out_freq.keys())
        out_y = list(out_freq.values())
        ins = list(dict(G.in_degree).values())      # ccdf setup
        outs = list(dict(G.out_degree).values())    # ccdf setup
        in_ccdf_x, in_ccdf_y = self.__ccdf(ins)
        out_ccdf_x, out_ccdf_y = self.__ccdf(outs)
        return [in_x, in_y], [out_x, out_y], [in_ccdf_x, in_ccdf_y], [out_ccdf_x, out_ccdf_y]

    def __ccdf(self, degs):
        n, x, _ = plt.hist(degs, density=True, cumulative=True, bins=100); plt.close()
        x = 0.5 * (x[1:] + x[:-1])
        y = [1 - v for v in n]
        return [list(x), list(y)]


    def __clustering(self, G):
        if G.is_multigraph():
            G = nx.DiGraph(G)
        cluster = Counter(dict(nx.clustering(G)).values())
        x = list(cluster.keys())
        y = list(cluster.values())
        return x, y

    def __config(self, G):
        d_in = [G.in_degree[node] for node in G.nodes]
        d_out = [G.out_degree[node] for node in G.nodes]
        return nx.directed_configuration_model(d_in, d_out)


# script
def main():
    construct = False        # if True we reconstruct the graph analysis data.
    for G in tqdm(S.values()):
        if not construct and f"{G.name}.json" in os.listdir('../data/dumps/'):
            with open(f"../data/dumps/{G.name}.json", 'r') as data_file:
                data = json.load(data_file)
            D = Metric(G, data=data)
            D.attack()
        else:               # read graph analysis data from file
            D = Metric(G)
            D.build()
            D.save()


if __name__ == "__main__":
    main()
