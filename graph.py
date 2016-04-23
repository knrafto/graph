import collections
import itertools

class Tree:
    def __init__(self, root, branches=()):
        self.root = root
        self.branches = branches

    def postorder(self):
        for b in self.branches:
            yield from b.postorder()
        yield self.root

class Graph:
    def __init__(self, edges=()):
        self.G = collections.defaultdict(set)
        for u, v in edges:
            self.G[u].add(v)

    def vertices(self):
        return self.G.keys()

    def neighbors(self, v):
        return self.G[v]

    def outdegree(self, v):
        return len(self.neighbors(v))

    def indegree(self, v):
        return self.transpose().outdegree(v)

    def edges(self):
        for u in self.G:
            for v in self.G[u]:
                yield (u, v)

    def transpose(self):
        return Graph((v, u) for u, v in self.edges())

    def union(self, other):
        return Graph(itertools.chain(self.edges(), other.edges()))

    def undirected(self):
        return self.union(self.transpose())

    def spanning_tree(self, v, visited=None):
        if visited is None:
            visited = set()
        visited.add(v)
        return Tree(v, self.spanning_forest(self.neighbors(v), visited))

    def spanning_forest(self, vertices=None, visited=None):
        if vertices is None:
            vertices = self.vertices()
        if visited is None:
            visited = set()
        for v in vertices:
            if v not in visited:
                yield self.spanning_tree(v, visited)

    def ccs(self):
        return (t.postorder() for t in self.spanning_forest()):

    def linearize(self):
        for t in self.spanning_forest():
            yield from reversed(tuple(t.postorder()))

    def reachable(self, u, v):
        return any(w == v for w in self.spanning_tree(u).postorder())

    def acyclic(self):
        post = {v: i for i, v in enumerate(self.linearize())}
        return all(post[u] < post[v] for u, v in self.edges())

    def sccs(self):
        return (t.postorder()
            for t in self.transpose().spanning_forest(self.linearize()))

    def condensation(self):
        contract = {}
        for scc in self.sccs():
            S = frozenset(scc)
            for v in S:
                contract[v] = S
        return Graph((contract[u], contract[v])
            for u, v in self.edges() if contract[u] != contract[v])

    def shortest_path(self, s, t, weight=lambda e: 1):
        dist = {s: 0}
        prev = {s: None}
        Q = {s}
        while Q:
            u = min(Q, key=dist.get)
            Q.remove(u)
            if u == t:
                break
            for v in self.neighbors(u):
                alt = dist[u] + weight((u, v))
                if v not in dist or alt < dist[v]:
                    Q.add(v)
                    dist[v] = alt
                    prev[v] = u
        if t not in prev:
            return None
        path = []
        while t is not None:
            path.append(t)
            t = prev[t]
        return reversed(path)

# from http://en.wikipedia.org/wiki/Strongly_connected_component
g = Graph([
    ('a', 'b'),
    ('b', 'e'),
    ('e', 'a'),
    ('b', 'f'),
    ('e', 'f'),
    ('f', 'g'),
    ('g', 'f'),
    ('b', 'c'),
    ('c', 'd'),
    ('d', 'c'),
    ('d', 'h'),
    ('h', 'd'),
    ('c', 'g'),
    ('h', 'g')
])
