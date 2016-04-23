import collections
import itertools

class Tree:
    def __init__(self, root, branches=()):
        self.root = root
        self.branches = list(branches)

    def __repr__(self):
        if not self.branches:
            return 'Tree({!r})'.format(self.root)
        else:
            return 'Tree({!r}, {!r})'.format(self.root, self.branches)

    def postorder(self):
        for b in self.branches:
            yield from b.postorder()
        yield self.root

class Graph:
    def __init__(self, edges=()):
        self.G = collections.defaultdict(set)
        for u, v in edges:
            self.G[u].add(v)

    def __repr__(self):
        return 'Graph({!r})'.format(list(self.edges()))

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
        """Return a list of connected components of the graph. Each conencted
        component is a list of vertices.
        """
        return [list(t.postorder()) for t in self.spanning_forest()]

    def linearize(self):
        """Return a list of vertices in a topological order. The first vertex
        will have no incoming edges, and the last vertix will have no outgoing
        edges.
        """
        for t in self.spanning_forest():
            yield from reversed(tuple(t.postorder()))

    def reachable(self, u, v):
        """Return True iff there is a directed path from u to v."""
        return any(w == v for w in self.spanning_tree(u).postorder())

    def acyclic(self):
        """Return True iff the graph is acyclic."""
        post = {v: i for i, v in enumerate(self.linearize())}
        return all(post[u] < post[v] for u, v in self.edges())

    def sccs(self):
        """Return a list of strongly connected components of the graph. Each
        strongly connected component is a list of vertices.
        """
        return [list(t.postorder())
            for t in self.transpose().spanning_forest(self.linearize())]

    def condensation(self):
        """Return directed acyclic graph. The vertices of the returned graph
        are strongly connected components of the original graph (as sets of
        vertices). The edges of the new graph are the edges of the new graph
        as if all of the strongly connected components are "condensed" into a
        single vertex.
        """
        contract = {}
        for scc in self.sccs():
            S = frozenset(scc)
            for v in S:
                contract[v] = S
        return Graph((contract[u], contract[v])
            for u, v in self.edges() if contract[u] != contract[v])

    def shortest_path(self, s, t, weight=lambda e: 1):
        """Return the shortest path from s to t, as a list of vertices starting
        with s and ending with t. If there is no path, return None.

        The weight parameter is a function that takes an edge and returns the
        length of that edge. One way to do this is with a dictionary:

        edges = []
        weights = {}
        for u, v, weight in weighted_edges:
            e = (u, v)
            edges.append(e)
            weights[e] = w
        g = Graph(edges)
        g.shortest_path(start, end, lambda e: weights[e])
        """
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
test_graph = Graph([
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
