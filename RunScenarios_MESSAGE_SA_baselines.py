# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 09:59:27 2018

@author: dwabel
"""

import ixmp as ix
import message_ix

import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey
#%matplotlib inline
plt.style.use('ggplot')

import tools
import subprocess
import argparse

def create_par(ds, parameters, parname, index=[0]):
    df = pd.DataFrame(columns=ds.par(parname).columns, index=index)
    for parameter in parameters:
        df.loc[:, parameter] = parameters[parameter]
    return df


def addpar(ds, parname, _par):
    ds.check_out()
    ds.add_par(parname, _par)
    ds.commit(' ')
    
def changeInvCost(df,tec_name,scale):
    df = df[df['technology']==tec_name]
    vtg = df[df['technology']==tec_name]['year_vtg']
    new_costs = df['value']*scale
    parameters = {'mode': 'M1', 
                  'node_loc': 'South Africa',
                  'technology': tec_name,
                  'time': 'year',
                  'unit': '???',
                  'value': list(new_costs),
                  'year_act': list(vtg),
                  'year_vtg': list(vtg)}
    par = create_par(copy, parameters, 'inv_cost', index=range(0, len(vtg)))
    addpar(copy, 'inv_cost', par)

    
def addMissingVariables(model,scen_out,ssp):
    #read in files
    gdp_pop_in = pd.read_csv('C:\\Users\\dwabel\\Documents\\IIASA\\zaf_ssp_data.csv')
    reporting_in = pd.read_excel('C:\\Users\\dwabel\\Documents\\Message_Oliver\\message_data\\post-processing\\output\\'+model+'_'+scen_out+'.xlsx')
           
    #interpolation, could be more robust.
    #reporting_in[2010] = reporting_in[2020] #Must be changed later
    #reporting_in[2015] = reporting_in[2020] #Must be changed later
    reporting_in[2025] = (reporting_in[2030]-reporting_in[2020])/2 + reporting_in[2020]
    reporting_in[2035] = (reporting_in[2040]-reporting_in[2030])/2 + reporting_in[2030]
    reporting_in[2045] = (reporting_in[2050]-reporting_in[2040])/2 + reporting_in[2040]
    reporting_in = reporting_in[['Model', 'Scenario', 'Region', 'Variable', 'Unit', 2020, 
                                 2025, 2030, 2035, 2040, 2045, 2050]]
    
    #Add gdp and population
    df = gdp_pop_in
    df = df[['scenario', 'year', 'pop', 'gdp']]
    #convert 2010 USD to 2005 Euro
    df['gdp'] = df['gdp']*0.84431747
    df = df[(df.scenario == ssp) & (df.year <=2050) & (df.year >=2020)]
    df = (
        pd.pivot_table(df, values=['pop', 'gdp'], columns=['scenario'], index=['year'])
        .T
        .reset_index()
        .rename(columns={'level_0':'Variable'})
    )
    del df['scenario']
    df['Model'] = 'MESSAGE South Africa'
    df['Scenario'] = 'baseline'
    df['Region'] = 'South Africa'
    df['Variable'] = ['GDP|MER', 'Population']
    df['Unit'] = ['2005Euro','ppl']
    
    reporting_in = pd.concat([reporting_in,df],ignore_index=True)
    
    #Write out the dataframe to new excel file
    reporting_in.to_excel('C:\\Users\\dwabel\\Documents\\Message_Oliver\\message_data\\post-processing\\output\\'+model+'_'+scen_out+'_appended.xlsx')

####
#### MAIN
####

mp = ix.Platform(dbprops='enedb.properties')
ssp = ['SSP1','SSP2','SSP3']
model_header = 'MESSAGE South Africa '
scen_in = 'baseline_IEP' 
    
for ssp in ssp:
    model = (model_header + ssp)
    base = mp.Scenario(model, scen_in, scheme='MESSAGE')
                
    base.solve('MESSAGE')
    subprocess.call(['python', 
                             'C:\\Users\\dwabel\\Documents\\Message_Oliver\\message_data\\runscript\\run_reporting_SA.py',
                             '--model', model, '--scenario', scen_in])
    addMissingVariables(model,scen_in,ssp)
    print('Finished Model: {}, Scenario: {}'.format(model,scen_in))
        