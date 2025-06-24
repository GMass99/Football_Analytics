def get_team_id(team_name):
    import pandas as pd
    teams = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\teams.csv")
    team_id = teams[teams['name'] == team_name]['id'].values[0]
    return team_id

def get_team_fixtures(team_name):
    import pandas as pd
    team_id = get_team_id(team_name)
    fixtures = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\fixtures.csv")
    fixtures = fixtures[(fixtures['home_team_id'] == team_id) | (fixtures['away_team_id'] == team_id)].reset_index(drop=True)
    fixtures[['home_team','away_team']] = fixtures['name'].str.split(' vs ', expand=True)
    fixtures['opponent'] = fixtures.apply(lambda x: x['away_team'] if x['home_team'] == team_name else x['home_team'], axis=1)
    #fixtures = fixtures[fixtures['stats_imported'] == 1].reset_index(drop=True)
    fixtures = fixtures[['id','competition_id','round_id','season_id','kickoff_datetime','opponent','home_team','away_team','home_team_id','away_team_id','home_team_goals','away_team_goals']]
    return fixtures

def get_stat_id(stat_name):
    import pandas as pd
    stats = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\stats_types.csv")
    stat_id = stats[stats['name'] == stat_name]['id'].values[0]
    return stat_id

def get_team_stats(stat, team, venue='Yes'):
    import pandas as pd
    team_stats = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\fixture_team_stats.csv")
    fixtures = get_team_fixtures(team)
    if stat == 'Fouls Drawn':
        team_stats = team_stats[team_stats['fixture_id'].isin((fixtures).id.unique()) & 
                            (team_stats['stats_type_id'] == get_stat_id('Fouls')) & 
                            (team_stats['team_id'] != get_team_id(team))].reset_index(drop=True)
    else:
        team_stats = team_stats[team_stats['fixture_id'].isin((fixtures).id.unique()) & 
                                (team_stats['stats_type_id'] == get_stat_id(stat)) & 
                                (team_stats['team_id'] == get_team_id(team))].reset_index(drop=True)
    team_stats = team_stats[['fixture_id','value','team_id']]
    team_stats = team_stats.merge(fixtures, left_on='fixture_id', right_on='id', how='left')
    if venue == 'Yes':
        venue = []
        for index, row in team_stats.iterrows():
            if row['team_id'] == row['home_team_id']:
                venue.append('H')
            else:
                venue.append('A')
        team_stats['venue'] = venue
        team_stats = team_stats[['kickoff_datetime','opponent','value','venue']]
    else:
        team_stats = team_stats[['kickoff_datetime','opponent','value']]
    team_stats.rename(columns={'value': f'Team {stat}'}, inplace=True)
    return team_stats.sort_values(by='kickoff_datetime').reset_index(drop=True)

def get_opp_stats(stat, team, venue='Yes'):
    import pandas as pd
    team_stats = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\fixture_team_stats.csv")
    fixtures = get_team_fixtures(team)
    if stat == 'Fouls Drawn':
        team_stats = team_stats[team_stats['fixture_id'].isin((fixtures).id.unique()) & 
                            (team_stats['stats_type_id'] == get_stat_id('Fouls')) & 
                            (team_stats['team_id'] == get_team_id(team))].reset_index(drop=True)
    else:
        team_stats = team_stats[team_stats['fixture_id'].isin((fixtures).id.unique()) & 
                                (team_stats['stats_type_id'] == get_stat_id(stat)) & 
                                (team_stats['team_id'] != get_team_id(team))].reset_index(drop=True)
    team_stats = team_stats[['fixture_id','value','team_id']]
    team_stats = team_stats.merge(fixtures, left_on='fixture_id', right_on='id', how='left')
    if venue == 'Yes':
            venue = []
            for index, row in team_stats.iterrows():
                if row['team_id'] == row['home_team_id']:
                    venue.append('H')
                else:
                    venue.append('A')
            team_stats['venue'] = venue
            team_stats = team_stats[['kickoff_datetime','opponent','value','venue']]
    else:
        team_stats = team_stats[['kickoff_datetime','opponent','value']]
    team_stats.rename(columns={'value': f'Team {stat}'}, inplace=True)
    return team_stats.sort_values(by='kickoff_datetime').reset_index(drop=True)

