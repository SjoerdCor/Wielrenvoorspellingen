# -*- coding: utf-8 -*-
"""
Created on Fri Jul 06 08:24:25 2018

@author: sjoer_000
"""

import pandas as pd
import os 
import numpy as np
#%%
input_folder = 'C:\Users\sjoer_000\Documents\Willekeurige berekeningen\Tour De France\Data'
output_folder = 'C:\Users\sjoer_000\Documents\Willekeurige berekeningen\Tour De France\Output'
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
gc_end_scores = np.array(stage_scores)*2
green_end_scores = range(20, 0, -2)
unimportant_jerseys_end_score = [10, 7, 5, 3, 1]
df_end_scores = pd.DataFrame([gc_end_scores, green_end_scores, 
                          unimportant_jerseys_end_score]).T

df_end_scores.columns = ['gc_end_scores', 'green_end_scores', 
                         'unimportant_jerseys_end_score' ]
df_end_scores.fillna(0, inplace=True)

df_extra_class_scores = pd.DataFrame([])
df_extra_class_scores['gc_extra_scores'] = df_end_scores['gc_end_scores']\
     - df_stage_scores['gc_stage_scores']
df_extra_class_scores['green_extra_scores'] = df_end_scores['green_end_scores']\
     - df_stage_scores['green_stage_scores']
df_extra_class_scores['polka_extra_scores'] = df_end_scores['unimportant_jerseys_end_score']\
     - df_stage_scores['polka_stage_scores']
df_extra_class_scores['youth_extra_scores'] = df_end_scores['unimportant_jerseys_end_score']\
     - df_stage_scores['youth_stage_scores']
df_extra_class_scores['rank'] = df_extra_class_scores.index + 1
#%%
file_riders = 'riders_tdf_total.csv'
df = pd.read_csv(os.path.join(input_folder, file_riders))
df = df.merge(df_stage_scores[['rank', 'stage_scores']], how='left', 
         left_on='Rank_stage', right_on='rank')
df = df.merge(df_stage_scores[['rank', 'gc_stage_scores']], how='left', 
         left_on='Rank_gc', right_on='rank')
df = df.merge(df_stage_scores[['rank', 'green_stage_scores']], how='left', 
         left_on='Rank_points', right_on='rank')
df = df.merge(df_stage_scores[['rank', 'polka_stage_scores']], how='left', 
         left_on='Rank_polka', right_on='rank')
df = df.merge(df_stage_scores[['rank', 'youth_stage_scores']], how='left', 
         left_on='Rank_youth', right_on='rank')
#%%
df['last_stage'] = df.groupby('year')['stage'].transform(max)
df_last_stages = df[df['stage'] == df['last_stage']].copy()
df_last_stages = df_last_stages.merge(df_extra_class_scores[['rank', 'gc_extra_scores']],
                                      how='left', left_on='Rank_gc', right_on='rank')
df_last_stages = df_last_stages.merge(df_extra_class_scores[['rank', 'green_extra_scores']],
                                      how='left', left_on='Rank_points', right_on='rank')
df_last_stages = df_last_stages.merge(df_extra_class_scores[['rank', 'polka_extra_scores']],
                                      how='left', left_on='Rank_polka', right_on='rank')
df_last_stages = df_last_stages.merge(df_extra_class_scores[['rank', 'youth_extra_scores']],
                                      how='left', left_on='Rank_youth', right_on='rank')

rank_columns = [c for c in df_last_stages.columns if 'rank' in c]
rank_columns.extend([c for c in df_last_stages.columns if 'rank' in c])
rank_columns = list(set(rank_columns))
df_no_last_stages = df[df['stage'] != df['last_stage']].copy()
df_last_stages.drop(columns=rank_columns, inplace=True)
df_no_last_stages.drop(columns=rank_columns, inplace=True)


df = pd.concat([df_last_stages, df_no_last_stages])
df.fillna(0, inplace=True)
df['score'] = df.filter(like='scores').sum(axis=1)
#%%
score_columns = [c for c in df.columns if 'score' in c]
tour_rider_points = df.groupby(['Age', 'BIB', 'Rider', 'year'], as_index=False)[score_columns].sum()
tour_rider_points.to_csv(os.path.join(output_folder, 'rider_points.csv'))
