# -*- coding: utf-8 -*-
"""
Created on Sat Jul 07 16:20:12 2018

@author: sjoer_000
"""

import pandas as pd
import os
import numpy as np
from sklearn.externals import joblib
import unicodedata

from fuzzywuzzy import process
# TODO: bedenken hoe ik aan Age en BIB kom vóór Tourstart
#%%
input_folder = 'C:\Users\sjoer_000\Documents\Willekeurige berekeningen\Tour De France\Data'
output_folder = 'C:\Users\sjoer_000\Documents\Willekeurige berekeningen\Tour De France\Output'
#%%
jaar = 2017
file_inschrijf = 'Inschrijfformulier Tour Poule %s.xlsx'% str(jaar)
df_riders = pd.read_excel(os.path.join(input_folder, file_inschrijf), 
                          encoding='utf-8')
df_riders = df_riders[['Renner', 'Waarde']].copy()
df_riders['year'] = jaar

tour_rider_points = pd.read_csv(os.path.join(input_folder, 'rider_points_incl_2018.csv'), 
                                encoding='utf-8')
dauphine_rider_points = pd.read_csv(os.path.join(input_folder, 
                                                 'dauphine_rider_points.csv'))
dauphine_rider_points.rename(columns={'stage_scores': 'dauphine_scores'}, 
                             inplace=True)

suisse_rider_points = pd.read_csv(os.path.join(input_folder, 
                                                 'suisse_rider_points.csv'))
suisse_rider_points.rename(columns={'stage_scores': 'suisse_scores'}, 
                             inplace=True)

naam_tabel = pd.read_excel(os.path.join(input_folder, 'naam_tabel.xlsx'), usecols='A,B')
naam_dict = naam_tabel.set_index('Naam_inschrijf').to_dict()['Naam_procycling']
#%%
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

df_riders['Renner'] = correct_rider_names(df_riders['Renner'])
df_riders.rename(columns={'Renner': 'Rider'}, inplace=True)
tour_rider_points['Rider'] = correct_rider_names(tour_rider_points['Rider'])
suisse_rider_points['Rider'] = correct_rider_names(suisse_rider_points['Rider'])
dauphine_rider_points['Rider'] = correct_rider_names(dauphine_rider_points['Rider'])

df_riders['Rider2'] = df_riders['Rider'].map(naam_dict)
df_riders['Rider2'].fillna(df_riders['Rider'], inplace=True)
df_riders['Rider'] = df_riders['Rider2']
df_riders.drop(columns='Rider2', inplace=True)

if jaar == 2019 :
    tour_rider_points = tour_rider_points.append(df_riders)
else: 
    tour_rider_points = tour_rider_points.merge(df_riders, how='outer')
    if not tour_rider_points.loc[tour_rider_points['Waarde'].notnull(), 'score'].notnull().all():
        failed_names_inschrijf = tour_rider_points.loc[tour_rider_points['Waarde'].notnull() 
        & tour_rider_points['score'].isnull(), 'Rider']
        failed_names_procycling = tour_rider_points.loc[tour_rider_points['Waarde'].isnull() 
        & tour_rider_points['score'].notnull(), 'Rider'].unique()
        
    assert tour_rider_points.loc[tour_rider_points['Waarde'].notnull(), 'score'].notnull().all(),\
    tour_rider_points[tour_rider_points['Waarde'].notnull() & tour_rider_points['score'].isnull()]
tour_rider_points = tour_rider_points.merge(suisse_rider_points, how='left')
tour_rider_points = tour_rider_points.merge(dauphine_rider_points, how='left')

#%%
#naam_tabel_list = []
#for n in failed_names_inschrijf:
#    print(n)
#    found_name, ratio = process.extractOne(n, failed_names_procycling)
#    naam_tabel_list.append([n, found_name, ratio])
#columns = ['Naam_inschrijf', 'Naam_procycling', 'overeenkomst']
#naam_tabel = pd.DataFrame(naam_tabel_list, columns=columns)
#naam_tabel.to_excel(os.path.join(output_folder, 'naam_tabel.xlsx'), index=False)

#%%
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
score_columns = tour_rider_points.filter(like='_scores').columns
score_shift_columns = [c+'_shift' for c in score_columns]
tour_rider_points[score_shift_columns] = tour_rider_points[score_columns].shift()
tour_rider_points.loc[mask, score_shift_columns] = np.nan
#%%
id_vars = ['BIB',  'Rider', 'year', 'Waarde']
pred_columns = ['score_shift', 'score_shift_2', 'Age', 'is_teamlead', 
                'team_bib', 'dauphine_scores', 'suisse_scores']
selection = id_vars + pred_columns

df_pred = tour_rider_points.loc[tour_rider_points['year'] == jaar, selection]

print(df_pred.loc[df_pred[id_vars].isnull().any(axis=1), id_vars])
df_pred['Waarde'].fillna(100, inplace=True)

assert df_pred[id_vars].notnull().all().all()

print(df_pred.info())
df_pred.fillna(0, inplace=True)
#%%
ri = joblib.load(os.path.join(input_folder, 'model.pkl')) 
mmscale = joblib.load(os.path.join(input_folder, 'minmaxscaler.pkl')) 
X_pred = mmscale.transform(df_pred[pred_columns].fillna(0))
df_pred['prediction'] = ri.predict(X_pred)
df_pred.to_csv(os.path.join(output_folder, 'prediction_%s.csv' % str(jaar)))
df_pred.to_excel(os.path.join(output_folder, 'prediction_%s.xlsx' % str(jaar)), index=False)
