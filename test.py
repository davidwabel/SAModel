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
    print(df)
    for parameter in parameters:
        df.loc[:, parameter] = parameters[parameter]
        print(df.loc[:, parameter])
    return df


def addpar(ds, parname, _par):
    ds.check_out()
    ds.add_par(parname, _par)
    ds.commit(' ')

mp = ix.Platform(dbprops='enedb.properties')
ssp = ['SSP1','SSP2','SSP3']
model_header = 'MESSAGE South Africa '
scen_in = 'baseline'

for x in ssp:
    model = (model_header + x)
    print(model)
    base = mp.Scenario(model, scen_in, scheme='MESSAGE')
    scen_out = ['wind_10%_ic','wind_20%_ic','wind_30%_ic','wind_50%_ic']
    scale = [.9,.8,.7,.5]
    for scen_out, scale in zip(scen_out, scale):
        copy = base.clone(model,scen_out,keep_sol = False)
        print(copy)
        df = copy.par('inv_cost')
        df = df[df['technology']=='wind_ppl']
        print(df)
        new_costs = df['value']*scale
        print(new_costs)
        parameters = {'mode': 'M1', 
                      'node_loc': 'South Africa',
                      'technology': 'wind_ppl',
                      'time': 'year',
                      'unit': '???',
                      'value': list(new_costs),
                      'year_act': list(range(2010, 2060, 10)),
                      'year_vtg': list(range(2010, 2060, 10))}
        print(parameters)
        par = create_par(copy, parameters, 'var_cost', index=range(0, 5))
        print(par)
        addpar(copy, 'var_cost', par)
        copy.solve('MESSAGE')


        