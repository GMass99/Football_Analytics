def get_team_id(team_name):
    import pandas as pd
    teams = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\teams.csv")
    team_id = teams[teams['name'] == team_name]['id'].values[0]
    return team_id

def get_team_fixtures(team_name, comp_id=None, season_id=None):
    import pandas as pd
    team_id = get_team_id(team_name)
    fixtures = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\fixtures.csv")
    fixtures = fixtures[(fixtures['home_team_id'] == team_id) | (fixtures['away_team_id'] == team_id)].reset_index(drop=True)
    fixtures[['home_team','away_team']] = fixtures['name'].str.split(' vs ', expand=True)
    fixtures['opponent'] = fixtures.apply(lambda x: x['away_team'] if x['home_team'] == team_name else x['home_team'], axis=1)
    #fixtures = fixtures[fixtures['stats_imported'] == 1].reset_index(drop=True)
    if comp_id is not None:
        try:
            fixtures = fixtures[fixtures['competition_id'].isin(comp_id)].reset_index(drop=True)
        except:
            fixtures = fixtures[fixtures['competition_id'] == comp_id].reset_index(drop=True)
    if season_id is not None:
        fixtures = fixtures[fixtures['season_id'] == season_id].reset_index(drop=True)
    fixtures = fixtures[['id','competition_id','round_id','season_id','kickoff_datetime','opponent','home_team','away_team','home_team_id','away_team_id','home_team_goals','away_team_goals']]
    return fixtures.sort_values(by='kickoff_datetime').reset_index(drop=True)

def get_team_league_id(team):
    import pandas as pd
    comp_season_teams = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\competition_season_teams.csv")
    team_id = get_team_id(team)
    comp_season_teams = comp_season_teams[comp_season_teams['competition_id'] != 2]
    comp_season_teams = comp_season_teams[comp_season_teams['team_id'] == team_id]
    league_id = comp_season_teams['competition_id'].values[0]
    return league_id

def get_stat_id(stat_name):
    import pandas as pd
    stats = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\stats_types.csv")
    stat_id = stats[stats['name'] == stat_name]['id'].values[0]
    return stat_id

def get_team_stats(stat, team, venue='Yes', date_from=None, comp_id=None, season_id=None, games=None):
    import pandas as pd
    team_stats = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\fixture_team_stats.csv")
    team_stats.drop_duplicates(subset=['fixture_id','stats_type_id','team_id'], inplace=True)
    fixtures = get_team_fixtures(team, comp_id, season_id)
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
        team_stats = team_stats[['kickoff_datetime','season_id','opponent','value','venue']]
    else:
        team_stats = team_stats[['kickoff_datetime','season_id','opponent','value']]
    team_stats.rename(columns={'value': f'Team {stat}'}, inplace=True)
    team_stats = team_stats.sort_values(by='kickoff_datetime').reset_index(drop=True)
    if date_from is not None:
        team_stats = team_stats[pd.to_datetime(team_stats['kickoff_datetime']) < date_from].reset_index(drop=True)
    if games is not None:
        team_stats = team_stats.iloc[-games:]
    return team_stats.reset_index(drop=True)

def get_opp_stats(stat, team, venue='Yes', date_from=None, comp_id=None, season_id=None, games=None):
    import pandas as pd
    team_stats = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\fixture_team_stats.csv")
    team_stats.drop_duplicates(subset=['fixture_id','stats_type_id','team_id'], inplace=True)
    fixtures = get_team_fixtures(team, comp_id, season_id)
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
                    venue.append('A')
                else:
                    venue.append('H')
            team_stats['venue'] = venue
            team_stats = team_stats[['kickoff_datetime','season_id','opponent','value','venue']]
    else:
        team_stats = team_stats[['kickoff_datetime','season_id','opponent','value']]
    team_stats.rename(columns={'value': f'Team {stat}'}, inplace=True)
    team_stats = team_stats.sort_values(by='kickoff_datetime').reset_index(drop=True)
    if date_from is not None:
        team_stats = team_stats[pd.to_datetime(team_stats['kickoff_datetime']) < date_from].reset_index(drop=True)
    if games is not None:
        team_stats = team_stats.iloc[-games:]
    return team_stats.reset_index(drop=True)

def get_weighted_opp_stats(stat, team, weight, venue='Yes', date_from=None, comp_id = None, season_id=None, games=None):
    import pandas as pd
    team_stats = get_opp_stats(stat, team, venue, date_from, comp_id, season_id, games)
    if date_from is None:
        date_from = pd.to_datetime('today')
    team_stats = team_stats[pd.to_datetime(team_stats['kickoff_datetime']) < date_from].reset_index(drop=True)
    team_stats['Weeks Since Kickoff'] = (date_from - pd.to_datetime(team_stats['kickoff_datetime'])).dt.days // 7
    team_stats['Weight'] = weight ** (team_stats['Weeks Since Kickoff'])
    team_stats['Weighted'+ stat] = team_stats['Team ' + stat] * team_stats['Weight']
    return team_stats

def get_weighted_team_stats(stat, team, weight, venue='Yes', date_from=None, comp_id = None, season_id=None, games=None):
    import pandas as pd
    team_stats = get_team_stats(stat, team, venue, date_from, comp_id, season_id, games)
    if date_from is None:
        date_from = pd.to_datetime('today')
    team_stats = team_stats[pd.to_datetime(team_stats['kickoff_datetime']) < date_from].reset_index(drop=True)
    team_stats['Weeks Since Kickoff'] = (date_from - pd.to_datetime(team_stats['kickoff_datetime'])).dt.days // 7
    team_stats['Weight'] = weight ** (team_stats['Weeks Since Kickoff'])
    team_stats['Weighted '+ stat] = team_stats['Team ' + stat] * team_stats['Weight']
    return team_stats

def get_team_weighted_average(stat, team, weight, venue='Yes', date_from=None, comp_id = None, season_id=None, games=None):
    team_stats = get_weighted_team_stats(stat, team, weight, venue, date_from, comp_id, season_id, games)
    return team_stats['Weighted '+ stat].sum() / team_stats['Weight'].sum()

def get_opp_weighted_average(stat, team, weight, venue='Yes', date_from=None, comp_id = None, season_id=None, games=None):
    team_stats = get_weighted_opp_stats(stat, team, weight, venue, date_from, comp_id, season_id, games)
    return team_stats['Weighted'+ stat].sum() / team_stats['Weight'].sum()

def get_team(team_id):
    import pandas as pd
    teams = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\teams.csv")
    team = teams[teams['id'] == team_id]
    return team['name'].values[0]

