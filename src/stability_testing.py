from sklearn.preprocessing import StandardScaler
import pandas as pd
from sklearn.ensemble import IsolationForest
from scipy.spatial.distance import pdist, squareform
from itertools import combinations
import numpy as np



def jaccard_peturbation_contamination( X, contaminations, K, feature_set, seed_N):

    N = len(contaminations)
    

    seeds = [i for i in range(seed_N)]
    means = []

    for seed in seeds:
        sets = []
        sim = np.eye(N)
        for contamination in contaminations:
            scores = run_iso(X,seed,feature_set, contamination)
            scores = pd.Series(scores, index=X.index)
            

            n_top = max(1, int(len(scores) * K))

            top_samples = scores.nsmallest(n_top)
            sets.append( set(X.loc[top_samples.index, "buyer"].values ))
            
        for i, j in combinations(range(N), 2):
            val = jaccard(sets[i], sets[j])
            sim[i, j] = sim[j, i] = val
        mean = sim[np.triu_indices_from(sim, k=1)].mean()
        print(sim)
        means.append(mean)
    print(np.array(means).mean())

def jaccard_peturbation_seed( X, N, feature_set, K):
    # K = 0.005

    seeds =  [i for i in range(N)]

    # key=k -> (sets index seed ->top k set)
    sets = {k: [] for k in K}

    sims = {k: np.eye(N) for k in K}

    for seed in seeds:
        # most expensive opperation
        scores = run_iso(X, seed, feature_set)
        scores = pd.Series(scores, index=X.index)
        
        for k in K:
            
            n_top = max(1, int(len(scores) * k))
            # IMPORTANT: the scikit learn library considers the lowest score to be more anomolous
            top_samples = scores.nsmallest(n_top)
            sets[k].append( set(X.loc[top_samples.index, "buyer"].values ))

    means = []
    vars = []
    for k in K:
        for i, j in combinations(range(N), 2):
            val = jaccard(sets[k][i], sets[k][j])
            sims[k][i, j] = sims[k][j, i] = val
        mean = sims[k][np.triu_indices_from(sims[k], k=1)].mean()
        means.append(mean)
        var = sims[k][np.triu_indices_from(sims[k], k=1)].var()
        vars.append(var)
    return means, sims, vars
    
        
        
    



def run_iso(X, random_state, feature_set, contamination = 0.005):

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X[feature_set])

    iso = IsolationForest(
        n_estimators=300,
        max_samples=2048,
        contamination=contamination,
        random_state=random_state
    )

    iso.fit(X_scaled)

    return iso.decision_function(X_scaled)


def jaccard(a, b):
    return len(a & b) / len(a | b) if a or b else 0.0




# jaccard_peturbation_contamination(X, [0.0025, 0.005, 0.01, 0.02],0.005,[
#             "avg_time_distance",
#             "delta_volume",
#             "delta_frequency",
#             "missing_delta"], 5)

def complete_seed_testing(sample_path, features, N):
    X = pd.read_csv(sample_path)


    # stability[feature][run]
    stability =[]
    means = []
    K = [0.0025,0.005,0.01,0.02,0.05]


        # most expensive opperation
    means, _, vars = jaccard_peturbation_seed(X, N, features, K)
        
        
    
    return [0.0025,0.005,0.01,0.02,0.05], means, vars


def statistical_seed_testing(sample_path, features, N):
    X = pd.read_csv(sample_path)


    # stability[feature][run]
    stability =[]
    
    K =[0.0025,0.005,0.01,0.02,0.05]


    # most expensive opperation 
    _, jaccard_matrices, _ = jaccard_peturbation_seed(X, N, features, K)
    
        
        # sf,i​(k)=1/19j!=i∑​Jaccard(topk​(Rf,i​),topk​(Rf,j​))
        # stability = 1/(N-1)(jaccard_matrices[K][i].sum()-jaccard_matrices[K][i, i])
    stability = {}
    for k, J in jaccard_matrices.items():
        stability[k] = (J.sum(axis=1) - np.diag(J)) / (N - 1)
        
    S = np.vstack([stability[k] for k in K])
    
    
    den = K[-1] - K[0]
    # the AUC for each seed run
    AUCs = np.trapezoid(S, x=K, axis=0) / den

    # essentially a sepperate statistic normalizing for k values
    return AUCs
            
        
        
    
    return 0
def normalized_auc(k_vals, stability_vals):
    return np.trapz(stability_vals, x=k_vals) / (k_vals[-1] - k_vals[0])