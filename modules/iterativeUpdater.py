import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gamma
from scipy.special import gamma as gamma_distribution
from scipy.integrate import quad

GAMMA_PRIOR = (10, 10)

def initializeParams(curr_matches, params, curr_names, curr_period, prev_period): 
    if prev_period is None: 
        params[curr_period] = {name: GAMMA_PRIOR for name in curr_names}
    else: 
        for name in curr_names: 
            if name not in params[prev_period].keys(): 
                params[curr_period][name] = GAMMA_PRIOR
            else: 
                params[curr_period][name] = params[prev_period][name]
    
def probGreaterThan(params1, params2): 
    a1, b1 = params1
    a2, b2 = params2
    samples1 = gamma.rvs(a1, scale = 1 / b1, size = 10000)
    samples2 = gamma.rvs(a2, scale = 1 / b2, size = 10000)
    return (samples1 > samples2).mean()
        
def getW(score1, score2): 
    if score1 == score2: 
        return 0.5
    return score1 > score2

def performanceIndicator(score1, score2, params1, params2): 
    W = getW(score1, score2)
    P = probGreaterThan(params1, params2)
    R = score1 / (score1 + score2)
    pi1 = W * P + R
    pi2 = (1 - W) * (1 - P) + (1 - R)
    return (pi1, pi2)
    
def performanceIndicatorDict(curr_matches, match_data, prev_params, curr_names, pi_dict, curr_period): 
    pi_dict[curr_period] = {name: [] for name in curr_names}
    for match in curr_matches: 
        _, name1, name2 = match
        score1, score2 = match_data[match]
        
        if name1 not in prev_params.keys(): 
            params1 = GAMMA_PRIOR
        else: 
            params1 = prev_params[name1]
            
        if name2 not in prev_params.keys(): 
            params2 = GAMMA_PRIOR
        else: 
            params2 = prev_params[name2]
            
        pi1, pi2 = performanceIndicator(score1, score2, params1, params2)
        
        pi_dict[curr_period][name1].append(pi1)
        pi_dict[curr_period][name2].append(pi2)

def getAllNames(curr_matches): 
    return set(match[1] for match in curr_matches) | set(match[2] for match in curr_matches)

def updateGammaPrior(pi_dict, params, curr_period, name): 
    pi_list = pi_dict[curr_period][name]
    n = len(pi_list)
    a, b = params[curr_period][name]
    a_n = a + n
    b_n = b + sum(pi_list)
    params[curr_period][name] = (a_n, b_n)
    
def updateObservations(pi_dict, curr_matches, match_data, params, curr_names, curr_period, prev_period): 
    initializeParams(curr_matches, params, curr_names, curr_period, prev_period)
    if prev_period == None: 
        performanceIndicatorDict(curr_matches, match_data, params[curr_period], curr_names, pi_dict, curr_period)
    else: 
        performanceIndicatorDict(curr_matches, match_data, params[prev_period], curr_names, pi_dict, curr_period)
    for name in curr_names: 
        updateGammaPrior(pi_dict, params, curr_period, name)

def printOutputs(curr_params, curr_names, type, curr_period): 
    x = np.linspace(0, 10, 1000)
    num_plots = len(curr_params.keys())
    num_rows = -(-num_plots // 5)
    fig, axes = plt.subplots(nrows=num_rows, ncols=5, figsize=(10, 2 * num_rows))
    
    for i, name in enumerate(curr_names): 
        row = i // 5
        col = i % 5
        a, b = curr_params[name]
        y = gamma.pdf(x, a, scale=1 / b)
        axes[row, col].plot(x, y)
        axes[row, col].set_title(name)
        
    for i in range(num_plots, num_rows * 5):
        row = i // 5
        col = i % 5
        axes[row, col].axis('off')
    
    if type == 'OP': 
        fig.suptitle(f'Observation, Year {curr_period}', fontsize=16)
    if type == 'NOP': 
        fig.suptitle(f'Non-observation, Year {curr_period}', fontsize=16)
        
    plt.tight_layout()
    plt.show()
    
# def updateNonObservations(params, curr_names): 
#     for name in curr_names: 


def bestPerformance(params, athlete_data): 
    final_dict = {name: -np.inf for name in athlete_data.keys()}
    for name in athlete_data.keys(): 
        for period in athlete_data[name].keys(): 
            a, b = params[period][name]
            result = a / b
            if result > final_dict[name]: 
                final_dict[name] = result
    final_dict = dict(sorted(final_dict.items(), key = lambda item: -item[1]))
    return final_dict
    
def PAPERS(period_data, match_data, athlete_data, verbose = False): 
    params = {period: {} for period in sorted(period_data.keys())}
    prev_period = None
    pi_dict = {}
    for curr_period in sorted(period_data.keys()): 
        curr_matches = period_data[curr_period]
        curr_names = getAllNames(curr_matches)
        updateObservations(pi_dict, curr_matches, match_data, params, curr_names, curr_period, prev_period)
        if verbose: 
            printOutputs(params[curr_period], curr_names, 'Observation Period', curr_period)
        #updateNonObservations()
        #if verbose: 
        #    printOutputs(params[curr_period], curr_names, 'Non-observation Period', curr_period)
        prev_period = curr_period
    final_dict = bestPerformance(params, athlete_data)
    return final_dict, params