def get_player_stats(stat_df,team_df,player_id, stat, mins=50, games=None):
    import pandas as pd
    stat_types = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\stats_types.csv")
    player_df = stat_df[stat_df['player_id'] == player_id]
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
    player_stats = player_stats[['kickoff_datetime','fixture_id','team_id','name','value','minutes']].sort_values(by='kickoff_datetime')
    if stat == 'Expected Goals (xG)':
        player_stats['value'] = player_stats['value'].astype(float)
    else:
        player_stats['value'] = player_stats['value'].astype(int)
    player_stats.rename(columns={'name':'Game','value': f'Player {stat}'}, inplace=True)
    if games is not None:
        if stat == 'Goals':
            player_stats = player_stats.iloc[-(games+20):]
        else:
            player_stats = player_stats.iloc[-games:]
    player_stats.reset_index(drop=True)
    team_stat_list = []
    for i in range(len(player_stats)):
        team_id = player_stats['team_id'].iloc[i]
        fixture_id = player_stats['fixture_id'].iloc[i]
        team_stat_fix = team_df[team_df['fixture_id'] == fixture_id]
        if stat == 'Fouls Drawn':
            team_stat_df = team_stat_fix[team_stat_fix['team_id'] != team_id]
            team_stat = team_stat_df[team_stat_df['stats_type_id'] == get_stat_id('Fouls')]
        else:
            team_stat_df = team_stat_fix[team_stat_fix['team_id'] == team_id]
            team_stat = team_stat_df[team_stat_df['stats_type_id'] == get_stat_id(stat)]
        try:
            team_stat_list.append(team_stat['value'].values[0])
        except:
            team_stat_list.append(None)
    player_stats[f'Team {stat}'] = team_stat_list 
    player_stats[f'Team {stat}'].replace({0:None}, inplace=True)
    player_stats.dropna(subset=[f'Team {stat}'], inplace=True) 
    if stat == 'Expected Goals (xG)':
        player_stats[f'Team {stat}'] = player_stats[f'Team {stat}'].astype(float)
    else:
        player_stats[f'Team {stat}'] = player_stats[f'Team {stat}'].astype(int)
    if stat == 'Goals':
        player_stats = player_stats.iloc[-games:]
    player_stats['Game'] = player_stats['Game'].str.split(' v ').str[0]
    player_stats[f'{stat} Proportion'] = ((player_stats[f'Player {stat}'] / player_stats[f'Team {stat}'])).round(3)
    player_stats[f'{stat} Proportion'] = player_stats[f'{stat} Proportion'].apply(lambda x: 1 if x > 1 else x)
    player_stats[f'{stat} Proportion'].fillna(0, inplace=True)
    return player_stats.reset_index(drop=True)

def get_weighted_player_stats(df,team_df,player_id,stat, weight, mins=50, games=None):
    import pandas as pd
    player_stats = get_player_stats(df,team_df,player_id,stat, mins, games)
    player_stats = player_stats[pd.to_datetime(player_stats['kickoff_datetime']) < pd.to_datetime('today')].reset_index(drop=True)
    player_stats['Weeks Since Kickoff'] = (pd.to_datetime('today') - pd.to_datetime(player_stats['kickoff_datetime'])).dt.days // 7
    player_stats['Weight'] = weight ** (player_stats['Weeks Since Kickoff'] - 5)
    player_stats.loc[player_stats['Weeks Since Kickoff'] < 6, 'Weight'] = 1
    for i in range(len(player_stats)):
        if player_stats.loc[i,'team_id'] != player_stats.loc[len(player_stats)-1,'team_id']:
            player_stats.loc[i,'Weight'] = player_stats.loc[i,'Weight'] * 0.5
    player_stats[f'Weighted {stat} Proportion'] = player_stats[f'{stat} Proportion'] * player_stats['Weight']
    return player_stats

def get_player_weighted_average(df,team_df,player_id,stat,weight,mins=50,games=None):
    player_stats = get_weighted_player_stats(df,team_df,player_id,stat,weight,mins,games)
    if player_stats[f'Weighted {stat} Proportion'].sum() == 0:
        return 0
    elif 15 <= len(player_stats) <= 20:
        return player_stats[f'Weighted {stat} Proportion'].sum() / player_stats['Weight'].sum() * 0.7
    elif 10 <= len(player_stats) < 15:
        return (player_stats[f'Weighted {stat} Proportion'].sum() / player_stats['Weight'].sum()) * 0.6
    elif 5 < len(player_stats) < 10:
        return (player_stats[f'Weighted {stat} Proportion'].sum() / player_stats['Weight'].sum()) * 0.5
    elif len(player_stats) < 5:
        return (player_stats[f'Weighted {stat} Proportion'].sum() / player_stats['Weight'].sum()) * 0.1
    elif len(player_stats[player_stats['Weeks Since Kickoff'] < 20]) == 0:
        return (player_stats[f'Weighted {stat} Proportion'].sum() / player_stats['Weight'].sum()) * 0.8
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
    return ['Goals','Shots Total','Shots On Target','Corners','Fouls','Yellowcards','Tackles','Passes','Successful Passes','Interceptions','Total Crosses','Offsides']

def get_team_players(team):
    import pandas as pd
    players = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\players.csv")
    team_id = get_team_id(team)
    team_players = players[players['current_team_id'] == team_id]
    return team_players[['id','display_name']]

def get_round_id(fixtures, previous=False):
    import pandas as pd
    date = pd.to_datetime('today')
    fixtures['kickoff_datetime'] = pd.to_datetime(fixtures['kickoff_datetime'])
    if previous == True:
        fixtures = fixtures[fixtures['kickoff_datetime'] < date].reset_index(drop=True)
        fixtures = fixtures.sort_values(by='kickoff_datetime', ascending=False)
    else:
        fixtures = fixtures[fixtures['kickoff_datetime'] > date].reset_index(drop=True)
        fixtures = fixtures.sort_values(by='kickoff_datetime', ascending=True)
    round_id = fixtures['round_id'].iloc[0]
    return round_id

def get_stage_id(fixtures, previous=False):
    import pandas as pd
    date = pd.to_datetime('today')
    fixtures['kickoff_datetime'] = pd.to_datetime(fixtures['kickoff_datetime'])
    if previous == True:
        fixtures = fixtures[fixtures['kickoff_datetime'] < date].reset_index(drop=True)
        fixtures = fixtures.sort_values(by='kickoff_datetime', ascending=False)
    else:
        fixtures = fixtures[fixtures['kickoff_datetime'] > date].reset_index(drop=True)
        fixtures = fixtures.sort_values(by='kickoff_datetime', ascending=True)
    stage_id = fixtures['stage_id'].iloc[0]
    return stage_id

def get_fixtures(fixtures, previous=False, cup=False, leg=None):
    import pandas as pd
    if cup == True:
        stage_id = get_stage_id(fixtures, previous)
        fixtures = fixtures[fixtures['stage_id'] == stage_id]
        if leg != None:
            fixtures = fixtures[fixtures['leg'] == f'{leg}/2']
    else:
        round_id = get_round_id(fixtures,previous)
        fixtures = fixtures[fixtures['round_id'] == round_id]
    fixtures = fixtures[['id','kickoff_datetime','name','home_team_id','away_team_id']]
    fixtures['home_team'] = fixtures['home_team_id'].apply(get_team)
    fixtures['away_team'] = fixtures['away_team_id'].apply(get_team)
    fixtures = fixtures[['id','kickoff_datetime','home_team','away_team']]
    fixtures.sort_values(by=['kickoff_datetime','home_team'], inplace=True)
    return fixtures.reset_index(drop=True)

