# -*- coding: utf-8 -*-
"""
Created on Sat Jul 07 22:03:29 2018

@author: sjoer_000
"""

from bs4 import BeautifulSoup
import urllib2
import pandas as pd
import os
#%%
output_folder = 'C:\Users\sjoer_000\Documents\Willekeurige berekeningen\Tour De France\Output'
#%%
race = 'tour-de-france'
tour_description = pd.DataFrame([])
tour_stage_descriptions = pd.DataFrame([])
for y in range(2017, 1997, -1):
    print(y)
    url = 'https://www.procyclingstats.com/race/%s/%s/stages/winners' % (race, str(y))
    page_request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urllib2.urlopen(page_request)
    soup = BeautifulSoup(page, 'html5lib')
    table = soup.find('table')
    df_stage_descriptions = pd.read_html(str(table), flavor='bs4')[0]
    df_stage_descriptions['year'] = y
    df_stage_descriptions['stage'] = 0
    rows = soup.find("table").find("tbody").find_all("tr")

    profile_str = 'profile t'
    for i, row in enumerate(rows):
        cell = str(row.find("td"))
        ind = cell.index(profile_str)
        # type 1: fully flat stage, type 2: one hill in the middle
        # type 3: some hills, 4: mountains, 5: mountains, finishes on mountain
        stage_type = cell[ind+len(profile_str):ind+len(profile_str)+1]
        df_stage_descriptions.iloc[i, 0] = int(stage_type)
        df_stage_descriptions.iloc[i, 5] = i

    df_stage_descriptions['IndivTimeTrial'] = (df_stage_descriptions['Stage'].str.contains('(ITT)') |\
        df_stage_descriptions['Stage'].str.contains('ndividual') | \
        df_stage_descriptions['Stage'].str.contains('rologue')).astype(int)
    df_stage_descriptions['TeamTimeTrial'] = (df_stage_descriptions['Stage'].str.contains('(TTT)') |\
        df_stage_descriptions['Stage'].str.contains('Team Time Trial')).astype(int)
    
    df_stage_descriptions['MountainStage'] = (df_stage_descriptions['Unnamed: 0'] > 3).astype(int)
    df_stage_descriptions['SprintStage'] = (df_stage_descriptions[['IndivTimeTrial' , 'TeamTimeTrial',
                         'MountainStage']].max(axis=1) == 0).astype(int)
    
    tour_description_temp = df_stage_descriptions.groupby('year').agg(
            {'MountainStage': 'sum', 'SprintStage':'sum', 
             'IndivTimeTrial': 'sum', 'TeamTimeTrial': 'sum'})
    
    tour_description_temp['FirstNonSprintStage'] =  min(df_stage_descriptions\
                         [df_stage_descriptions['SprintStage'] == 0].index)
    tour_description = tour_description.append(tour_description_temp)
    tour_stage_descriptions = tour_stage_descriptions.append(df_stage_descriptions)
tour_stage_descriptions.rename(columns={'Unnamed: 0': 'stage_type'}, inplace=True)
tour_stage_descriptions.to_csv(os.path.join(output_folder, 'stages_%s.csv' % 
                                          race), encoding='utf-8', index=False)
tour_description.to_csv(os.path.join(output_folder, 'tour_description.csv' ))
