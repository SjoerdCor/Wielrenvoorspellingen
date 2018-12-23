# -*- coding: utf-8 -*-
"""
Created on Fri Jul 06 10:49:55 2018

@author: sjoer_000
"""
import pandas as pd
import os
import numpy as np
from lpsolve55 import *
#%%
input_folder = 'C:\Users\sjoer_000\Documents\Willekeurige berekeningen\Tour De France\Data'
output_folder = 'C:\Users\sjoer_000\Documents\Willekeurige berekeningen\Tour De France\Output'

jaar = 2017
df_predictions = pd.read_csv(os.path.join(input_folder, 'prediction_%s.csv' % jaar))
#%%
def bepaal_team(max_kosten, aantal_renners, df_prediction):
    ''' 
    Riders must have 'prediction': expected nr of points, and
    'Waarde': the cost of one rider
    '''
    # Zet model klaar
    lp = lpsolve('make_lp', 0, len(df_prediction))
    lpsolve('set_verbose', lp, 'IMPORTANT')
    
    # Maximaliseer het aantal punten
    lpsolve('set_obj_fn', lp, df_prediction['prediction'].values)
    lpsolve('set_maxim', lp)
    
    # Betaal minder dan max kosten
    lpsolve('add_constraint', lp, df_prediction['Waarde'].values, 'LE', max_kosten)
    lpsolve('set_row_name', lp, 1,'Kosten')
    
    # Pak precies juiste aantal renners
    lpsolve('add_constraint', lp, np.ones_like(df_prediction['Waarde'].values), 'EQ', aantal_renners)
    lpsolve('set_row_name', lp, 2,'Aantal')
    
    # Alle variabelen zijn binary
    for j in range(len(df_prediction)):
        lpsolve('set_binary',lp,j+1,1) 
    
    # Solve
    lpsolve('write_lp', lp, 'warehouse.lp')
    ret = lpsolve('solve', lp)
    assert ret==0, 'Solving failed!'
    
    # Geef resultaten
    inds_chosen_riders = lpsolve('get_variables', lp)[0]
    chosen_riders = df_prediction[map(bool, inds_chosen_riders)].copy()
    chosen_riders['ROI'] = chosen_riders['prediction'] / chosen_riders['Waarde']
    assert len(chosen_riders)==aantal_renners, 'Onjuist aantal renners!'
    assert chosen_riders['Waarde'].sum() <= max_kosten, 'Te hoge kosten!'
    return chosen_riders

norm_text = lambda t: unicodedata.normalize('NFKD', t).encode('ascii', 'ignore')
capitalize = lambda s: " ".join(w.capitalize() for w in s.split())

def correct_rider_names(names):
    names = names.str.replace(',', '')
    names = names.str.lower().apply(capitalize)
    try:
        names = names.apply(norm_text)
    except TypeError: 
        print('Normalize didnt work')
    return names

#%%
if jaar == 2018: max_kosten = 150
elif jaar == 2017: max_kosten = 100
elif jaar == 2016: max_kosten = 125
else: raise ValueError('kosten unknown')
chosen_riders = bepaal_team(max_kosten, 15, df_predictions)
print('Verwacht aantal punten: %.2f, kosten: %.1f'% 
      (chosen_riders['prediction'].sum(), chosen_riders['Waarde'].sum()))

#%%
tour_rider_points = pd.read_csv(os.path.join(input_folder, 'rider_points.csv'))
chosen_riders['year'] = jaar
chosen_riders = chosen_riders.merge(tour_rider_points[['BIB', 'year', 'score']], how='left')
#assert chosen_riders['score'].notnull().all()
chosen_riders['Actual_ROI'] = chosen_riders['score'] /chosen_riders['Waarde']
print('Aantal punten: %.0f' % chosen_riders['score'].sum())


#%%
chosen_riders.to_excel(os.path.join(output_folder, 'team_%s.xlsx'%jaar), index=False)
