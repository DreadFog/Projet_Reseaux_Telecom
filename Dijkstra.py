def Dijkstra(G, s, lci = lambda x,y: x+y):
    dist = [float('Inf')]*len(G)
    pred = [-9999]*len(G)
    passage = [False]*len(G)

    passage[s] = True
    dist[s] = 0
    pred[s] = s
    Q = list()
    S = list()
    Q.append(s)
    while len(Q) != 0:
        u = min(Q)
        Q.pop(Q.index(u))
        S.append(u)
        adjV = [indvoisin for indvoisin in range(len(G[u])) if G[u][indvoisin] != 0]
        for v in adjV:
            if lci(G[u][v], dist[u]) < dist[v]:
                dist[v] = lci(G[u][v], dist[u])
                pred[v] = u
                if not(passage[v]):
                    passage[v] = True
                    Q.append(v)
    return (dist, pred)
