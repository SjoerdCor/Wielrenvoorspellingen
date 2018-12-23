# -*- coding: utf-8 -*-
"""
Created on Fri Jul 06 18:26:06 2018

@author: sjoer_000
"""

import pandas as pd
import glob
import os
#%%
input_folder = 'C:\Users\sjoer_000\Documents\Willekeurige berekeningen\Tour De France\Data\TdF historical details'
output_folder = 'C:\Users\sjoer_000\Documents\Willekeurige berekeningen\Tour De France\Output'

#%%
def create_1_df(files, individual=True):
    historical_files = glob.glob(os.path.join(input_folder, files))
    df = pd.DataFrame([])
    for f in historical_files:
        df = df.append(pd.read_csv(f)) 
    
    if individual: 
        return_columns = ['Age', 'BIB', 'Rider', 'Rnk', 'stage', 'year']        
    else:
        return_columns = ['Team', 'Rnk', 'stage', 'year']
    df = df[return_columns].copy()
    df.rename(columns={'Rnk': 'Rank_%s' % files[:-6]}, inplace=True)
    return df
#%%
df_stage = create_1_df('stage_*.csv')
df_gc = create_1_df('gc_*.csv')
df_points = create_1_df('points_*.csv')
df_youth = create_1_df('youth_*.csv')
df_polka = create_1_df('polka_*.csv')
df_team = create_1_df('team_*.csv', False)
#%%
# TODO: uitzoeken waarom 2003 - 4 en 2016 - 1 misgaan
# TODO: Mergen op rugnummer = BIB
df_total = df_stage.merge(df_gc, how='outer')
df_total = df_total.merge(df_points, how='outer')
df_total = df_total.merge(df_youth, how='outer')
df_total = df_total.merge(df_polka, how='outer')
#%%
# TODO: find out why ~1500 are lost during to_numeric
df_total.replace('\*', '', regex=True, inplace=True)
rank_columns = [c for c in df_total.columns if 'Rank_' in c]
for c in rank_columns:
    df_total[c] = pd.to_numeric(df_total[c], errors='coerce', downcast='integer')
    
df_total.to_csv(os.path.join(output_folder, 'riders_tdf_total.csv'), index=False)
df_team.to_csv(os.path.join(output_folder, 'teams_tdf_total.csv'), index=False)