def get_weighted_opp_stats(stat, team, weight, date_from=None):
    import pandas as pd
    if date_from is None:
        date_from = pd.to_datetime('today')
    team_stats = get_opp_stats(stat, team)
    team_stats = team_stats[pd.to_datetime(team_stats['kickoff_datetime']) < date_from].reset_index(drop=True)
    team_stats['Weeks Since Kickoff'] = (date_from - pd.to_datetime(team_stats['kickoff_datetime'])).dt.days // 7
    team_stats['Weight'] = weight ** (team_stats['Weeks Since Kickoff'] - 5)
    team_stats.loc[team_stats['Weeks Since Kickoff'] < 6, 'Weight'] = 1
    team_stats['Weighted'+ stat] = team_stats['Team ' + stat] * team_stats['Weight']
    return team_stats

def get_weighted_team_stats(stat, team, weight, date_from=None):
    import pandas as pd
    if date_from is None:
        date_from = pd.to_datetime('today')
    team_stats = get_team_stats(stat, team)
    team_stats = team_stats[pd.to_datetime(team_stats['kickoff_datetime']) < date_from].reset_index(drop=True)
    team_stats['Weeks Since Kickoff'] = (date_from - pd.to_datetime(team_stats['kickoff_datetime'])).dt.days // 7
    team_stats['Weight'] = weight ** (team_stats['Weeks Since Kickoff'] - 5)
    team_stats.loc[team_stats['Weeks Since Kickoff'] < 6, 'Weight'] = 1
    team_stats['Weighted'+ stat] = team_stats['Team ' + stat] * team_stats['Weight']
    return team_stats

def get_team_weighted_average(stat, team, weight, date_from=None):
    team_stats = get_weighted_team_stats(stat, team, weight, date_from)
    return team_stats['Weighted'+ stat].sum() / team_stats['Weight'].sum()

def get_opp_weighted_average(stat, team, weight, date_from=None):
    team_stats = get_weighted_opp_stats(stat, team, weight, date_from)
    return team_stats['Weighted'+ stat].sum() / team_stats['Weight'].sum()

def get_team(team_id):
    import pandas as pd
    teams = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\teams.csv")
    team = teams[teams['id'] == team_id]
    return team['name'].values[0]

def get_player_stats(stat_df,player_id, stat, mins=10, team=True):
    import pandas as pd
    stat_types = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\stats_types.csv")
    player_df = stat_df[stat_df['player_id'] == player_id]
    team_id = player_df['team_id'].iloc[-1]
    team_name = get_team(team_id)
    team_stats = get_team_stats(stat,team_name)
    team_stats = team_stats[team_stats[f'Team {stat}'] > 0]
    player_stats = player_df.merge(stat_types, left_on='stats_type_id', right_on='id')
    player_minutes = player_stats[player_stats['name'] == 'Minutes Played']
    player_minutes = player_minutes[['fixture_id','value','team_id']]
    player_minutes.rename(columns={'value':'minutes'}, inplace=True)
    player_minutes['minutes'] = player_minutes['minutes'].astype(int)
    player_minutes = player_minutes[player_minutes['minutes'] > mins]
    player_stats = player_stats[player_stats['name'] == stat]
    player_stats.drop(columns=['team_id'], inplace=True)
    player_stats = player_minutes.merge(player_stats, left_on='fixture_id', right_on='fixture_id', how='left')
    player_stats['value'].fillna(0, inplace=True)
    player_stats = player_stats[['fixture_id','value','minutes','team_id']]
    fixtures = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\fixtures.csv")
    player_stats = player_stats.merge(fixtures, left_on='fixture_id', right_on='id')
    player_stats = player_stats[player_stats['team_id'] == team_id]
    player_stats = player_stats[['kickoff_datetime','name','value','minutes']].sort_values(by='kickoff_datetime')
    player_stats['value'] = player_stats['value'].astype(int)
    player_stats.rename(columns={'name':'Game','value': f'Player {stat}'}, inplace=True)
    player_stats[f'Min Adjusted Player {stat}'] = (player_stats[f'Player {stat}'] / player_stats['minutes'] * 90).round(3)
    player_stats['Game'] = player_stats['Game'].str.split(' v ').str[0]
    if team == True:
        player_stats = player_stats.merge(team_stats, left_on='kickoff_datetime', right_on='kickoff_datetime')
        player_stats[f'{stat} Proportion'] = ((player_stats[f'Min Adjusted Player {stat}'] / player_stats[f'Team {stat}'])).round(3)
    else:
        return player_stats
    return player_stats

