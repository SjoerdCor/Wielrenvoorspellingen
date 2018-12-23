# -*- coding: utf-8 -*-
"""
Created on Fri Jul 06 08:24:25 2018

@author: sjoer_000
"""

import pandas as pd
import os 
#import numpy as np
import trueskill
#%%
input_folder = r'C:\Users\sjoer_000\Documents\Willekeurige berekeningen\Tour De France\Data'
output_folder = r'C:\Users\sjoer_000\Documents\Willekeurige berekeningen\Tour De France\Output'
#%%
file_riders = 'riders_tdf_total.csv'
df = pd.read_csv(os.path.join(input_folder, file_riders))
df_stages = pd.read_csv(os.path.join(input_folder, 'stages_tour-de-france.csv'))
#df_stages_2017['stage'] = df_stages_2017.index + 1
dubbel = df[df.duplicated(subset=['Rider', 'stage', 'year'], keep=False)]
df.drop_duplicates(subset=['Rider', 'stage', 'year'], inplace=True)
#%%
ts = trueskill.TrueSkill(draw_probability=0.001, backend='mpmath')

df_ratings = pd.DataFrame(index=df['Rider'].unique(), columns=[1, 2, 3, 4, 5])
df_ratings = df_ratings.applymap(lambda x: trueskill.Rating())
#%%
df_ratings_list = []
for y in range(2013, 2018):
    df_y = df[df['year']==y].copy()
    for i in range(df_y['stage'].max()):
        print(y, i)
        df_stage = df_y[df_y['stage']==i+1].copy()
        df_stage.loc[df_stage['Rank_stage'] > 15, 'Rank_stage'] = 16

        stage_type = df_stages.loc[(df_stages['stage']==i) & (df_stages['year']==y), 
                                   'stage_type']
        df_stage = df_stage.merge(df_ratings, how='left', left_on='Rider', 
                                  right_index=True, suffixes=('', '_x'))
        df_stage['Rating_after_stage'] = [x[0] for x in ts.rate(df_stage[stage_type].values, 
                ranks=df_stage['Rank_stage'].fillna(16))] 
        df_ratings = df_ratings.merge(df_stage[['Rider', 'Rating_after_stage']], 
                                      how='left', left_index=True, right_on='Rider')
        df_ratings[int(stage_type)] = df_ratings['Rating_after_stage'].fillna(df_ratings[int(stage_type)])
        df_ratings.set_index('Rider', inplace=True)
        df_ratings.drop(columns=['Rating_after_stage'], inplace=True)
    df_ratings_list.append(df_ratings)
#%%
#%%
df_ratings_2 = df_ratings.applymap(lambda x: x.mu)
df_ratings_2 = df_ratings_2[~((df_ratings_2>24.999) & (df_ratings_2<25.001)).all(axis=1)]
df_ratings_2.corr()
sns.jointplot(x=1, y=4, data=df_ratings_2)
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
