import os
import pandas as pd
import glob
from datetime import date
import numpy as np

def standings(data,ku,grup):
  uk = data.copy()
  uk = uk[uk['KU']==ku]
  uk = uk[uk['Grup']==grup].reset_index(drop=True)
  uk = uk[['Match', 'Result']]
  uk = uk.groupby(['Match', 'Result'], as_index=False).nunique()

  uk['Home'] = uk['Match'].str.split(' -').str[0]
  uk['Away'] = uk['Match'].str.split('- ').str[1]
  uk['FTHG'] = uk['Result'].str.split(' -').str[0]
  uk['FTAG'] = uk['Result'].str.split('- ').str[1]
  uk['FTHG'] = uk['FTHG'].astype(int)
  uk['FTAG'] = uk['FTAG'].astype(int)

  uk =  uk[['Home', 'Away', 'FTHG', 'FTAG']]

  df_results = uk.copy()
  teams = set(df_results['Home']).union(set(df_results['Away']))
  stats = {team: {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'Pts': 0} for team in teams}

  def update_stats(team, played, win, draw, loss, gf, ga, pts):
    stats[team]['P'] += played
    stats[team]['W'] += win
    stats[team]['D'] += draw
    stats[team]['L'] += loss
    stats[team]['GF'] += gf
    stats[team]['GA'] += ga
    stats[team]['Pts'] += pts

  for index, row in df_results.iterrows():
    home = row['Home']
    away = row['Away']
    fthg = row['FTHG']
    ftag = row['FTAG']

    if fthg > ftag:
      update_stats(home, 1, 1, 0, 0, fthg, ftag, 3)
      update_stats(away, 1, 0, 0, 1, ftag, fthg, 0)
    elif ftag > fthg:
      update_stats(home, 1, 0, 0, 1, fthg, ftag, 0)
      update_stats(away, 1, 1, 0, 0, ftag, fthg, 3)
    else:
      update_stats(home, 1, 0, 1, 0, fthg, ftag, 1)
      update_stats(away, 1, 0, 1, 0, ftag, fthg, 1)

  df_standings = pd.DataFrame.from_dict(stats, orient='index').reset_index().rename(columns={'index': 'Team'})
  df_standings['GD'] = df_standings['GF'] - df_standings['GA']

  def calculate_h2h_stats(tied_teams, df_all_results):
    h2h_matches = df_all_results[
        (df_all_results['Home'].isin(tied_teams)) &
        (df_all_results['Away'].isin(tied_teams))
    ].copy()

    h2h_stats = {team: {'H2H_Pts': 0, 'H2H_GF': 0, 'H2H_GA': 0} for team in tied_teams}

    for _, row in h2h_matches.iterrows():
        home, away, fthg, ftag = row['Home'], row['Away'], row['FTHG'], row['FTAG']

        pts_home, pts_away = (3, 0) if fthg > ftag else ((0, 3) if ftag > fthg else (1, 1))

        h2h_stats[home]['H2H_Pts'] += pts_home
        h2h_stats[away]['H2H_Pts'] += pts_away

        h2h_stats[home]['H2H_GF'] += fthg
        h2h_stats[home]['H2H_GA'] += ftag
        h2h_stats[away]['H2H_GF'] += ftag
        h2h_stats[away]['H2H_GA'] += fthg

    df_h2h = pd.DataFrame.from_dict(h2h_stats, orient='index').reset_index().rename(columns={'index': 'Team'})
    df_h2h['H2H_GD'] = df_h2h['H2H_GF'] - df_h2h['H2H_GA']
    return df_h2h

  def custom_sort(df_standings, df_all_results):
    df_grouped = df_standings.groupby('Pts')
    sorted_groups = []

    for pts in sorted(df_grouped.groups.keys(), reverse=True):
      group = df_grouped.get_group(pts).copy()

      if len(group) > 1:
        tied_teams = group['Team'].tolist()
        df_h2h = calculate_h2h_stats(tied_teams, df_all_results)

        df_tied = pd.merge(group, df_h2h, on='Team', how='left')

        df_tied_sorted = df_tied.sort_values(by=['H2H_Pts', 'H2H_GD', 'H2H_GF', 'GD', 'GF'], ascending=False)

        sorted_groups.append(df_tied_sorted[df_standings.columns])
      else:
        group_sorted = group.sort_values(by=['GD', 'GF'], ascending=False)
        sorted_groups.append(group_sorted)

    return pd.concat(sorted_groups).reset_index(drop=True)

  df_final_standings = custom_sort(df_standings, df_results)

  df_final_standings = df_final_standings[['Team', 'P', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']]
  df_final_standings.insert(0, 'Pos', range(1, 1 + len(df_final_standings)))

  return df_final_standings

def standings_chart(data,ku,grup):
  uk = data.copy()
  uk = uk[uk['KU']==ku]
  uk = uk[uk['Grup']==grup].reset_index(drop=True)
  uk = uk[['Match', 'Result','Gameweek']]
  uk = uk.groupby(['Match', 'Result', 'Gameweek'], as_index=False).nunique()

  uk['Home'] = uk['Match'].str.split(' -').str[0]
  uk['Away'] = uk['Match'].str.split('- ').str[1]
  uk['FTHG'] = uk['Result'].str.split(' -').str[0]
  uk['FTAG'] = uk['Result'].str.split('- ').str[1]
  uk['FTHG'] = uk['FTHG'].astype(int)
  uk['FTAG'] = uk['FTAG'].astype(int)

  uk =  uk[['Home', 'Away', 'FTHG', 'FTAG', 'Gameweek']]

  df_results = uk.copy()
  teams = sorted(list(set(df_results['Home']).union(set(df_results['Away']))))
  max_gameweek = df_results['Gameweek'].max()
  num_teams = len(teams)

  def calculate_h2h_stats(tied_teams, df_all_results):
    h2h_matches = df_all_results[
        (df_all_results['Home'].isin(tied_teams)) &
        (df_all_results['Away'].isin(tied_teams))
        ].copy()

    h2h_stats = {team: {'H2H_Pts': 0, 'H2H_GF': 0, 'H2H_GA': 0} for team in tied_teams}

    for _, row in h2h_matches.iterrows():
      home, away, fthg, ftag = row['Home'], row['Away'], row['FTHG'], row['FTAG']
      pts_home, pts_away = (3, 0) if fthg > ftag else ((0, 3) if ftag > fthg else (1, 1))

      if home in tied_teams:
        h2h_stats[home]['H2H_Pts'] += pts_home
        h2h_stats[home]['H2H_GF'] += fthg
        h2h_stats[home]['H2H_GA'] += ftag
      if away in tied_teams:
        h2h_stats[away]['H2H_Pts'] += pts_away
        h2h_stats[away]['H2H_GF'] += ftag
        h2h_stats[away]['H2H_GA'] += fthg

    df_h2h = pd.DataFrame.from_dict(h2h_stats, orient='index').reset_index().rename(columns={'index': 'Team'})
    df_h2h['H2H_GD'] = df_h2h['H2H_GF'] - df_h2h['H2H_GA']
    return df_h2h

  def custom_sort(df_current_standings, df_matches_so_far):
    df_current_standings['GD'] = df_current_standings['GF'] - df_current_standings['GA']

    df_grouped = df_current_standings.groupby('Pts')
    sorted_groups = []

    for pts in sorted(df_grouped.groups.keys(), reverse=True):
      group = df_grouped.get_group(pts).copy()

      if len(group) > 1:
        tied_teams = group['Team'].tolist()
        df_h2h = calculate_h2h_stats(tied_teams, df_matches_so_far)
        df_tied = pd.merge(group, df_h2h, on='Team', how='left')

        df_tied[['H2H_Pts', 'H2H_GF', 'H2H_GA', 'H2H_GD']] = df_tied[['H2H_Pts', 'H2H_GF', 'H2H_GA', 'H2H_GD']].fillna(0)
        df_tied_sorted = df_tied.sort_values(by=['H2H_Pts', 'H2H_GD', 'H2H_GF', 'GD', 'GF'], ascending=False,kind='mergesort')

        sorted_groups.append(df_tied_sorted[df_current_standings.columns])
      else:
        group_sorted = group.sort_values(by=['GD', 'GF'], ascending=False)
        sorted_groups.append(group_sorted)

    return pd.concat(sorted_groups).reset_index(drop=True)

  position_history = {team: [] for team in teams}
  initial_stats = {team: {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'Pts': 0} for team in teams}
  df_current_stats = pd.DataFrame.from_dict(initial_stats, orient='index').reset_index().rename(columns={'index': 'Team'})

  for gw in range(1, max_gameweek + 1):
    df_matches_so_far = df_results[df_results['Gameweek'] <= gw]
    gw_stats = {team: {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'Pts': 0} for team in teams}

    for _, row in df_matches_so_far.iterrows():
      home, away, fthg, ftag = row['Home'], row['Away'], row['FTHG'], row['FTAG']

      if fthg > ftag:
        gw_stats[home]['P'] += 1; gw_stats[home]['W'] += 1; gw_stats[home]['GF'] += fthg; gw_stats[home]['GA'] += ftag; gw_stats[home]['Pts'] += 3
        gw_stats[away]['P'] += 1; gw_stats[away]['L'] += 1; gw_stats[away]['GF'] += ftag; gw_stats[away]['GA'] += fthg
      elif ftag > fthg:
        gw_stats[home]['P'] += 1; gw_stats[home]['L'] += 1; gw_stats[home]['GF'] += fthg; gw_stats[home]['GA'] += ftag
        gw_stats[away]['P'] += 1; gw_stats[away]['W'] += 1; gw_stats[away]['GF'] += ftag; gw_stats[away]['GA'] += fthg; gw_stats[away]['Pts'] += 3
      else:
        gw_stats[home]['P'] += 1; gw_stats[home]['D'] += 1; gw_stats[home]['GF'] += fthg; gw_stats[home]['GA'] += ftag; gw_stats[home]['Pts'] += 1
        gw_stats[away]['P'] += 1; gw_stats[away]['D'] += 1; gw_stats[away]['GF'] += ftag; gw_stats[away]['GA'] += fthg; gw_stats[away]['Pts'] += 1

    df_gw_standings = pd.DataFrame.from_dict(gw_stats, orient='index').reset_index().rename(columns={'index': 'Team'})
    df_gw_standings['GD'] = df_gw_standings['GF'] - df_gw_standings['GA']

    df_ranked_standings = custom_sort(df_gw_standings, df_matches_so_far)
    df_ranked_standings['Pos'] = range(1, num_teams + 1)

    for _, row in df_ranked_standings.iterrows():
      position_history[row['Team']].append(row['Pos'])

  gameweek_index = [f"GW {gw}" for gw in range(1, max_gameweek + 1)]
  df_position_history = pd.DataFrame(position_history, index=gameweek_index)

  df_position_history = df_position_history.T
  latest_gameweek_col = f"GW {max_gameweek}"
  df_position_history = df_position_history.sort_values(by=latest_gameweek_col, ascending=True)
  df_position_history.index.name = 'Team'
  df_position_history.reset_index(inplace=True)

  return df_position_history