def get_weighted_player_stats(df,player_id,stat, weight):
    import pandas as pd
    player_stats = get_player_stats(df,player_id,stat)
    player_stats = player_stats[pd.to_datetime(player_stats['kickoff_datetime']) < pd.to_datetime('today')].reset_index(drop=True)
    player_stats['Weeks Since Kickoff'] = (pd.to_datetime('today') - pd.to_datetime(player_stats['kickoff_datetime'])).dt.days // 7
    player_stats['Weight'] = weight ** (player_stats['Weeks Since Kickoff'] - 5)
    player_stats.loc[player_stats['Weeks Since Kickoff'] < 6, 'Weight'] = 1
    player_stats[f'Weighted {stat} Proportion'] = player_stats[f'{stat} Proportion'] * player_stats['Weight']
    return player_stats

def get_player_weighted_average(df,player_id,stat,weight):
    player_stats = get_weighted_player_stats(df,player_id,stat,weight)
    if player_stats[f'Weighted {stat} Proportion'].sum() == 0:
        return 0
    else:
        return player_stats[f'Weighted {stat} Proportion'].sum() / player_stats['Weight'].sum()

def distribute_stat_to_players(df, stat, value, team, opponent, weight):
    import numpy as np
    import pandas as pd
    players = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\players.csv")
    team_players = players[players['current_team_id'] == get_team_id(team)]
    predicted_stats = []
    for name, id in team_players[['display_name','id']].values:
        try:
            stat_prop = get_player_weighted_average(df,id,stat,weight)
            if np.isnan(stat_prop) == False:
                player_name = name
                predicted_stat = stat_prop * value
                predicted_stats.append([player_name,predicted_stat])
        except:
            pass        
    predicted_stats = pd.DataFrame(predicted_stats, columns=['Player',f'Predicted {stat}'])
    predicted_stats[f'Predicted {stat}'].fillna(0, inplace=True)
    predicted_stats[f'Predicted {stat}'] = predicted_stats[f'Predicted {stat}'].round(2)
    predicted_stats['Opponent'] = opponent
    predicted_stats['Team'] = team
    predicted_stats = predicted_stats[['Player','Team','Opponent',f'Predicted {stat}']]
    predicted_stats = predicted_stats.sort_values(by=f'Predicted {stat}', ascending=False).reset_index(drop=True)
    return predicted_stats.values

def get_stat_list():
    return ['Goals','Shots Total','Shots On Target','Passes','Interceptions','Tackles','Total Crosses','Corners','Fouls']

def get_team_players(team):
    import pandas as pd
    players = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\players.csv")
    team_id = get_team_id(team)
    team_players = players[players['current_team_id'] == team_id]
    return team_players[['id','display_name']]

def get_round_id():
    import pandas as pd
    date = pd.to_datetime('today')
    fixtures = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\fixtures.csv")
    fixtures['kickoff_datetime'] = pd.to_datetime(fixtures['kickoff_datetime'])
    fixtures = fixtures[fixtures['kickoff_datetime'] > date].reset_index(drop=True)
    fixtures = fixtures.sort_values(by='kickoff_datetime')
    round_id = fixtures['round_id'].iloc[0]
    return round_id

def get_prem_fixtures():
    import pandas as pd
    round_id = get_round_id()
    fixtures = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\fixtures.csv")
    fixtures = fixtures[fixtures['round_id'] == round_id]
    fixtures = fixtures[['id','kickoff_datetime','name','home_team_id','away_team_id']]
    fixtures['home_team'] = fixtures['home_team_id'].apply(get_team)
    fixtures['away_team'] = fixtures['away_team_id'].apply(get_team)
    fixtures = fixtures[['id','kickoff_datetime','home_team','away_team']]
    fixtures.sort_values(by='kickoff_datetime', inplace=True)
    return fixtures.reset_index(drop=True)

def load_model(stat):
    import pickle
    filename = stat + '_model.sav'
    model = pickle.load(open(filename, 'rb'))
    return model

def load_all_models(stat_list):
    models = {}
    for stat in stat_list:
        model = load_model(stat)
        models[stat] = model
    return models

def get_team_stat_prediction(team, opponent, stat, model, venue):
    team_history = get_team_weighted_average(stat, team, 0.96)
    opponent_history = get_opp_weighted_average(stat, opponent, 0.96)
    team_stat = model.predict([[team_history, opponent_history]])
    return (team_stat[0] * calculate_venue_effect(team, stat, venue)).round(2) 

def get_team_all_stats_prediction(team, opponent, stat_list, models, venue):
    predictions = {}
    predictions['Team'] = team
    predictions['Opponent'] = opponent
    predictions['Venue'] = venue
    for stat in stat_list:
        model = models[stat]
        predictions[stat] = get_team_stat_prediction(team, opponent, stat, model, venue)
    return predictions

