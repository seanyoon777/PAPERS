import numpy as np
import statistics as stats
from scipy.stats import norm

LARGE_VARIANCE = 100    # Arbitrary large variance when there is only one observation

def probGreaterThan(params1, params2): 
    mu1, sigma1 = params1
    mu2, sigma2 = params2
    samples1 = norm.rvs(mu1, sigma1, size = 10000)
    samples2 = norm.rvs(mu2, sigma2, size = 10000)
    return (samples1 > samples2).mean()

def add_noise(observations, noise_stddev = 0.01):     # Add artificial noise to prevent all observations having var = 0
    noise = np.random.normal(0, noise_stddev, len(observations))
    return observations + noise

def sampleSummary(pi_list): 
    n = len(pi_list)
    if n == 1: 
        mu_samples = pi_list[0]
        var_samples = LARGE_VARIANCE
    else: 
        mu_samples = np.mean(pi_list)
        var_samples = stats.variance(pi_list)
    return mu_samples, var_samples, n

def updateGaussianPrior(pi_dict, params, curr_period, name, regularization_term = 1): 
    pi_list = pi_dict[curr_period][name]
    pi_list = add_noise(pi_list)
    mu_prior, var_prior = params[curr_period][name]
    mu_samples, var_samples, n = sampleSummary(pi_list)
    tau_prior = 1 / var_prior
    tau_data = 1 / var_samples
        
    mu_post = (tau_prior * mu_prior + n * tau_data * mu_samples) / (tau_prior + n * tau_data)
    var_post = max(1 / (tau_prior + n * tau_data), regularization_term)
    params[curr_period][name] = (mu_post, var_post)
