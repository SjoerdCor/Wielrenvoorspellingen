# -*- coding: utf-8 -*-
"""
Created on Fri Jul 06 10:49:55 2018

@author: sjoer_000
"""
import os

import pandas as pd
import pulp
#%%
INPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'Data')
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'Output')

JAAR = 2018
DF_PREDICTIONS = pd.read_csv(os.path.join(INPUT_FOLDER, 'prediction_{jaar}.csv'))
#%%
def bepaal_team(df_prediction, max_kosten, aantal_renners):
    '''
    Selects the team with the highest predicted score with constraints

    Uses linear programming. Selects riders based on
    df_prediction: contains riders, costs (in column 'Waarde') and predicted score
    ('prediction')
    max_kosten: maximum the riders can cost tomorrow
    aantal_renners: the exact number of riders that a team should contain
    '''

    prob = pulp.LpProblem('Rijderselectie', pulp.LpMaximize)

    riders = df_prediction['Rider'].values.tolist()
    kosten_dict = df_prediction.set_index('Rider').to_dict()['Waarde']
    punten_dict = df_prediction.set_index('Rider').to_dict()['prediction']

    # Rijder kan 0 of 1 x in selectie zitten
    rijder_geselecteerd = pulp.LpVariable.dict('Rider', riders, 0, 1, 'Integer')
    
    
    # Optimize for predicted points
    prob += pulp.lpSum([rijder_geselecteerd[i] * punten_dict[i] for i in riders]), 'Totaal aantal punten'
    
    prob += pulp.lpSum([rijder_geselecteerd[i] for i in riders]) == aantal_renners, 'Precies aantal renners in ploeg'
    prob += pulp.lpSum([rijder_geselecteerd[i] * kosten_dict[i] for i in riders]) <= max_kosten, 'Renners kosten samen niet meer dan max'

    prob.writeLP("Wielrenselectie.lp")
    prob.solve()

    assert pulp.LpStatus[prob.status] == 'Optimal', 'Optimization failed!'

    chosen_riders = df_prediction[[bool(v.varValue) for v in prob.variables()]]
    return chosen_riders
#%%
MAX_KOSTEN_PER_JAAR = {2018: 150, 2017:100, 2016: 125}
SELECTION = bepaal_team(MAX_KOSTEN_PER_JAAR[JAAR], 15, DF_PREDICTIONS)

print(SELECTION[['BIB', 'Rider']])
print(f'Aantal renners: {len(SELECTION)}')
print(f'Tot kosten: {SELECTION["Waarde"].sum()}')
print(f'Verwachte score: {SELECTION["prediction"].sum()}')
#%%
SELECTION.to_excel(os.path.join(OUTPUT_FOLDER, f'team_{JAAR}.xlsx'), index=False)