def get_team_round_predictions(fixtures, stat_list, models):
    import pandas as pd
    round_preds = []
    for index, row in fixtures.iterrows():
        home_team_preds = get_team_all_stats_prediction(row['home_team'], row['away_team'], stat_list, models, 'H')
        away_team_preds = get_team_all_stats_prediction(row['away_team'], row['home_team'], stat_list, models, 'A')
        home_team_preds['Fouls Drawn'] = away_team_preds['Fouls']
        away_team_preds['Fouls Drawn'] = home_team_preds['Fouls']
        home_team_preds['Assists'] = (home_team_preds['Goals'] * 0.82).round(2)
        away_team_preds['Assists'] = (away_team_preds['Goals'] * 0.82).round(2)
        home_team_preds['Saves'] = away_team_preds['Shots On Target'] - away_team_preds['Goals']
        away_team_preds['Saves'] = home_team_preds['Shots On Target'] - home_team_preds['Goals']
        round_preds.append(home_team_preds)
        round_preds.append(away_team_preds)
        df = pd.DataFrame(round_preds)
    return df[['Team','Opponent','Venue','Goals','Assists'] + stat_list[1:] + ['Fouls Drawn','Saves']]  

def distribute_team_predictions_to_players(player_stats, team_predictions):
    import numpy as np
    import pandas as pd
    stat_list = team_predictions.columns[3:].to_list()
    stat_list.remove('Saves')
    stat_list.remove('Corners')
    full_predicted_stats = []
    players = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\players.csv")
    for row in team_predictions.iterrows():
        team_stat_values = row[1].values
        team_players = players[players['current_team_id'] == get_team_id(team_stat_values[0])]
        for name, id in team_players[['display_name','id']].values:
            player_pred_stats = {}
            for i in range(len(stat_list)):
                try:
                    stat_prop = get_player_weighted_average(player_stats, id, stat_list[i], 0.96)
                    if np.isnan(stat_prop) == False:
                        if stat_prop == 0:
                            player_pred_stats[stat_list[i]] = 0.00
                        else:
                            predicted_stat = stat_prop * team_stat_values[i+3]
                            player_pred_stats[stat_list[i]] = predicted_stat.round(2)
                except:
                    pass
            if sum(player_pred_stats.values()) == 0:
                continue
            player_pred_stats['Player'] = name
            player_pred_stats['Team'] = team_stat_values[0]
            player_pred_stats['Opponent'] = team_stat_values[1]
            player_pred_stats['Venue'] = team_stat_values[2]
            full_predicted_stats.append(player_pred_stats)
    df = pd.DataFrame(full_predicted_stats)
    df.dropna(ignore_index=True, inplace=True)
    return df[['Player','Team','Opponent','Venue'] + stat_list]  

def calculate_venue_effect(team, stat, venue):
    team_stats = get_team_stats(stat, team)
    home = team_stats[team_stats['venue'] == 'H'][f'Team {stat}'].mean()
    away = team_stats[team_stats['venue'] == 'A'][f'Team {stat}'].mean()
    avg = team_stats[f'Team {stat}'].mean()
    if len(team_stats) < 20:
        weight = 0.5
    else:
        weight = 0
    if venue == 'H':
        return (home-((home-avg)*weight))/avg
    else:
        return (away-((away-avg)*weight))/avg
    
def get_player_id(player_name, player_df, team):
    team_id = get_team_id(team)
    player_df = player_df[player_df['current_team_id'] == team_id]
    player_id = player_df[player_df['display_name'] == player_name]['id']
    return player_id.values[0]

def get_player_mins(stat_df,player_name, players, team, mins = 10):
    player_id = get_player_id(player_name, players, team)
    player_stats = stat_df[stat_df['player_id'] == player_id]
    team_fix = get_team_fixtures(team)
    team_fix = team_fix['id'].tolist()
    player_stats = player_stats[player_stats['fixture_id'].isin(team_fix)]
    player_stats = player_stats[player_stats['value'] > mins]
    player_minutes = player_stats[player_stats['stats_type_id'] == 119]
    mins = player_minutes['value'].sum().astype(int)
    games_played = len(player_minutes)
    return mins, games_played

def player_stat_types():
    import pandas as pd
    player_stats = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\fixture_player_stats.csv")
    stats_types = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\stats_types.csv")
    fixtures = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\fixtures.csv")
    fixtures = fixtures[fixtures['season_id'] == 23614]
    player_stats = player_stats[player_stats['fixture_id'].isin(fixtures['id'])]
    stats_types = stats_types[stats_types['id'].isin(player_stats['stats_type_id'])]
    return stats_types['name'].unique()