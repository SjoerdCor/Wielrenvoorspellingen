# -*- coding: utf-8 -*-
"""
Created on Wed Jul 04 22:05:54 2018

@author: sjoer_000
"""

from bs4 import BeautifulSoup
import urllib2
import pandas as pd
import os
#%%
output_folder = 'C:\Users\sjoer_000\Documents\Willekeurige berekeningen\Tour De France\Output'
#%%
def count_nr_stages(year):
    url = 'https://www.procyclingstats.com/race/tour-de-france/%s/stages/winners' % str(year)
    page_request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urllib2.urlopen(page_request)
    soup = BeautifulSoup(page, 'html5lib')
    tables = soup.find_all('table')
    df_stage_descriptions = pd.read_html(str(tables), flavor='bs4')[0]
    nr_stages = len(df_stage_descriptions)
    has_prologue = df_stage_descriptions['Stage'].str.contains('Prologue').any()
    return nr_stages, has_prologue
    
#%%
for y in range(1997, 1996, -1): 
    nr_stages, has_prologue = count_nr_stages(y)
    df_stage_results = pd.DataFrame([])
    df_points = pd.DataFrame([])
    df_polka = pd.DataFrame([])
    df_youth = pd.DataFrame([])
    df_list = [df_stage_results, df_points, df_youth, df_polka]
    for i in range(1, nr_stages+1):
    for i in range(1, 3):
        print(y, i)
        if has_prologue:
            i -= 1
        if i==0:
            stage_part = 'prologue'
        else: 
            stage_part = 'stage-%s' % str(i)
            
            
        base_url = 'https://www.procyclingstats.com/race/tour-de-france/%s/' % str(y)
        url = base_url + stage_part
        if (not has_prologue and i==nr_stages) or (has_prologue and i==nr_stages-1):
            url_points = base_url + 'points'
            url_youth = base_url + 'youth'
            url_polka = base_url + 'kom'
        elif i==0:
            url_points = base_url + stage_part_prologue + '-points'
            url_youth = base_url + stage_part_prologue + '-youth'
            url_polka = base_url + stage_part_prologue + '-kom'
        else: 
            url_points =  url_stage + '-points'
            url_youth = url_stage + '-youth'
            url_polka = url_stage + '-kom'
            
        url_list = [url_stage, url_points, url_youth, url_polka]
        
        for j, url in enumerate(url_list):
            print(url)
            page_request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            page = urllib2.urlopen(page_request)
        
            soup = BeautifulSoup(page, 'html5lib')
            try:
                tables = soup.find('table')
                df_temp = pd.read_html(str(tables), flavor='bs4')[0]
                df_temp['stage_nr'] = i
                df_list[j] = df_list[j].append(df_temp)
            except ValueError:
                print(url)
                print('No tables found!')
                pass
    
    df_stage_results, df_points, df_youth, df_polka = df_list
    
    df_stage_results.to_csv(os.path.join(output_folder, 'stage_results_%s.csv' % str(y)),
                            index=False, encoding='utf-8')
    df_points.to_csv(os.path.join(output_folder, 'points_%s.csv' % str(y)),
                            index=False, encoding='utf-8')
    df_polka.to_csv(os.path.join(output_folder, 'polka_%s.csv' % str(y)),
                            index=False, encoding='utf-8')
    df_youth.to_csv(os.path.join(output_folder, 'youth_%s.csv' % str(y)),
                            index=False, encoding='utf-8')