def load_model(stat):
    import pickle
    filename = "C:\\Users\\George\\Documents\\Statz.ai\\Notebooks\\PL Projections\\Model Builds\\" + stat + '_model.sav'
    model = pickle.load(open(filename, 'rb'))
    return model

def load_all_models(stat_list):
    models = {}
    for stat in stat_list:
        model = load_model(stat)
        models[stat] = model
    return models

def get_team_stat_prediction(team, opponent, stat, model, venue, comp_id=None, games=None):
    team_history = get_team_weighted_average(stat, team, 0.98,comp_id=comp_id,games=games) * calculate_team_venue_effect(team, stat, venue,comp_id=comp_id,games=games*2)
    if venue == 'H':
        opponent_venue = 'A'
    else:
        opponent_venue = 'H'    
    opponent_history = get_opp_weighted_average(stat, opponent, 0.98,comp_id=comp_id,games=games) * calculate_opp_venue_effect(team, stat, opponent_venue,comp_id=comp_id,games=games*2)
    team_stat = model.predict([[team_history, opponent_history]])
    return (team_stat[0]).round(2) 

def get_team_all_stats_prediction(team, opponent, stat_list, models, venue, comp_id=None, season_id=None, games=None):
    predictions = {}
    predictions['Team'] = team
    predictions['Opponent'] = opponent
    predictions['Venue'] = venue
    for stat in stat_list:
        model = models[stat]
        predictions[stat] = get_team_stat_prediction(team, opponent, stat, model, venue, comp_id=comp_id,games=games)
    return predictions

def get_team_round_predictions(fixtures, stat_list, models, goals=False, comp_id=None, games=None):
    import pandas as pd
    if goals == False:
        stat_list.remove('Goals')
    round_preds = []
    for index, row in fixtures.iterrows():
        home_team_preds = get_team_all_stats_prediction(row['home_team'], row['away_team'], stat_list, models, 'H', comp_id=comp_id,games=games)
        away_team_preds = get_team_all_stats_prediction(row['away_team'], row['home_team'], stat_list, models, 'A', comp_id=comp_id,games=games)
        home_team_preds['Fouls Drawn'] = away_team_preds['Fouls']
        away_team_preds['Fouls Drawn'] = home_team_preds['Fouls']
        if goals == True:
            home_team_preds['Assists'] = (home_team_preds['Goals'] * 0.82).round(2)
            away_team_preds['Assists'] = (away_team_preds['Goals'] * 0.82).round(2)
            home_team_preds['Saves'] = away_team_preds['Shots On Target'] - away_team_preds['Goals']
            away_team_preds['Saves'] = home_team_preds['Shots On Target'] - home_team_preds['Goals']
        round_preds.append(home_team_preds)
        round_preds.append(away_team_preds)
        df = pd.DataFrame(round_preds)
    if goals == True:
        return df[['Team','Opponent','Venue','Goals','Assists'] + stat_list[1:] + ['Fouls Drawn','Saves']]
    else:
        return df[['Team','Opponent','Venue'] + stat_list[0:] + ['Fouls Drawn']]  

def distribute_team_predictions_to_players(player_stats, team_df, team_predictions, xG=True):
    import numpy as np
    import pandas as pd
    team_predictions = team_predictions.drop(columns=['Corners'])
    stat_list = team_predictions.columns[3:].to_list()
    stat_list.remove('Saves')
    full_predicted_stats = []
    players = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\players.csv")
    for row in team_predictions.iterrows():
        team_stat_values = row[1].values
        team_players = players[players['current_team_id'] == get_team_id(team_stat_values[0])]
        for name, id in team_players[['display_name','id']].values:
            player_pred_stats = {}
            for i in range(len(stat_list)):
                if stat_list[i] == 'Goals':
                    try:
                        stat_prop_goals = get_player_weighted_average(player_stats, team_df, id, 'Goals', 0.96, games=30)
                        if xG == True:
                            stat_prop_xG = get_player_weighted_average(player_stats, team_df, id, 'Expected Goals (xG)', 0.96, games=30)
                            stat_prop = (stat_prop_goals + stat_prop_xG) / 2
                        else:
                            stat_prop = stat_prop_goals
                        if np.isnan(stat_prop) == False:
                            if stat_prop == 0:
                                player_pred_stats[stat_list[i]] = 0.00
                            else:
                                predicted_stat = stat_prop * team_stat_values[i+3]
                                player_pred_stats[stat_list[i]] = predicted_stat.round(2)
                    except:
                        pass
                else:
                    try:
                        stat_prop = get_player_weighted_average(player_stats, team_df, id, stat_list[i], 0.96, games=30)
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

def calculate_team_venue_effect(team, stat, venue, comp_id=None, games=None):
    team_stats = get_team_stats(stat, team,'Yes', comp_id=comp_id, games=games)
    home = team_stats[team_stats['venue'] == 'H'][f'Team {stat}'].mean()
    away = team_stats[team_stats['venue'] == 'A'][f'Team {stat}'].mean()
    avg = team_stats[f'Team {stat}'].mean()
    if venue == 'H':
        return home/avg
    else:
        return away/avg
    
def calculate_opp_venue_effect(team, stat, venue, comp_id=None, games=None):
    team_stats = get_opp_stats(stat, team,'Yes', comp_id=comp_id, games=games)
    home = team_stats[team_stats['venue'] == 'H'][f'Team {stat}'].mean()
    away = team_stats[team_stats['venue'] == 'A'][f'Team {stat}'].mean()
    avg = team_stats[f'Team {stat}'].mean()
    if venue == 'H':
        return home/avg
    else:
        return away/avg
    
def get_player_id(player_name, player_df, team):
    team_id = get_team_id(team)
    player_df = player_df[player_df['current_team_id'] == team_id]
    player_id = player_df[player_df['display_name'] == player_name]['id']
    return player_id.values[0]

def get_player_mins(stat_df,player_name, players, team, mins = 50, comp_id=None, season_id=None, games=None):
    player_id = get_player_id(player_name, players, team)
    player_stats = stat_df[stat_df['player_id'] == player_id]
    team_fix = get_team_fixtures(team, comp_id, season_id )
    team_fix = team_fix['id'].tolist()
    player_stats = player_stats[player_stats['fixture_id'].isin(team_fix)]
    player_stats = player_stats[player_stats['value'] > mins]
    player_minutes = player_stats[player_stats['stats_type_id'] == 119]
    player_minutes = player_minutes.iloc[-games:]
    mins = player_minutes['value'].sum().astype(int)
    games_played = len(player_minutes)
    return mins, games_played

