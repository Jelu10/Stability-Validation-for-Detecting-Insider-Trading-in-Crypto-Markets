import pandas as pd
import ast

def scc(link_path):
    df = pd.read_csv(link_path)
    df = df.set_index("a")
    df["linked_buyers"] = df["linked_buyers"].apply(ast.literal_eval)

    # linked wallets, list of wallets that were transfered coins (that also bought during the prelisting window)

    # for v in df.index:
    #     for w in df.loc[v,"linked_buyers"]:
    #         print(w)
    #     break

    # exit()

    # tarjans algorithm
    index = 0
    stack = []
    on_stack = set()
    indices = {}
    lowlink = {}
    sccs = []

    def strongconnect(v):
        nonlocal index
        indices[v] = index
        lowlink[v] = index
        index += 1

        stack.append(v)
        on_stack.add(v)
        
        # vertice (wallet) can not be in the list if it has zero addresses it sent to
        if(v in df.index):
            for w in df.loc[v,"linked_buyers"]:
                if w not in indices:
                    strongconnect(w)
                    lowlink[v] = min(lowlink[v], lowlink[w])
                elif w in on_stack:
                    lowlink[v] = min(lowlink[v], indices[w])

        # If v is the root of an SCC
        if lowlink[v] == indices[v]:
            scc = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                scc.append(w)
                if w == v:
                    break
            sccs.append(scc)

    # main
    for v in df.index:
        if v not in indices:
            strongconnect(v)

    return sccs

# end


# print(df.head(10))
