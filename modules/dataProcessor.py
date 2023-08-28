import pandas as pd

MAX_SCORE = 15

def readDataset(filepath): 
    df = pd.read_csv(filepath)
    return df

def updateCountry(countrydata, row): 
    name1 = row['Player1']
    name2 = row['Player2']
    countrydata[name1] = row['Country1']
    countrydata[name2] = row['Country2']

def updateAthlete(athletedata, index, row): 
    name1 = row['Player1']
    name2 = row['Player2']
    year = row['Year']
    
    if year not in athletedata[name1].keys(): 
        athletedata[name1][year] = []
    athletedata[name1][year].append((index, name1, name2))
    if year not in athletedata[name2].keys(): 
        athletedata[name2][year] = []
    athletedata[name2][year].append((index, name1, name2))
    
def updateMatch(matchdata, index, row): 
    name1 = row['Player1']
    name2 = row['Player2']
    try: 
        matchdata[(index, name1, name2)] = (float(row['Score1']), float(row['Score2']))
    except ValueError:
        raise ValueError(f"Could not convert Score1 or Score2 to float for row: {row}")
    except KeyError as e:
        raise KeyError(f"KeyError encountered: {e}. Check if the row contains the correct keys.")
 
def updatePeriod(period_data, index, row): 
    year = row['Year']
    name1 = row['Player1']
    name2 = row['Player2']
    period_data[year].append((index, name1, name2))
    
def modifyRow(row):
    score1 = row['Score1']
    score2 = row['Score2']
    diff = 0
    if score1 < MAX_SCORE and score2 < MAX_SCORE : 
        diff = MAX_SCORE - max(score1, score2) 
    row['Score1'] += diff
    row['Score2'] += diff
    return row
    
def processData(filepath, modify = False): 
    '''
    Returns three dictionaries containing information about athletes in input csv file.
    countrydata: athlete name is mapped to athlete's country
    athletedata: athlete name is mapped to a dictionary, where year participated is matched
        to a tuple containing (match index, athlete, opposition)
    matchdata: tuple containing (match index, athlete, opposition) is mapped to number of
        points [athlete] scored in match [match index] against [opposition]
    '''
    df = readDataset(filepath)
    names = set(df['Player1']) | set(df['Player2'])
    observed_periods = set(df['Year'])
    country_data = {name: '' for name in names}
    athlete_data = {name: {} for name in names}
    match_data = {}
    period_data = {year: [] for year in observed_periods}
    
    if modify: 
        df = df.apply(modifyRow, axis = 1)
        
    for index, row in df.iterrows(): 
        updateCountry(country_data, row)
        updateAthlete(athlete_data, index, row)
        updateMatch(match_data, index, row)
        updatePeriod(period_data, index, row)
    return (period_data, country_data, athlete_data, match_data)