def get_previous_team_ratings(league, fbref_id):
    import pandas as pd
    import requests
    from bs4 import BeautifulSoup
    import time
    league_dashed = league.replace(' ', '-')
    standings_url = f"https://fbref.com/en/comps/{fbref_id}/{league_dashed}-Stats"
    data = requests.get(standings_url)
    soup = BeautifulSoup(data.text)
    standings_table = soup.select('table.stats_table')[0]
    links = standings_table.find_all('a')
    links = [l.get("href") for l in links]
    links = [l for l in links if '/squads/' in l]
    team_urls = [f"https://fbref.com{l}" for l in links]
    previous_urls = [link[:link.rfind('/')] + "/2023-2024" + link[link.rfind('/'):] for link in team_urls]
    previous_team_ratings = []
    time.sleep(5)
    for url in previous_urls:
        team = ' '.join(url.split('/')[-1].split('-')[:-1])
        #print(team, url)
        data = requests.get(url)
        matches = pd.read_html(data.text, match="Scores & Fixtures")[0] 
        matches = matches[matches['Comp'] == league]
        if len(matches) == 0:
            continue
        matches = matches[['Date','Opponent','Venue','GF','GA','xG', 'xGA']]
        matches.dropna(inplace=True)
        matches.reset_index(drop=True, inplace=True)
        matches['GF'] = matches['GF'].astype(int)
        matches['GA'] = matches['GA'].astype(int)
        matches['xG'] = matches['xG'].astype(float)
        matches['xGA'] = matches['xGA'].astype(float)
        matches['Adjusted Goals'] = matches['GF']*0.3 + matches['xG']*0.7
        matches['Adjusted Goals Against'] = matches['GA']*0.3 + matches['xGA']*0.7
        matches = matches[['Date','Opponent','Venue','Adjusted Goals','Adjusted Goals Against']]
        matches['Weeks Since Game'] = (pd.to_datetime('today') - pd.to_datetime(matches['Date'])).dt.days // 7
        matches['Game Weight'] = 0.96**matches['Weeks Since Game']
        matches['Weighted Goals'] = matches['Adjusted Goals'] * matches['Game Weight']
        matches['Weighted Goals Against'] = matches['Adjusted Goals Against'] * matches['Game Weight']
        attack_rating = matches['Weighted Goals'].sum() / matches['Game Weight'].sum()
        defense_rating = matches['Weighted Goals Against'].sum() / matches['Game Weight'].sum()
        previous_team_ratings.append([team, attack_rating, defense_rating])
        time.sleep(5)
    previous_team_ratings = pd.DataFrame(previous_team_ratings, columns=['Team', 'Attack', 'Defense'])
    previous_team_ratings['Attack Rating'] = (previous_team_ratings['Attack'] / previous_team_ratings['Attack'].mean()) * 100
    previous_team_ratings['Defense Rating'] = ((previous_team_ratings['Defense'].mean() + (previous_team_ratings['Defense'].mean() - previous_team_ratings['Defense'])) / previous_team_ratings['Defense'].mean()) * 100
    return previous_team_ratings[['Team', 'Attack Rating', 'Defense Rating']]

def get_current_team_ratings(league, fbref_id):
    import pandas as pd
    import requests
    from bs4 import BeautifulSoup
    import time
    league_dashed = league.replace(' ', '-')
    standings_url = f"https://fbref.com/en/comps/{fbref_id}/{league_dashed}-Stats"
    data = requests.get(standings_url)
    soup = BeautifulSoup(data.text)
    standings_table = soup.select('table.stats_table')[0]
    links = standings_table.find_all('a')
    links = [l.get("href") for l in links]
    links = [l for l in links if '/squads/' in l]
    team_urls = [f"https://fbref.com{l}" for l in links]
    team_ratings = []
    time.sleep(5)
    for url in team_urls:
        team = ' '.join(url.split('/')[-1].split('-')[:-1])
        #print(team)
        data = requests.get(url)
        matches = pd.read_html(data.text, match="Scores & Fixtures")[0] 
        matches = matches[matches['Comp'] == league]
        matches = matches[['Date','Opponent','Venue','GF','GA','xG', 'xGA']]
        matches.dropna(inplace=True)
        matches.reset_index(drop=True, inplace=True)
        matches['GF'] = matches['GF'].astype(int)
        matches['GA'] = matches['GA'].astype(int)
        matches['xG'] = matches['xG'].astype(float)
        matches['xGA'] = matches['xGA'].astype(float)
        matches['Adjusted Goals'] = matches['GF']*0.4 + matches['xG']*0.6
        matches['Adjusted Goals Against'] = matches['GA']*0.4 + matches['xGA']*0.6
        matches = matches[['Date','Opponent','Venue','Adjusted Goals','Adjusted Goals Against']]
        matches['Weeks Since Game'] = (pd.to_datetime('today') - pd.to_datetime(matches['Date'])).dt.days // 7
        matches['Game Weight'] = 0.96**matches['Weeks Since Game']
        matches['Weighted Goals'] = matches['Adjusted Goals'] * matches['Game Weight']
        matches['Weighted Goals Against'] = matches['Adjusted Goals Against'] * matches['Game Weight']
        matches10 = matches.iloc[-10:]
        attack_last10 = matches10['Adjusted Goals'].mean()
        defense_last10 = matches10['Adjusted Goals Against'].mean()
        attack_rating = ((matches['Weighted Goals'].sum() / matches['Game Weight'].sum()) * 0.65) + (attack_last10 * 0.35)
        defense_rating = ((matches['Weighted Goals Against'].sum() / matches['Game Weight'].sum()) * 0.65) + (defense_last10 * 0.35)
        team_ratings.append([team, attack_rating, defense_rating])
        time.sleep(5)
    team_ratings = pd.DataFrame(team_ratings, columns=['Team', 'Attack', 'Defense'])
    team_ratings['Attack Rating'] = (team_ratings['Attack'] / team_ratings['Attack'].mean()) * 100
    team_ratings['Defense Rating'] = ((team_ratings['Defense'].mean() + (team_ratings['Defense'].mean() - team_ratings['Defense'])) / team_ratings['Defense'].mean()) * 100
    return team_ratings[['Team', 'Attack Rating', 'Defense Rating']]

def get_ratings_old(league, fbref_id):
    import pandas as pd
    current_ratings = get_current_team_ratings(league, fbref_id)
    prev_ratings = get_previous_team_ratings(league, fbref_id)
    actual_rating = []
    for team in current_ratings['Team']:
        if team not in prev_ratings['Team'].values:
            attack = (current_ratings[current_ratings['Team'] == team]['Attack Rating'].values[0]).round(0).astype(int)
            defense = (current_ratings[current_ratings['Team'] == team]['Defense Rating'].values[0]).round(0).astype(int)
            actual_rating.append([team, attack, defense])
            continue
        prev_attack = prev_ratings[prev_ratings['Team'] == team]['Attack Rating'].values[0]
        prev_defense = prev_ratings[prev_ratings['Team'] == team]['Defense Rating'].values[0]
        current_attack = current_ratings[current_ratings['Team'] == team]['Attack Rating'].values[0]
        current_defense = current_ratings[current_ratings['Team'] == team]['Defense Rating'].values[0]
        attack = (prev_attack*0.2 + current_attack*0.8).round(0).astype(int)
        defense = (prev_defense*0.2 + current_defense*0.8).round(0).astype(int)
        actual_rating.append([team, attack, defense])
    actual_rating = pd.DataFrame(actual_rating, columns=['Team', 'Attack', 'Defense'])
    return actual_rating

