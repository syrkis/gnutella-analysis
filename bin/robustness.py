# robustness.py
#   simulates attacks of the gnutella network
# by: Noah Syrkis

# imports
import random
import networkx as nx
from operator import itemgetter


class Robustness(object):
    """
    Class is initiated with graph. It precalculates betweenness centrality and finds largest component.
    Below are various methods of testing network robustness.
    """
    def __init__(self, graph):
        self.graph = graph
        self.L = self.__component(graph)
        self.B = self.__betweenness()

    def random(self, p):
        """
        removes a p-th of the nodes randomly and returns subgraph
        """
        G = self.L
        nodes = random.sample(G.nodes, int(float(len(G.nodes)) * (1-p)))
        S = nx.subgraph(G, nodes)
        return S

    def degrees(self, p):
        """
        Removes a p-th of the nodes by degree and returns subgraph
        """
        G = self.L
        degs = sorted(G.degree, key=itemgetter(1))[::-1]
        nodes = [entry[0] for entry in degs][int(len(degs) * p):]
        S = nx.subgraph(G, nodes)
        return S

    def betweenness(self, p):
        """
        Removes a p-th of the nodes by betweenness centrality and returns subgraph
        """
        G = self.L
        out = self.B
        nodes = [(k, v) for k, v in out.items()]
        nodes = sorted(nodes, key=itemgetter(1))[::-1]
        nodes = [entry[0] for entry in nodes][int(len(nodes) * p):]
        S = nx.subgraph(G, nodes)
        return S

    def __component(self, G):
        """
        Takes in graph and returns largest strongly connected component
        """
        components = sorted(nx.strongly_connected_components(G), key=len)[::-1]
        L = G.subgraph(components[0])
        return L

    def __betweenness(self):
        """
        for pre-computing betweenness centrality scores so as to not recompute for every p
        """
        G = self.L
        return nx.betweenness_centrality(G)


def main():
    from construct import S
    G = list(S.values())[-2]
    robustness = Robustness(G)
    #attack.random(0.1)
    S = robustness.closeness(0.1)
    print(nx.info(S))


if __name__ == "__main__":
    main()
