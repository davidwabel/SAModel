# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 16:15:23 2018

@author: dwabel
"""

##### Calculate Scenario Costs

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

def calcInvCost(model,scen_out,tec):
    base = mp.Scenario(model, scen_in, scheme='MESSAGE')
    load = mp.Scenario(model, scen_out, scheme='MESSAGE')
    df_base = base.par('inv_cost')
    df_base = df_base[df_base['technology']==tec]
    df = load.par('inv_cost')
    df = df[df['technology']==tec]
    df2 = load.var('CAP_NEW')
    df2 = df2[df2['technology']==tec]
    subsidy = (df_base[df_base['year_vtg']==2020]['value']-
               df[df['year_vtg']==2020]['value'])
    newCapacity = df2['lvl'].sum()
    df2['cost_FV'] = df2['lvl']*subsidy.iloc[0]
    discount = 0.04
    baseyear = 2010
    df2['cost_PV'] = (df2['cost_FV'])/((1+discount)**(df2['year_vtg']-baseyear))
    total_cost = df2['cost_PV'].sum()*10**6
    cost_dict = {'Cost (2010 USD)':[total_cost],
               'Subsidy (2010 USD/kWa)':[subsidy.iloc[0]],
               'Avg. control var cost (2010 USD/kWa)':[0],
               'New Capacity (Assume GWa)':[newCapacity],
               'Controlled Activity (Assume GWa)':[0]}
    cost_df = pd.DataFrame(cost_dict)
    return cost_df


def calcControlCost(model,scen_out,tec):
    base = mp.Scenario(model, scen_in, scheme='MESSAGE')
    load = mp.Scenario(model, scen_out, scheme='MESSAGE')
    df = load.par('var_cost')
    df = df[df['technology']==tec]
    df_base = base.par('var_cost')
    df_base = df_base[df_base['technology']==tec]
    print(df_base)
    df2 = load.var('ACT')
    df2 = df2[df2['technology']==tec]
    print(df2)
    df3_i = pd.merge(df,df2,on=['year_act','year_vtg'],how='left')
    df3 = pd.merge(df3_i,df_base,on=['year_act','year_vtg'],how='left')
    df3['value'] = df3['value_x']-df3['value_y']
    print(df3)
    discount = 0.04
    baseyear = 2010
    df3['controlCost_PV'] = (df3['lvl']*df3['value'])/((1+discount)**(df3['year_act']-baseyear))
    print(df3)
    avg_control_cost = df3.loc[df3['year_act']>=2020,'value'].mean()
    print(avg_control_cost)
    total_cost = df3[df3['year_act']>=2020]['controlCost_PV'].sum()*10**6 #kW-year to GWa
    controlledActivity = df3[df3['year_act']>=2020]['lvl'].sum()
    cost_dict = {'Cost (2010 USD)':[total_cost],
               'Subsidy (2010 USD/kWa)':[0],
               'Avg. control var cost (2010 USD/kWa)':[avg_control_cost],
               'New Capacity (Assume GWa)':[0],
               'Controlled Activity (Assume GWa)':[controlledActivity]}
    print(cost_dict)
    cost_df = pd.DataFrame(cost_dict)
    return cost_df

####MAIN
    
mp = ix.Platform(dbprops='enedb.properties')
ssp = ['SSP1','SSP2','SSP3']
model_header = 'MESSAGE South Africa '
scen_in = 'baseline_IEP' 

col_names =  ['Model', 'Scenario', 'Cost (2010 USD)', 'Subsidy (2010 USD/kWa)',
              'Avg. control var cost (2010 USD/kWa)', 'New Capacity (Assume GWa)',
              'Controlled Activity (Assume GWa)']
costs_summary  = pd.DataFrame(columns = col_names)

for ssp in ssp:
    model = (model_header + ssp)
    base = mp.Scenario(model, scen_in, scheme='MESSAGE')
    inputs = pd.read_excel('MESSAGE_scenarioInputs.xlsx')
    scen_out = inputs['Scenario']
    inputs.set_index('Scenario',inplace=True)
    for scen_out in scen_out:
        cost_df1 = calcInvCost(model,scen_out,'solar_pv_ppl')
        cost_df2 = calcInvCost(model,scen_out,'wind_ppl')
        cost_df3 = calcInvCost(model,scen_out,'nuc_ppl')
        cost_df4 = calcControlCost(model,scen_out,'coal_adv')
        cost_df5 = calcControlCost(model,scen_out,'coal_ppl')
        cost_df6 = calcControlCost(model,scen_out,'foil_ppl')
        cost_df7 = calcControlCost(model,scen_out,'loil_ppl')
        cost_df = (cost_df1+cost_df2+cost_df3+cost_df4+cost_df5+cost_df6+cost_df7)
        cost_df['Model'] = model
        cost_df['Scenario'] = scen_out
        costs_summary = pd.concat([costs_summary,cost_df])
        print(costs_summary)
costs_summary.to_excel('costs_summary.xlsx')
    
    
    