def get_comp_teams(league_id,season_id):
    import pandas as pd
    comp_teams = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\competition_season_teams.csv")
    comp_teams = comp_teams[(comp_teams['competition_id'] == league_id) & 
                            (comp_teams['season_id'] == season_id)].reset_index(drop=True)
    team_names = []
    for index, row in comp_teams.iterrows():
        team_names.append(get_team(row['team_id']))
    return team_names

def get_team_ratings(league_id, season_id, weight,last10=False):
    import pandas as pd
    teams = get_comp_teams(league_id, season_id)
    team_ratings = []
    for team in teams:
        xG = get_team_stats('Expected Goals (xG)',team,season_id=season_id)
        xGA = get_opp_stats('Expected Goals (xG)',team,season_id=season_id)
        xGA = xGA.rename(columns={'Team Expected Goals (xG)': 'Opponent Expected Goals (xG)'})
        GF = get_team_stats('Goals',team,season_id=season_id)
        GA = get_opp_stats('Goals',team,season_id=season_id)
        GA = GA.rename(columns={'Team Goals': 'Opponent Goals'})
        matches = GF.merge(xG[['kickoff_datetime','Team Expected Goals (xG)']], on='kickoff_datetime', how='left')
        matches = matches.merge(GA[['kickoff_datetime','Opponent Goals']], on='kickoff_datetime', how='left')
        matches = matches.merge(xGA[['kickoff_datetime','Opponent Expected Goals (xG)']], on='kickoff_datetime', how='left')
        matches['Team Expected Goals (xG)'].fillna(matches['Team Goals'], inplace=True)
        matches['Opponent Expected Goals (xG)'].fillna(matches['Opponent Goals'], inplace=True)
        matches['Adjusted Goals'] = matches['Team Goals'] * 0.3 + matches['Team Expected Goals (xG)'] * 0.7
        matches['Adjusted Goals Against'] = matches['Opponent Goals'] * 0.3 + matches['Opponent Expected Goals (xG)'] * 0.7
        matches = matches[['kickoff_datetime','opponent','Adjusted Goals','Adjusted Goals Against']]
        if last10 == True:
            matches = matches.iloc[-10:]
            matches.reset_index(drop=True, inplace=True)
            attack_rating = matches['Adjusted Goals'].mean()
            defense_rating = matches['Adjusted Goals Against'].mean()
            team_ratings.append([team, attack_rating, defense_rating])
            continue
        matches['Weeks Since Game'] = (pd.to_datetime(matches['kickoff_datetime'].max()) - pd.to_datetime(matches['kickoff_datetime'])).dt.days // 7
        matches['Game Weight'] = weight**matches['Weeks Since Game']
        matches['Weighted Goals'] = matches['Adjusted Goals'] * matches['Game Weight']
        matches['Weighted Goals Against'] = matches['Adjusted Goals Against'] * matches['Game Weight']
        attack_rating = matches['Weighted Goals'].sum() / matches['Game Weight'].sum()
        defense_rating = matches['Weighted Goals Against'].sum() / matches['Game Weight'].sum()
        team_ratings.append([team, attack_rating, defense_rating])
    team_ratings = pd.DataFrame(team_ratings, columns=['Team', 'Attack', 'Defense'])
    team_ratings['Attack Rating'] = (team_ratings['Attack'] / team_ratings['Attack'].mean()) * 100
    team_ratings['Defense Rating'] = ((team_ratings['Defense'].mean() + (team_ratings['Defense'].mean() - team_ratings['Defense'])) / team_ratings['Defense'].mean()) * 100
    return team_ratings[['Team', 'Attack Rating', 'Defense Rating']]

def get_weightings(matches_played):
    if matches_played == 0:
        return 1, 0, 0
    elif 0 < matches_played < 3:
        return 0.8, 0.2
    elif 3 <= matches_played < 5:
        return 0.75, 0.25
    elif 5 <= matches_played < 7:
        return 0.7, 0.3
    elif 7 <= matches_played <= 10:
        return 0.65, 0.35
    elif 10 < matches_played <= 12:
        return 0.6, 0.4
    elif 12 < matches_played <= 15:
        return 0.5, 0.5
    elif 15 < matches_played <= 18:
        return 0.45, 0.55
    elif 18 < matches_played <= 20:
        return 0.4, 0.6
    elif 20 < matches_played <= 25:
        return 0.35, 0.65
    elif 25 < matches_played <= 30:
        return 0.3, 0.7
    elif 30 < matches_played <= 35:
        return 0.25, 0.75
    else:
        return 0.2, 0.8
    
    
def get_ratings(league_id, season_id, previous_season_id, matches_played):
    import pandas as pd
    prev = get_team_ratings(league_id,previous_season_id, weight=0.985)
    current = get_team_ratings(league_id,season_id, weight=0.97)
    actual_rating = []
    for team in current['Team']:
        if team not in prev['Team'].values:
            prev_attack = current[current['Team'] == team]['Attack Rating'].values[0]
            prev_defense = current[current['Team'] == team]['Defense Rating'].values[0]
            current_attack = current[current['Team'] == team]['Attack Rating'].values[0]
            current_defense = current[current['Team'] == team]['Defense Rating'].values[0]
        else:
            prev_attack = prev[prev['Team'] == team]['Attack Rating'].values[0]
            prev_defense = prev[prev['Team'] == team]['Defense Rating'].values[0]
            current_attack = current[current['Team'] == team]['Attack Rating'].values[0]
            current_defense = current[current['Team'] == team]['Defense Rating'].values[0]
        prev_weighting, current_weighting = get_weightings(matches_played)
        attack = (prev_attack * prev_weighting) + (current_attack * current_weighting)
        defense = (prev_defense * prev_weighting) + (current_defense * current_weighting)
        actual_rating.append([team, attack, defense])
    actual_rating = pd.DataFrame(actual_rating, columns=['Team', 'Attack', 'Defense'])
    actual_rating['Attack'] = (actual_rating['Attack'] / actual_rating['Attack'].mean()) * 100
    actual_rating['Defense'] = (actual_rating['Defense'] / actual_rating['Defense'].mean()) * 100
    actual_rating['Attack'] = actual_rating['Attack']
    actual_rating['Defense'] = actual_rating['Defense']
    return actual_rating

