# -*- coding: utf-8 -*-
"""
Created on Fri Jul 06 19:32:43 2018

@author: sjoer_000
"""

from bs4 import BeautifulSoup
import urllib2
import pandas as pd
import os
#%%
output_folder = 'C:\Users\sjoer_000\Documents\Willekeurige berekeningen\Tour De France\Output'
#%%
def count_nr_stages(year, race):
    url = 'https://www.procyclingstats.com/race/%s/%s/stages/winners' % (race, str(year))
    page_request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urllib2.urlopen(page_request)
    soup = BeautifulSoup(page, 'html5lib')
    tables = soup.find_all('table')
    df_stage_descriptions = pd.read_html(str(tables), flavor='bs4')[0]
    nr_stages = len(df_stage_descriptions)
    has_prologue = df_stage_descriptions['Stage'].str.contains('Prologue').any()
    return nr_stages, has_prologue
    
#%%
race = 'tour-of-qatar'
for y in range(2018, 2003, -1): 
    nr_stages, has_prologue = count_nr_stages(y, race)
    df_stage_results = pd.DataFrame([])
    df_gc = pd.DataFrame([])
    df_points = pd.DataFrame([])
    df_polka = pd.DataFrame([])
    df_youth = pd.DataFrame([])
    df_team = pd.DataFrame([])
    
    base_url = 'https://www.procyclingstats.com/race/%s/%s/' % (race, str(y))
    for i in range(1, nr_stages+1):
        print(y, i)
        if has_prologue:
            i -= 1
        
        if i==0:
            stage_part = 'prologue'
        else: 
            stage_part = 'stage-%s' % str(i)
        
        url = base_url + stage_part
        page_request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        page = urllib2.urlopen(page_request)
    
        soup = BeautifulSoup(page, 'html5lib')
        tables = soup.find_all('table')
        try:
            df_list = pd.read_html(str(tables), flavor='bs4')
        except ValueError:
            print('No tables found! Skipping this iteration')
            continue
        
        if len(df_list) not in [1, 2, 5, 6]:
            print('Skipping - wrong number of tables available!')
            continue
        
        
        df_this_stage = df_list[0]
        df_this_stage['year'] = y
        df_this_stage['stage'] = i
        df_stage_results = df_stage_results.append(df_this_stage)
        
        # A number of races only report stage results (especially historical)
        if len(df_list) == 1:
            continue
                
        df_this_gc = df_list[1]
        df_this_gc['year'] = y
        df_this_gc['stage'] = i
        df_gc = df_gc.append(df_this_gc)

        # A number of races only report stage results and yellow jersey, 
        # not the other classifcations (especially historical data)
        if len(df_list) == 2:
            continue

        df_this_points = df_list[2]
        df_this_points['year'] = y
        df_this_points['stage'] = i
        df_points = df_points.append(df_this_points)

        df_this_youth = df_list[3]
        df_this_youth['year'] = y
        df_this_youth['stage'] = i
        df_youth = df_youth.append(df_this_youth)
        
        # There is a king-of-mountains classification
        if len(df_list) == 6:
            df_this_polka = df_list[4]
            df_this_polka['year'] = y
            df_this_polka['stage'] = i
            df_polka = df_polka.append(df_this_polka)
            
            df_this_team = df_list[5]
            df_this_team['year'] = y
            df_this_team['stage'] = i
            df_team = df_team.append(df_this_team)
        
        # No King of the mountains classification
        elif len(df_list) == 5:
            df_this_team = df_list[4]
            df_this_team['year'] = y
            df_this_team['stage'] = i
            df_team = df_team.append(df_this_team)
    
    df_stage_results.to_csv(os.path.join(output_folder, 'stage_results_%s_%s.csv' % (race, str(y))),
                            index=False, encoding='utf-8')
    df_gc.to_csv(os.path.join(output_folder, 'gc_%s_%s.csv' % (race, str(y))),
                            index=False, encoding='utf-8')
    df_points.to_csv(os.path.join(output_folder, 'points_%s_%s.csv' % (race, str(y))),
                            index=False, encoding='utf-8')
    df_polka.to_csv(os.path.join(output_folder, 'polka_%s_%s.csv' % (race, str(y))),
                            index=False, encoding='utf-8')
    df_youth.to_csv(os.path.join(output_folder, 'youth_%s_%s.csv' % (race, str(y))),
                            index=False, encoding='utf-8')
    df_team.to_csv(os.path.join(output_folder, 'team_%s_%s.csv' % (race, str(y))),
                            index=False, encoding='utf-8')