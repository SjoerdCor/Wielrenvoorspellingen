# -*- coding: utf-8 -*-
"""
Created on Sat Jul 07 12:37:55 2018

@author: sjoer_000
"""

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn import linear_model
from sklearn import model_selection
from sklearn.externals import joblib
from sklearn import preprocessing

# TODO: schalen naar concurrentie (per groep klimmer/tijdrijder/sprinter)
# TODO: beter afhandelen missende data, mss schatten op basis van andere data?
#%%
input_folder = 'C:\Users\sjoer_000\Documents\Willekeurige berekeningen\Tour De France\Data'
output_folder = 'C:\Users\sjoer_000\Documents\Willekeurige berekeningen\Tour De France\Output'
#%%
tour_rider_points = pd.read_csv(os.path.join(input_folder, 'rider_points.csv'))

tour_rider_points.sort_values(['Rider', 'year'], inplace=True)

tour_rider_points['score_shift'] = tour_rider_points['score'].shift()
tour_rider_points['score_shift_2'] = tour_rider_points['score'].shift(2)
tour_rider_points['score_shift_3'] = tour_rider_points['score'].shift(2)

tour_rider_points['score_diff'] = tour_rider_points['score'].diff().shift()

mask = tour_rider_points['Rider'].shift() != tour_rider_points['Rider']
mask_2 = tour_rider_points['Rider'].shift(2) != tour_rider_points['Rider']
mask_3 = tour_rider_points['Rider'].shift(3) != tour_rider_points['Rider']

tour_rider_points.loc[mask, 'score_shift'] = np.nan
tour_rider_points.loc[mask_2, 'score_shift_2'] = np.nan
tour_rider_points.loc[mask_3, 'score_shift_3'] = np.nan
tour_rider_points.loc[mask_2, 'score_diff'] = np.nan

# TODO: Deze slimmer imputeren! Bv. gemiddelde ipv 0
#tour_rider_points['score_shift'].fillna(tour_rider_points['score_shift'].mean(), inplace=True)
#tour_rider_points['score_shift_2'].fillna(tour_rider_points['score_shift_2'].mean(), inplace=True)

#%%
tour_rider_points['BIB'].fillna(0, inplace=True)
tour_rider_points['last_digit_bib'] = tour_rider_points['BIB'].astype(int)\
    .astype(str).str[-1:].astype(int)
tour_rider_points['is_teamlead'] = (tour_rider_points['last_digit_bib'] == 1).astype(int) * 40
#%%
tour_rider_points['team_bib'] = tour_rider_points['BIB'].astype(int)\
    .astype(str).str[:-1].fillna('0').replace('', '0').astype(int)
tour_rider_points['team_bib'].clip(0, 22, inplace=True)
#%%
tour_rider_points['Age'].clip(21, 35, inplace=True)
#%%
dauphine_rider_points = pd.read_csv(os.path.join(input_folder, 
                                                 'dauphine_rider_points.csv'))
dauphine_rider_points.rename(columns={'stage_scores': 'dauphine_scores'}, 
                             inplace=True)
tour_rider_points = tour_rider_points.merge(dauphine_rider_points, how='left')
#%%
suisse_rider_points = pd.read_csv(os.path.join(input_folder, 
                                                 'suisse_rider_points.csv'))
suisse_rider_points.rename(columns={'stage_scores': 'suisse_scores'}, 
                             inplace=True)
tour_rider_points = tour_rider_points.merge(suisse_rider_points, how='left')
#%%
california_rider_points = pd.read_csv(os.path.join(input_folder, 
                                                 'california_rider_points.csv'))
california_rider_points.rename(columns={'stage_scores': 'california_scores'}, 
                             inplace=True)
tour_rider_points = tour_rider_points.merge(california_rider_points, how='left')
#%%
giro_rider_points = pd.read_csv(os.path.join(input_folder, 
                                            'giro_rider_points.csv'))
tour_rider_points = tour_rider_points.merge(giro_rider_points, how='left')
#%%
score_columns = tour_rider_points.filter(like='_scores').columns
score_shift_columns = [c+'_shift' for c in score_columns]
tour_rider_points[score_shift_columns] = tour_rider_points[score_columns].shift()
tour_rider_points.loc[mask, score_shift_columns] = np.nan
#%%
tour_rider_points['nr_tour_starts'] = tour_rider_points.groupby('Rider').cumcount()
#%%
id_vars = ['Rider', 'year', 'score']
pred_columns = ['score_shift', 'score_shift_2', 'Age', 'is_teamlead', 
                'team_bib', 'dauphine_scores', 'suisse_scores', 'nr_tour_starts',
                'california_scores']

selection = id_vars + pred_columns
df_model = tour_rider_points[selection].copy()
corr = df_model.corr()
sns.heatmap(corr, xticklabels=corr.columns, yticklabels=corr.columns, 
            annot=True, vmin=-1, vmax=1, cmap='coolwarm')
#%%

assert df_model[id_vars].notnull().all().all()
print(df_model.info())

df_model.fillna(0, inplace=True)
X = df_model[pred_columns]
y = df_model['score']
X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, random_state=42)

mmscale  = preprocessing.MinMaxScaler((0, 1))
X_train = mmscale.fit_transform(X_train)
X_test = mmscale.transform(X_test)

ri = linear_model.Ridge(random_state=42)
#%%
param_grid = {'alpha': 10**np.arange(-5., 5., 0.5)}
gscv = model_selection.GridSearchCV(ri, param_grid=param_grid, cv=5)
gscv.fit(X_train, y_train)

plt.figure(figsize=(3,3))
plt.bar(pred_columns, gscv.best_estimator_.coef_)
plt.xticks(rotation=80)
plt.show()
print(gscv.score(X_test, y_test))
print(gscv.best_params_)

tour_rider_points['prediction'] = model_selection.cross_val_predict(ri, X, y)

tour_rider_points['Has_gc_end_points'] = tour_rider_points.groupby('Rider')\
['gc_extra_scores'].transform(max)
tour_rider_points['Has_gc_end_points'] = (tour_rider_points['Has_gc_end_points'] > 5).astype(int)

tour_rider_points['Has_green_end_points'] = tour_rider_points.groupby('Rider')\
['green_extra_scores'].transform(max)
tour_rider_points['Has_green_end_points'] = (tour_rider_points['Has_green_end_points'] > 1).astype(int)

tour_rider_points['rider_type'] = 'no_specialty'
tour_rider_points.loc[tour_rider_points['Has_green_end_points']==1, 'rider_type'] = 'green'
tour_rider_points.loc[tour_rider_points['Has_gc_end_points']==1, 'rider_type'] = 'yellow'


sns.lmplot('prediction', 'score', hue='rider_type', data=tour_rider_points)
plt.plot([0, tour_rider_points['prediction'].max()], 
          [0, tour_rider_points['prediction'].max()], 
          linestyle='--', color='k', linewidth=2)

#%%
joblib.dump(mmscale, os.path.join(output_folder, 'minmaxscaler.pkl')) 
joblib.dump(gscv.best_estimator_, os.path.join(output_folder, 'model.pkl')) 

#tour_rider_points[['Rider', 'year', 'prediction']].to_csv(
#        os.path.join(output_folder, 'prediction.csv'), index=False)