def get_average_goals(league_id, team_stats):
    import pandas as pd
    fixtures = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\fixtures.csv")
    fixtures = fixtures[fixtures['competition_id'] == league_id]
    df = fixtures[['id','home_team_id','away_team_id','kickoff_datetime']].merge(team_stats[['fixture_id','team_id','stats_type_id','value']], left_on='id', right_on='fixture_id', how='inner')
    df.drop_duplicates(subset=['id','home_team_id','away_team_id','team_id','stats_type_id'], inplace=True)
    df['Weeks Since Kickoff'] = (pd.to_datetime('now') - pd.to_datetime(df['kickoff_datetime'])).dt.days // 7
    df['Weeks Since Kickoff'] = df['Weeks Since Kickoff'].astype(int)
    df['Weight'] = 0.98**df['Weeks Since Kickoff']
    df['Weighted Value'] = df['value'] * df['Weight']
    goals = df[df['stats_type_id'] == get_stat_id('Goals')]
    goals_average = goals['Weighted Value'].sum() / goals['Weight'].sum()
    xG = df[df['stats_type_id'] == get_stat_id('Expected Goals (xG)')]
    xG_average = xG['Weighted Value'].sum() / xG['Weight'].sum()
    adjusted_goal_average = goals_average*0.3 + xG_average*0.7
    return adjusted_goal_average

def get_home_advantage(league_id,team_stats):
    import pandas as pd
    fixtures = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\fixtures.csv")
    fixtures = fixtures[fixtures['competition_id'] == league_id]
    df = fixtures[['id','home_team_id','away_team_id','kickoff_datetime']].merge(team_stats[['fixture_id','team_id','stats_type_id','value']], left_on='id', right_on='fixture_id', how='inner')
    df.drop_duplicates(subset=['id','home_team_id','away_team_id','team_id','stats_type_id'], inplace=True)
    df['Weeks Since Kickoff'] = (pd.to_datetime('now') - pd.to_datetime(df['kickoff_datetime'])).dt.days // 7
    df['Weeks Since Kickoff'] = df['Weeks Since Kickoff'].astype(int)
    df['Weight'] = 0.98**df['Weeks Since Kickoff']
    df['Weighted Value'] = df['value'] * df['Weight']
    goals = df[df['stats_type_id'] == get_stat_id('Goals')]
    goals_average = goals['Weighted Value'].sum() / goals['Weight'].sum()
    home_goals = goals[goals['team_id'] == goals['home_team_id']]
    home_goals_average = home_goals['Weighted Value'].sum() / home_goals['Weight'].sum()
    xG = df[df['stats_type_id'] == get_stat_id('Expected Goals (xG)')]
    xG_average = xG['Weighted Value'].sum() / xG['Weight'].sum()
    home_xG = xG[xG['team_id'] == xG['home_team_id']]
    home_xG_average = home_xG['Weighted Value'].sum() / home_xG['Weight'].sum()
    adjusted_goal_average = goals_average*0.3 + xG_average*0.7
    adjusted_home_goal_average = home_goals_average*0.3 + home_xG_average*0.7
    return adjusted_home_goal_average / adjusted_goal_average   

def get_draw_perc(league_id):
    import pandas as pd
    fixtures = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\fixtures.csv")
    fixtures = fixtures[fixtures['competition_id'] == league_id]
    fixtures.dropna(subset=['result_info'], inplace=True)
    fixtures.reset_index(drop=True, inplace=True)
    fixtures = fixtures[['result_info','kickoff_datetime']]
    fixtures.sort_values(by='kickoff_datetime', ascending=True, inplace=True)
    fixtures['Draw?'] = fixtures['result_info'].apply(lambda x: 1 if x == 'Game ended in draw.' else 0)
    fixtures['Weeks Since Kickoff'] = (pd.to_datetime('now') - pd.to_datetime(fixtures['kickoff_datetime'])).dt.days // 7
    fixtures['Weeks Since Kickoff'] = fixtures['Weeks Since Kickoff'].astype(int)
    fixtures['Weight'] = 0.95**(fixtures['Weeks Since Kickoff'] - 5)
    fixtures.loc[fixtures['Weeks Since Kickoff'] < 5, 'Weight'] = 1
    fixtures['Weighted Draw'] = fixtures['Draw?'] * fixtures['Weight']
    return (fixtures['Weighted Draw'].sum() / fixtures['Weight'].sum())

def get_draw_boost(ratings,average_goals, draw_perc, home_advantage):
    import numpy as np
    from scipy.stats import poisson
    draw_probs = []
    for i in range(len(ratings)):
        home_team = ratings.iloc[i]['Team']
        home_attack = ratings.iloc[i]['Attack']
        home_defense = ratings.iloc[i]['Defense']
        for i in range(len(ratings)):
            away_team = ratings.iloc[i]['Team']
            away_attack = ratings.iloc[i]['Attack']
            away_defense = ratings.iloc[i]['Defense']
            if home_team == away_team:
                continue
            home_goals = make_goal_prediction(home_attack, away_defense, average_goals) * home_advantage
            away_goals = make_goal_prediction(away_attack, home_defense, average_goals) * (2-home_advantage)
            x = np.arange(0, 9)
            y = np.arange(0, 9)
            X, Y = np.meshgrid(x, y)
            Z = poisson.pmf(X, home_goals) * poisson.pmf(Y, away_goals)
            draw_prob = np.sum(np.diag(Z))  # Diagonal
            draw_probs.append(draw_prob)

    projected_draw_prob = np.mean(draw_probs)
    draw_boost = draw_perc / projected_draw_prob
    return draw_boost

def make_round_goal_prediction(fixtures, team_ratings, average_goals, home_advantage):
    import pandas as pd
    predictions = []
    for i in range(len(fixtures)):
        home_team = fixtures.iloc[i]['home_team']
        away_team = fixtures.iloc[i]['away_team']
        home_attack_rating = team_ratings[team_ratings['Team'] == home_team]['Attack'].values[0]
        home_defense_rating = team_ratings[team_ratings['Team'] == home_team]['Defense'].values[0]
        away_attack_rating = team_ratings[team_ratings['Team'] == away_team]['Attack'].values[0]
        away_defense_rating = team_ratings[team_ratings['Team'] == away_team]['Defense'].values[0]
        home_goals = ((make_goal_prediction(home_attack_rating, away_defense_rating, average_goals)) * home_advantage).round(2)
        away_goals = ((make_goal_prediction(away_attack_rating, home_defense_rating, average_goals)) * (2-home_advantage)).round(2)
        predictions.append([home_team,home_goals, away_goals, away_team])
    return pd.DataFrame(predictions, columns=['Home Team', 'Home Goals', 'Away Goals', 'Away Team']) 

def make_goal_prediction(attack_rating, defense_rating, average_goals):
    diff = attack_rating - defense_rating
    
    if diff >= 0:
        # Keep original formula for positive differences
        return (1 + (diff/100)) * average_goals
    else:
        def_avg = average_goals / (defense_rating/100)
        return (attack_rating/100) * def_avg       

def get_season_id(fixtures, previous=False):
    if previous:
        season_id = fixtures['season_id'].min()
    else:
        season_id = fixtures['season_id'].max()
    return season_id

def get_league_id(league_name):
    import pandas as pd
    comps = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\competitions.csv")
    league_id = comps[comps['name'] == league_name]['id'].values[0]
    return league_id

