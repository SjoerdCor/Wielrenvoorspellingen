# -*- coding: utf-8 -*-
"""
Created on Sat Jul 07 20:07:28 2018

@author: sjoer_000
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Jul 07 18:17:56 2018

@author: sjoer_000
"""

import pandas as pd
import numpy as np
import glob
import os

#%%
input_folder = 'C:\Users\sjoer_000\Documents\Willekeurige berekeningen\Tour De France\Data\Giro historical details'
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
df_stage.replace('\*', '', regex=True, inplace=True)
rank_columns = [c for c in df_stage.columns if 'Rank_' in c]
for c in rank_columns:
    df_stage[c] = pd.to_numeric(df_stage[c], errors='coerce', downcast='integer')
#%%
stage_scores = [35, 30, 26, 24, 22, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6]
important_jersey_stage_scores = range(10, 0, -1)
uninmportant_jersey_stage_scores = range(5, 0, -1)
df_stage_scores = pd.DataFrame([stage_scores, important_jersey_stage_scores, 
                                important_jersey_stage_scores, 
                                uninmportant_jersey_stage_scores,
                          uninmportant_jersey_stage_scores]).T

df_stage_scores.columns = ['stage_scores', 'gc_stage_scores', 'green_stage_scores',
                           'polka_stage_scores', 'youth_stage_scores']
df_stage_scores['rank'] = df_stage_scores.index+1

df_stage_scores.fillna(0, inplace=True)

#%%
df = df_stage.merge(df_stage_scores[['rank', 'stage_scores']], how='left', 
         left_on='Rank_stage', right_on='rank')

giro_rider_points = df.groupby(['Rider', 'year'], as_index=False)\
.agg({'stage_scores': 'sum', 'Age': 'count'})

giro_rider_points['cummax'] = giro_rider_points.groupby('Rider')['stage_scores'].cummax(0)


giro_rider_points.rename(columns={'Age': 'nr_stages_giro', 'stage_scores': 
    'stage_scores_giro', 'cummax': 'Giro_max_total'}, inplace=True)

giro_rider_points.to_csv(os.path.join(output_folder, 'giro_rider_points.csv'), index=False)
#
#
#df_giro = df_stage.groupby(['Rider', 'year'], as_index=False)
