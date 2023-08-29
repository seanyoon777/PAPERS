import math
import numpy as np
import modules.reporter as reporter
import modules.paperStats as pstats
import matplotlib.pyplot as plt

PRIOR = (1., 10.)     # mean, variance
h = 0.05              # Exponential confidence decay factor over time
d = 0.1
MAX_OBSERVATION = 2

def modifyGaussianPrior(prior): 
    global PRIOR
    PRIOR = prior
    
def initializeParams(params, all_names, curr_period, prev_period): 
    '''
    Initializes the parameters for each athlete's performance function. Brings last data if 
    present, or initializes with default prior. 
    '''
    params[curr_period] = {name: PRIOR for name in all_names}
    if prev_period is not None: 
        for name in all_names: 
            if name in params[prev_period].keys(): 
                params[curr_period][name] = params[prev_period][name]
        
def getW(score1, score2): 
    if score1 == score2: 
        return 0.5
    return score1 > score2

def updateNums(match_nums, name1, name2): 
    match_nums[name1] += 1
    match_nums[name2] += 1
    
def performanceIndicator(score1, score2, params1, params2): 
    '''
    Calculates performance indicator for given match. 
    '''
    W = getW(score1, score2)
    P1 = params2[0]
    P2 = params1[0]
    R = score1 / (score1 + score2)
    pi1 = W * P1 + R
    pi2 = (1 - W) * P2 + (1 - R)
    return (pi1, pi2)
    
def performanceIndicatorDict(curr_matches, match_data, match_nums, prev_params, curr_names, pi_dict, curr_period): 
    '''
    Generates a dictionary of current observation period mapped to a dictionary of athlete names 
    mapped to performance indicators during that observation period. 
    '''
    pi_dict[curr_period] = {name: [] for name in curr_names}
    for match in curr_matches: 
        _, name1, name2 = match
        score1, score2 = match_data[match]
        params1 = PRIOR
        params2 = PRIOR
        
        if name1 in prev_params.keys(): 
            params1 = prev_params[name1]
        if name2 in prev_params.keys(): 
            params2 = prev_params[name2]
            
        pi1, pi2 = performanceIndicator(score1, score2, params1, params2)
        updateNums(match_nums, name1, name2)
        
        pi_dict[curr_period][name1].append(pi1)
        pi_dict[curr_period][name2].append(pi2)

def getAllNames(curr_matches): 
    return set(match[1] for match in curr_matches) | set(match[2] for match in curr_matches)
    
def updateObservations(pi_dict, curr_matches, match_data, match_nums, params, curr_names, curr_period, prev_period): 
    '''
    Generates performance indicators for given observation period, and updates the performance functions for each
    athlete. 
    '''
    if prev_period == None: 
        performanceIndicatorDict(curr_matches, match_data, match_nums, params[curr_period], curr_names, pi_dict, curr_period)
    else: 
        performanceIndicatorDict(curr_matches, match_data, match_nums, params[prev_period], curr_names, pi_dict, curr_period)
    for name in curr_names: 
        pstats.updateGaussianPrior(pi_dict, params, curr_period, name)

# Values of k, c should be empirically determined. 
def updateUncertaintyMu(mu_old, n, k = 2, c = 2): 
    obs_uncertainty = k / np.sqrt(n**2 + c**2)
    return mu_old - (MAX_OBSERVATION - mu_old) * obs_uncertainty * math.exp(h) * d

def updateUncertaintyVar(var_old, n, k = 2, c = 1): 
    obs_uncertainty = 1 + k / np.sqrt(n**2 + c**2)
    return var_old * obs_uncertainty * math.exp(h)
    
def updateNonObservations(params, pi_dict, match_nums, all_names, curr_period, prev_period): 
    '''
    Updates performance functions for given non-observation period. Mean is linearly decayed, while variance
    is exponentially decayed. 
    '''
    if prev_period == None: 
        return
    for name in all_names:
        if name not in pi_dict[curr_period]: 
            mu_old, var_old = params[prev_period][name]
        else: 
            mu_old, var_old = params[curr_period][name] 
        mu_new = updateUncertaintyMu(mu_old, match_nums[name])
        var_new = updateUncertaintyVar(var_old, match_nums[name])
        params[curr_period][name] = (mu_new, var_new)

def avgPerformanceDict(params, athlete_data, all_periods): 
    '''
    Generates dictionary of each athlete mapped to an average performance indicator for each observation period. 
    Also generates dictionary of each athlete mapped to an average performance indicator across all observation
    periods. 
    '''
    averages_dict = {name: [] for name in athlete_data.keys()}
    for name in athlete_data.keys(): 
        for period in all_periods: 
            if name in params[period].keys(): 
                mu, _ = params[period][name]
                averages_dict[name].append(mu)
    total_averages_dict = {}
    for name in averages_dict.keys(): 
        total_averages_dict[name] = np.mean(averages_dict[name])
    total_averages_dict = dict(sorted(total_averages_dict.items(), key = lambda item: -item[1]))
    return total_averages_dict, averages_dict
    
def PAPERS(period_data, match_data, athlete_data, modifyPrior = None, verbose = False): 
    '''
    PAPERS - probabilistically initializes and updates the performance functions for each athlete. 
    '''
    if modifyPrior is not None: 
        modifyGaussianPrior(modifyPrior)        
    all_periods = sorted(period_data.keys())
    params = {period: {} for period in all_periods}
    match_nums = {name: 0 for name in athlete_data.keys()}
    prev_period = None
    pi_dict = {}
    all_names = set()
    for curr_period in all_periods: 
        curr_matches = period_data[curr_period]
        curr_names = getAllNames(curr_matches)
        all_names.update(curr_names)
        initializeParams(params, all_names, curr_period, prev_period)
        updateObservations(pi_dict, curr_matches, match_data, match_nums, params, curr_names, curr_period, prev_period)
        if verbose: 
            fig, axes = reporter.printOutputs(params[curr_period], curr_names, 'Observation Period', curr_period)
            plt.show()
        updateNonObservations(params, pi_dict, match_nums, all_names, curr_period, prev_period)
        prev_period = curr_period
    total_averages_dict, averages_dict = avgPerformanceDict(params, athlete_data, all_periods)
    return total_averages_dict, averages_dict, params
