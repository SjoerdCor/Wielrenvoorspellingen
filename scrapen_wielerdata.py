# -*- coding: utf-8 -*-
"""
Created on Fri Jul 06 19:32:43 2018

@author: sjoer_000
"""

import os
from urllib import request

from bs4 import BeautifulSoup
import pandas as pd
pd.set_option('display.max_columns', 500)
#%%
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'Output')
#%%
def count_nr_stages(year, race):
    '''outputs number of stages and whether there was a prologue for a race

    Scrapes this information from procyclingstats
    year: the year in which the race was held
    race: the string that designates a race in the website procyclingstats,
    e.g. 'tour-de-france'
    '''
    url = f'https://www.procyclingstats.com/race/{race}/{year}/stages/winners'
    page_request = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = request.urlopen(page_request)
    soup = BeautifulSoup(page, 'html5lib')
    
    # First table contains needed information
    table = soup.find('table')
    
    #read_html outputs list of dfs
    df_stage_descriptions = pd.read_html(str(table), flavor='bs4')[0]
    nr_stages = len(df_stage_descriptions)    
    # Race contains a string with starting and endpoint and stage nr
    has_prologue = df_stage_descriptions['Race'].str.contains('Prologue').any()
    return nr_stages, has_prologue

def append_stage(df_stage, df_full, year, stage):
    '''Append stage results to the dataframe for the entire year

    df_stage: the dataframe of the HTML-table containing the results for the
    classification for a single stage
    df_full: the dataframe containing earlier results
    year: the season in which the race was held
    stage: number of the stage

    Will add stage and year to the table so that it can be later show in a long
    table for that race that contained of multiple stages
    '''
    df_stage['year'] = year
    df_stage['stage'] = stage
    return df_full.append(df_stage)

def scrape_stage(url):
    '''
    From a url retrieve all classifications for a stage

    returns (possibly empty) dataframes for stage results, general classification,
    points, king of the mountain, youth classification and team results.
    They are empty if procyclingstats did not record the classification or
    it doesn't exist (e.g. king of mountain in flat stage)
    '''
    page_request = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = request.urlopen(page_request)

    soup = BeautifulSoup(page, 'html5lib')
    tables = soup.find_all('table')
    stage_results_dict = {'stage': pd.DataFrame(), 'gc': pd.DataFrame(),
                          'points': pd.DataFrame(), 'kom': pd.DataFrame(),
                          'youth': pd.DataFrame(), 'team': pd.DataFrame()}

    try:
        df_list = pd.read_html(str(tables), flavor='bs4')
    except ValueError:
        print('No tables found! Skipping this iteration')
        return stage_results_dict

    # 1 table -> only stage results
    # 2 tables -> only stage and general classification
    # 5 tables -> stage, gc, points and youth
    # 6 tabkes -> includes also king of mountains

    if len(df_list) not in [1, 2, 5, 6]:
        print(f'Skipping - wrong number of tables available! \nurl: {url}')
        return stage_results_dict

    stage_results_dict['stage'] = df_list[0]

    try:
        stage_results_dict['gc'] = df_list[1]
    except KeyError:
        return stage_results_dict

    try:
        stage_results_dict['points'] = df_list[2]
        stage_results_dict['youth'] = df_list[3]
    except KeyError:
        return stage_results_dict

    # There is a king-of-mountains classification
    if len(df_list) == 6:
        stage_results_dict['kom'] = df_list[4]
        stage_results_dict['team'] = df_list[5]

    # No King of the mountains classification
    else:
        stage_results_dict['team'] = df_list[4]
    return stage_results_dict

def scrape_year(race, year, has_prologue, nr_stages):
    ''' Download results for one year for classifications and write to csv

    Uses https://www.procyclingstats.com/ to pick the results for a race and
    writes the following results: stage results, general classification,
    points, king of the mountain, youth classification,
    these tables can be (partly) empty if either procyclingstats did not
    record these stages, or because the classifications don't exist (
    e.g. king of mountain in a flat stage)

    race: the string that designates a race in the website procyclingstats,
    e.g. 'tour-de-france'
    year: the year in which the race was
    has_prologue: whether the race has a prologue (important because the URL
    is different)
    nr_stages: number of stages in the race
    '''

    race_results_dict = {'stage': pd.DataFrame(), 'gc': pd.DataFrame(),
                         'points': pd.DataFrame(), 'kom': pd.DataFrame(),
                         'youth': pd.DataFrame(), 'team': pd.DataFrame()}

    base_url = f'https://www.procyclingstats.com/race/{race}/{year}/'
    if has_prologue:
        first_stage = 0
        last_stage = nr_stages
    else:
        first_stage = 1
        last_stage = nr_stages + 1
    
    for stage_nr in range(first_stage, last_stage):
        print(race, year, stage_nr)

        if stage_nr == 0:
            stage_part = 'prologue'
        else:
            stage_part = f'stage-{stage_nr}'

        url = base_url + stage_part
        stage_results_dict = scrape_stage(url)

        assert stage_results_dict.keys() == race_results_dict.keys()

        race_results_dict = {k: append_stage(stage_results_dict[k], race_results_dict[k],
                                             year, stage_nr) for k in race_results_dict.keys()}

    return race_results_dict

def scrape_race(racename, years):
    '''Writes a csv for every classification for every year for a race

    racename: he string that designates a race in the website procyclingstats,
    e.g. 'tour-de-france'
    year: a list of years for which to extract the results
    '''
    for year in years:
        nr_stages, has_prologue = count_nr_stages(year, racename)
        race_results_dict = scrape_year(racename, year, has_prologue, nr_stages)
        for key, value in race_results_dict.items():
            value.to_csv(os.path.join(OUTPUT_FOLDER, f'{racename}_{year}_{key}.csv'),
                         index=False, encoding='utf-8')
#%%
RACE = 'tour-de-france'
YEARS = range(2018, 1997, -1)

scrape_race(RACE, YEARS)