def get_game_stats(fixture_id,stat_list,team_stats,home_team,away_team):
    home_id = get_team_id(home_team)
    away_id = get_team_id(away_team)
    team_stats = team_stats[team_stats['fixture_id'] == fixture_id]
    game_stats = {}
    game_stats['Home'] = home_team
    game_stats['Away'] = away_team
    for stat in stat_list:
        stat_id = get_stat_id(stat)
        df = team_stats[team_stats['stats_type_id'] == stat_id]
        try:
            game_stats['Home ' + stat] = df[df['team_id'] == home_id]['value'].values[0]
        except:
            game_stats['Home ' + stat] = 0
        try:
            game_stats['Away ' + stat] = df[df['team_id'] == away_id]['value'].values[0]
        except:
            game_stats['Away ' + stat] = 0
        game_stats['Total ' + stat] = game_stats['Home ' + stat] + game_stats['Away ' + stat]
    return game_stats

def load_model(stat):
    import pickle
    filename = "C:\\Users\\George\\Documents\\Statz.ai\\Notebooks\\PL Projections\\Model Builds\\" + stat + '_model.sav'
    model = pickle.load(open(filename, 'rb'))
    return model

def load_all_models(stat_list):
    models = {}
    for stat in stat_list:
        model = load_model(stat)
        models[stat] = model
    return models

def get_team_stat_prediction(team, opponent, stat, model, venue, comp_id=None, games=None):
    team_history = get_team_weighted_average(stat, team, 0.96,comp_id=comp_id,games=games) * calculate_team_venue_effect(team, stat, venue)
    if venue == 'H':
        opponent_venue = 'A'
    else:
        opponent_venue = 'H'
    opponent_history = get_opp_weighted_average(stat, opponent, 0.96,comp_id=comp_id,games=games) * calculate_opp_venue_effect(team, stat, opponent_venue)
    team_stat = model.predict([[team_history, opponent_history]])
    return (team_stat[0]).round(2) 

def get_team_all_stats_prediction(team, opponent, stat_list, models, venue, comp_id=None, season_id=None, games=None):
    predictions = {}
    predictions['Team'] = team
    predictions['Opponent'] = opponent
    predictions['Venue'] = venue
    for stat in stat_list:
        model = models[stat]
        predictions[stat] = get_team_stat_prediction(team, opponent, stat, model, venue, comp_id=comp_id,games=games)
    return predictions

def get_team_round_predictions(fixtures, stat_list, models, goals=False, comp_id=None, season_id=None, games=None):
    import pandas as pd
    if goals == False:
        stat_list.remove('Goals')
    round_preds = []
    for index, row in fixtures.iterrows():
        home_team_preds = get_team_all_stats_prediction(row['home_team'], row['away_team'], stat_list, models, 'H', comp_id=comp_id,games=games)
        away_team_preds = get_team_all_stats_prediction(row['away_team'], row['home_team'], stat_list, models, 'A', comp_id=comp_id,games=games)
        home_team_preds['Fouls Drawn'] = away_team_preds['Fouls']
        away_team_preds['Fouls Drawn'] = home_team_preds['Fouls']
        if goals == True:
            home_team_preds['Assists'] = (home_team_preds['Goals'] * 0.82).round(2)
            away_team_preds['Assists'] = (away_team_preds['Goals'] * 0.82).round(2)
            home_team_preds['Saves'] = away_team_preds['Shots On Target'] - away_team_preds['Goals']
            away_team_preds['Saves'] = home_team_preds['Shots On Target'] - home_team_preds['Goals']
        round_preds.append(home_team_preds)
        round_preds.append(away_team_preds)
        df = pd.DataFrame(round_preds)
    if goals == True:
        return df[['Team','Opponent','Venue','Goals','Assists'] + stat_list[1:] + ['Fouls Drawn','Saves']]
    else:
        return df[['Team','Opponent','Venue'] + stat_list[0:] + ['Fouls Drawn']] 

def get_cheat_sheet(team_projections):
    import pandas as pd
    import numpy as np
    df = {'Home Team':[],'Home Goals':[],'Away Goals':[],'Away Team':[],'Total Fouls':[],'Total Shots':[],'Total Shots On Target':[],'Total Tackles':[],'Total Corners':[],'Total Passes':[],'Home Fouls':[],'Home Shots':[],'Home Shots On Target':[],'Home Tackles':[],'Home Corners':[],'Home Passes':[],'Away Fouls':[],'Away Shots':[],'Away Shots On Target':[],'Away Tackles':[],'Away Corners':[],'Away Passes':[]}
    for fix in np.arange(0,len(team_projections),2):
        home_team = team_projections.iloc[fix]['Team']
        away_team = team_projections.iloc[fix]['Opponent']
        home_goals = team_projections.iloc[fix]['Goals']
        away_goals = team_projections.iloc[fix+1]['Goals']
        home_fouls = team_projections.iloc[fix]['Fouls'] 
        away_fouls = team_projections.iloc[fix+1]['Fouls']
        fouls = home_fouls + away_fouls
        home_shots = team_projections.iloc[fix]['Shots Total']
        away_shots = team_projections.iloc[fix+1]['Shots Total']
        shots = home_shots + away_shots
        home_shots_on_target = team_projections.iloc[fix]['Shots On Target']
        away_shots_on_target = team_projections.iloc[fix+1]['Shots On Target']
        shots_on_target = home_shots_on_target + away_shots_on_target
        home_passes = team_projections.iloc[fix]['Passes']
        away_passes = team_projections.iloc[fix+1]['Passes']
        passes = home_passes + away_passes
        home_tackles = team_projections.iloc[fix]['Tackles']
        away_tackles = team_projections.iloc[fix+1]['Tackles']
        tackles = home_tackles + away_tackles
        home_corners = team_projections.iloc[fix]['Corners']
        away_corners = team_projections.iloc[fix+1]['Corners']
        corners = home_corners + away_corners
        df['Home Team'].append(home_team)
        df['Home Goals'].append(home_goals)
        df['Away Goals'].append(away_goals)
        df['Away Team'].append(away_team)
        df['Total Fouls'].append(fouls)
        df['Total Shots'].append(shots)
        df['Total Shots On Target'].append(shots_on_target)
        df['Total Tackles'].append(tackles)
        df['Total Corners'].append(corners)
        df['Total Passes'].append(passes)
        df['Home Fouls'].append(home_fouls)
        df['Home Shots'].append(home_shots)
        df['Home Shots On Target'].append(home_shots_on_target)
        df['Home Tackles'].append(home_tackles)
        df['Home Corners'].append(home_corners)
        df['Home Passes'].append(home_passes)
        df['Away Fouls'].append(away_fouls)
        df['Away Shots'].append(away_shots)
        df['Away Shots On Target'].append(away_shots_on_target)
        df['Away Tackles'].append(away_tackles)
        df['Away Corners'].append(away_corners)
        df['Away Passes'].append(away_passes)
    cheat_sheet = pd.DataFrame(df)
    return cheat_sheet

