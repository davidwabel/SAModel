# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 14:26:34 2018

@author: dwabel
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jul 30 14:49:06 2018

@author: dwabel
"""

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
    
def addInvCost(df,tec_name,added):
    df = df[df['technology']==tec_name]
    vtg = df[df['technology']==tec_name]['year_vtg']
    new_costs = df['value']+added
    print(vtg)
    print(new_costs)
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
    df_test = copy.par('inv_cost')
    print(df)
    print(df_test[df_test['technology']==tec_name])
    
def scaleInvCost(df,tec_name,scale):
    df = df[df['technology']==tec_name]
    vtg = df[df['technology']==tec_name]['year_vtg']
    new_costs = df['value']*scale
    print(vtg)
    print(new_costs)
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
    df_test = copy.par('inv_cost')
    print(df)
    print(df_test[df_test['technology']==tec_name])

def changeControlsCost(df,cc):
    for column in cc:
        df2 = df[df['technology']==column]
        vtg = df2[df2['technology']==column]['year_vtg']
        act = df2[df2['technology']==column]['year_act']
        new_costs = df2[['year_act','value']]
        #new_costs.set_index('year_act',inplace=True)
        new_costs.loc[new_costs['year_act'] == 2020,['value']] = new_costs.loc[new_costs['year_act'] == 2020,['value']]+cc.loc[0,column]
        new_costs.loc[new_costs['year_act'] == 2030,['value']] = new_costs.loc[new_costs['year_act'] == 2030,['value']]+cc.loc[1,column]
        new_costs.loc[new_costs['year_act'] == 2040,['value']] = new_costs.loc[new_costs['year_act'] == 2040,['value']]+cc.loc[2,column]
        new_costs.loc[new_costs['year_act'] == 2050,['value']] = new_costs.loc[new_costs['year_act'] == 2050,['value']]+cc.loc[3,column]
        new_costs = new_costs['value']
        parameters = {'mode': 'M1', 
                      'node_loc': 'South Africa',
                      'technology': column,
                      'time': 'year',
                      'unit': '???',
                      'value': list(new_costs),
                      'year_act': list(act),
                      'year_vtg': list(vtg)}
        par = create_par(copy, parameters, 'var_cost', index=range(0, len(vtg)))
        addpar(copy, 'var_cost', par)
        df_test = copy.par('var_cost')
        print(df_test[df_test['technology']==column])
    
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
    df = df[(df.scenario == ssp) & (df.year <=2050) & (df.year >= 2020)]
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
    inputs = pd.read_excel('MESSAGE_scenarioInputs.xlsx')
    scen_out = inputs['Scenario']
    inputs.set_index('Scenario',inplace=True)
    for scen_out in scen_out:
        print('Beginning Model: {}, Scenario: {}'.format(model,scen_out))
        copy = base.clone(model,scen_out,keep_sol = False)
        
        if scen_out == 'CLE':
            df = copy.par('var_cost')
            controlsCosts = {'coal_adv': [4.881249,47.397506,1.279819,5.527307],
                 'coal_ppl': [36.074201,53.682990,41.564349,30.349379],
                 'foil_ppl': [16.955344,35.797198,30.626362,0], 
                 'loil_ppl': [5.469168,17.898599,15.313181,0]}
            cc = pd.DataFrame(controlsCosts)
            changeControlsCost(df,cc)
        elif scen_out == '100FGD':
            df = copy.par('var_cost')
            controlsCosts = {'coal_adv': [11.296531,11.296531,11.296531,11.296531],
                 'coal_ppl': [11.813888,11.813888,11.813888,11.813888]}
            cc = pd.DataFrame(controlsCosts)
            changeControlsCost(df,cc)
        elif scen_out == '100HED':
            df = copy.par('var_cost')
            controlsCosts = {'coal_adv': [12.138454,12.138454,12.138454,12.138454],
                 'coal_ppl': [11.632120,11.632120,11.632120,11.632120]}
            cc = pd.DataFrame(controlsCosts)
            changeControlsCost(df,cc)
        else:
            df = copy.par('inv_cost')
            tec = inputs.loc[scen_out,'Tech1']
            tec2 = inputs.loc[scen_out,'Tech2']
            added = inputs.loc[scen_out,'Tech1_InvCost_added']
            if added==0:
                scale = inputs.loc[scen_out,'Tech1_InvCost_scale']
                scaleInvCost(df,tec,scale)
            else:
                addInvCost(df,tec,added)
            if tec2 != 0:
                added2 = inputs.loc[scen_out,'Tech2_InvCost_added']
                if added2==0:
                    scale2 = inputs.loc[scen_out,'Tech2_InvCost_scale']
                    scaleInvCost(df,tec2,scale2)
                else:
                    addInvCost(df,tec2,added2)
                
        #Costs come from controlsCostMapping.xlsx pulled from GAINS and mapped to MESSAGE techs
        
        copy.solve('MESSAGE')
        subprocess.call(['python', 
                                 'C:\\Users\\dwabel\\Documents\\Message_Oliver\\message_data\\runscript\\run_reporting_SA.py',
                                 '--model', model, '--scenario', scen_out])
        addMissingVariables(model,scen_out,ssp)
        print('Finished Model: {}, Scenario: {}'.format(model,scen_out))
            