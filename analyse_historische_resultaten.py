# -*- coding: utf-8 -*-
"""
Created on Sat Jul 07 12:50:12 2018

@author: sjoer_000
"""
import pandas as pd
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# TODO: correlatie vorigaantalpunten met was_teamlead
#%%
input_folder = 'C:\Users\sjoer_000\Documents\Willekeurige berekeningen\Tour De France\Data'
output_folder = 'C:\Users\sjoer_000\Documents\Willekeurige berekeningen\Tour De France\Output'
#%%
tour_rider_points = pd.read_csv(os.path.join(input_folder, 'rider_points.csv'))
#%%
tour_rider_points['Has_gc_end_points'] = tour_rider_points.groupby('Rider')\
['gc_extra_scores'].transform(max)
tour_rider_points['Has_gc_end_points'] = (tour_rider_points['Has_gc_end_points'] > 30).astype(int)
#%%
tour_description = pd.read_csv(os.path.join(input_folder, 'tour_description.csv'))
tour_description = tour_description[tour_description['MountainStage'] > 3]

tour_rider_points = tour_rider_points.merge(tour_description, how='left')
#%%
sns.lmplot(x='TeamTimeTrial', y='score', hue='team_bib',
               data=tour_rider_points)
#%%
tour_rider_points.sort_values(['Rider', 'year'], inplace=True)

tour_rider_points_shift = tour_rider_points.shift()

tour_rider_points['score_diff'] = tour_rider_points['score'].diff()
tour_rider_points['score_diff_2y'] = tour_rider_points['score'].diff(2)

mask = tour_rider_points_shift['Rider'] != tour_rider_points['Rider']
mask_2y = tour_rider_points['Rider'].shift(2) != tour_rider_points['Rider']

tour_rider_points_shift.loc[mask, 'score'] = np.nan
tour_rider_points_shift.loc[mask, 'score_diff'] = np.nan
tour_rider_points_shift.loc[mask_2y, 'score_diff_2y'] = np.nan
#%%
tour_rider_points['nr_tour_starts'] = tour_rider_points.groupby('Rider').cumcount()
sns.regplot(x='nr_tour_starts', y='score', data=tour_rider_points)
#%%
for c in tour_rider_points.columns[3:-3]:
    print(c, tour_rider_points[c].autocorr())

#%%
sns.violinplot(y='score_diff', data=tour_rider_points)
sns.regplot('score_diff', tour_rider_points['score_diff_2y']- tour_rider_points['score_diff'], data=tour_rider_points)
np.corrcoef(tour_rider_points.loc[~mask_2y, 'score_diff'], 
            tour_rider_points.loc[~mask_2y, 'score_diff_2y']- tour_rider_points.loc[~mask_2y, 'score_diff'])
#%%
sns.regplot(tour_rider_points_shift['score'], tour_rider_points['score'])
np.corrcoef(tour_rider_points_shift.loc[~mask, 'score'], tour_rider_points.loc[~mask, 'score'])
#%%
tour_rider_points['BIB'].fillna(0, inplace=True)
tour_rider_points['last_digit_bib'] = tour_rider_points['BIB'].astype(int)\
    .astype(str).str[-1:].astype(int)

sns.factorplot(x='last_digit_bib', y='score', data= tour_rider_points)
#%%
tour_rider_points['team_bib'] = tour_rider_points['BIB'].astype(int)\
    .astype(str).str[:-1].fillna('0').replace('', '0').astype(int)
sns.factorplot(x='team_bib', y='score', data= tour_rider_points)

#%%
tour_rider_points['Age'].clip(21, 35, inplace=True)
bins = range(tour_rider_points['Age'].min(), tour_rider_points['Age'].max() + 2, 2)
tour_rider_points['Age_binned'] = pd.cut(tour_rider_points['Age'], bins)
sns.factorplot(x='Age_binned', y='score', data=tour_rider_points)
plt.xticks(rotation=70)
#%%

dauphine_rider_points = pd.read_csv(os.path.join(input_folder, 
                                                 'dauphine_rider_points.csv'))
dauphine_rider_points.rename(columns={'stage_scores': 'dauphine_scores'}, 
                             inplace=True)
tour_rider_points = tour_rider_points.merge(dauphine_rider_points, how='left')
sns.regplot(x='dauphine_scores', y='score', data=tour_rider_points)

#%%
suisse_rider_points = pd.read_csv(os.path.join(input_folder, 
                                                 'suisse_rider_points.csv'))
suisse_rider_points.rename(columns={'stage_scores': 'suisse_scores'}, 
                             inplace=True)
tour_rider_points = tour_rider_points.merge(suisse_rider_points, how='left')
sns.regplot(x='suisse_scores', y='score', data=tour_rider_points)
#%%
california_rider_points = pd.read_csv(os.path.join(input_folder, 
                                                 'california_rider_points.csv'))
california_rider_points.rename(columns={'stage_scores': 'california_scores'}, 
                             inplace=True)
tour_rider_points = tour_rider_points.merge(california_rider_points, how='left')
sns.regplot(x='california_scores', y='score', data=tour_rider_points)
#%%
qatar_rider_points = pd.read_csv(os.path.join(input_folder, 
                                                 'qatar_rider_points.csv'))
qatar_rider_points.rename(columns={'stage_scores': 'qatar_scores'}, 
                             inplace=True)
tour_rider_points = tour_rider_points.merge(qatar_rider_points, how='left')
sns.regplot(x='qatar_scores', y='score', data=tour_rider_points)

#%%
giro_rider_points = pd.read_csv(os.path.join(input_folder, 
                                            'giro_rider_points.csv'))
tour_rider_points = tour_rider_points.merge(giro_rider_points, how='left')
tour_rider_points['nr_stages_giro'].fillna(0, inplace=True)
tour_rider_points['Giro_cycled'] = (tour_rider_points['nr_stages_giro'] > 0).astype(int)
sns.factorplot(x='Giro_cycled', y='score', data=tour_rider_points)
plt.show()
sns.regplot(x='stages_cycled', y='score', data=tour_rider_points)
plt.show()
sns.regplot(x='Giro_max_total', y='score', data=tour_rider_points)