def get_player_position(player):
    import pandas as pd
    players = pd.read_csv(r"C:\Users\George\Documents\Statz.ai\Data\players.csv")
    position = players[players['display_name'] == player]['position'].values[0]
    if position == 'goalkeeper':
        return 'GK'
    elif position == 'defender':
        return 'DEF'
    elif position == 'midfielder':
        return 'MID'
    elif position == 'attacker':
        return 'FWD'
    #elif position == 'left-back':
    #    return 'LB'
    #elif position == 'right-back':
    #    return 'RB'
    #elif position == 'centre-back':
    #    return 'CB'
    #elif position == 'defensive-midfied':
    #    return 'CDM'
    #elif position == 'central-midfied':
    #    return 'CM'
    #elif position == 'attacking-midfied':
    #    return 'CAM'
    #elif position == 'left-wing':
    #    return 'LW'
    #elif position == 'right-wing':
    #    return 'RW'
    #elif position == 'centre-forward':
    #    return 'ST'
    #elif position == 'left-midfield':
    #    return 'LM'
    #elif position == 'right-midfield':
    #    return 'RM'
    #elif position == 'secondary_striker':
    #    return 'CF'
    #else:
    return position

def get_opta_points(pl_projections, score_preds, opta_points_dict):
    import pandas as pd
    opta_points_df = {'Player':[],'Position':[],'Start?':[],'Team':[],'Opponent':[],'Venue':[],'PTS':[],'Floor PTS':[]}
    for i in range(len(pl_projections)):
        start = pl_projections['Start?'][i]
        player = pl_projections['Player'][i]
        team = pl_projections['Team'][i]
        position = pl_projections['Position'][i]
        goals = pl_projections['Goals'][i]
        assists = pl_projections['Assists'][i]
        shots_off = pl_projections['Shots Total'][i] - pl_projections['Shots On Target'][i]
        shots_on_target = pl_projections['Shots On Target'][i]
        passes = pl_projections['Passes'][i]
        interceptions = pl_projections['Interceptions'][i]
        tackles = pl_projections['Tackles'][i]
        crosses = pl_projections['Total Crosses'][i]
        yellow_cards = pl_projections['Yellow Cards'][i]
        fouls = pl_projections['Fouls'][i]
        fouls_drawn = pl_projections['Fouls Drawn'][i]
        saves = pl_projections['Saves'][i]
        goals_conceded = score_preds[score_preds['Home Team'] == team]['Away Goals'].values[0] if pl_projections['Venue'][i] == 'H' else score_preds[score_preds['Away Team'] == team]['Home Goals'].values[0]
        if position == 'GK':
            goals_conceded = goals_conceded * 6
        points = goals * opta_points_dict['Goals'] + assists * opta_points_dict['Assists'] + shots_off * opta_points_dict['Shots Off'] + shots_on_target * opta_points_dict['Shots On Target'] + passes * opta_points_dict['Passes'] + interceptions * opta_points_dict['Interceptions'] + tackles * opta_points_dict['Tackles'] + crosses * opta_points_dict['Total Crosses'] + yellow_cards * opta_points_dict['Yellow Cards'] + fouls * opta_points_dict['Fouls'] + fouls_drawn * opta_points_dict['Fouls Drawn'] + saves * opta_points_dict['Saves'] + goals_conceded * opta_points_dict['Goals Conceded']
        floor_points = shots_off * opta_points_dict['Shots Off'] + shots_on_target * opta_points_dict['Shots On Target'] + passes * opta_points_dict['Passes'] + interceptions * opta_points_dict['Interceptions'] + tackles * opta_points_dict['Tackles'] + crosses * opta_points_dict['Total Crosses'] + yellow_cards * opta_points_dict['Yellow Cards'] + fouls * opta_points_dict['Fouls'] + fouls_drawn * opta_points_dict['Fouls Drawn'] + saves * opta_points_dict['Saves'] + goals_conceded * opta_points_dict['Goals Conceded']
        opta_points_df['Player'].append(player)
        opta_points_df['Position'].append(position)
        opta_points_df['Start?'].append(start)
        opta_points_df['Team'].append(team)
        opta_points_df['Opponent'].append(pl_projections['Opponent'][i])
        opta_points_df['Venue'].append(pl_projections['Venue'][i])
        opta_points_df['PTS'].append(points)
        opta_points_df['Floor PTS'].append(floor_points)
    opta_points = pd.DataFrame(opta_points_df)
    return opta_points

def get_fpl_points(pl_projections,score_preds, fpl_points_dict_gk,fpl_points_dict_mid,fpl_points_dict_fwd,fpl_points_dict_def):
    import pandas as pd
    fpl_point_df = {'Player':[],'Position':[],'Team':[],'Opponent':[],'Venue':[],'PTS':[]}
    for i in range(len(pl_projections)):
        if pl_projections['Position'][i] == 'GK':
            fpl_points_dict = fpl_points_dict_gk
        elif pl_projections['Position'][i] == 'DEF':
            fpl_points_dict = fpl_points_dict_def
        elif pl_projections['Position'][i] == 'MID':
            fpl_points_dict = fpl_points_dict_mid
        else:
            fpl_points_dict = fpl_points_dict_fwd
        player = pl_projections['Player'][i]
        team = pl_projections['Team'][i]
        position = pl_projections['Position'][i]
        goals = pl_projections['Goals'][i]
        assists = pl_projections['Assists'][i]
        yellow_cards = pl_projections['Yellow Cards'][i]
        saves = pl_projections['Saves'][i]
        goals_conceded = score_preds[score_preds['Home Team'] == team]['Away Goals'].values[0] if pl_projections['Venue'][i] == 'H' else score_preds[score_preds['Away Team'] == team]['Home Goals'].values[0]
        fpl_points = goals * fpl_points_dict['Goals'] + assists * fpl_points_dict['Assists'] + yellow_cards * fpl_points_dict['Yellow Card'] + saves * fpl_points_dict['Saves'] + goals_conceded * fpl_points_dict['Goals Conceded']
        fpl_point_df['Player'].append(player)
        fpl_point_df['Position'].append(position)
        fpl_point_df['Team'].append(team)
        fpl_point_df['Opponent'].append(pl_projections['Opponent'][i])
        fpl_point_df['Venue'].append(pl_projections['Venue'][i])
        fpl_point_df['PTS'].append(fpl_points)
    fpl_points = pd.DataFrame(fpl_point_df)
    return fpl_points

def get_poisson_probs(projections, stats, numbers):
    from scipy.stats import poisson
    import pandas as pd
    import numpy as np
    big_df = projections[projections.columns[:5].tolist()]
    for stat in stats:
        df = projections[[stat]]
        probs = []
        for value in df[stat]:
            poisson_pred = poisson.pmf(np.arange(0, numbers.max()), value)
            for number in numbers:
                prob = 1 - poisson_pred[:number].sum().round(4)
                prob = min(prob, 0.99)
                prob = prob * 100
                if prob == 100:
                    prob = 99.99
                probs.append(prob)
        for i in range(len(numbers)):
            df[f'{stat} {numbers[i]}+'] = probs[i::len(numbers)]
        big_df = pd.concat([big_df,df],axis=1)
    return big_df
                