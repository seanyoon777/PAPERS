# PAPERS: Probabilistic Athlete Performance Evaluation & Ranking Software


## Introduction and Motivation
The motivation behind creating this software was mostly to rank individual fencers based on their performance. Why fencing? Well, first of all, the 2024 Paris olympics are coming up, and they plan to hold the fencing matches in this beautiful stadium. How could we not talk about fencing? 
<p align="center">
  <img src="images/paris.png" alt="Ah, I love France." width="400"/>
  <br>Ah, I love France.
</p>
Also, with COVID striking the world a few years ago, I thought we just have to give fencing tribute for being the most sensible sport. Everyone wears masks, gloves, and stabs whoever that fails to socially distance. 
<p align="center">
  <img src="images/justification.png" alt="Fencing and COVID." width="400"/>
  <br>Fig 1. The intricate relationship between fencing and COVID
</p>
So, why not fencing? 

But this software can be 
Well, the 2024 Paris Olympics are coming up, and 
Also, this software is drawn from a paper I wrote with my friends (available [here](https://www.seanyoonbio.com/_files/ugd/577e3b_44a7ff922f504a058afc60882d9b4f12.pdf)). 
PAPERS is a software that evaluates and ranks athlete performance given a 
It is 
Although the package is designed for time series data, it doesn't necessarily have to be time series, and it also doesn't have to be sampled at regular intervals. For instance, in this case, we have analyzed the effect of age on the expression level of 7,348 proteins in the plasma, using a sample size of 450, as in the figure below.

<p align="center">
  <img src="test_data/plasma_clustered.png" alt="Effect of Age on Plasma Protein Expression Level" width="400"/>
  <br>Effect of Age on Plasma Protein Expression Level
</p>

## Setup
### Use directly in R
The package hasn't been released on CRAN yet, so it has to be downloaded from Github.
1. Install the "devtools" package in R: 
```
install.packages("devtools")
```

2. Load the "devtools" package in R: 
```
library(devtools)
```

3. Install the package from Github (This step shouldn't take long): 
```
install_github("seanyoon777/loessclust")
```

4. Load the package. 
```
library(loessclust)
```

### View package source code
Clone the repository to your local directory:
```
git clone https://github.com/seanyoon777/loessclust.git
```