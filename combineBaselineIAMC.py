# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 11:03:17 2018

@author: dwabel
"""

import pandas as pd

hist = pd.read_csv('C:\\Users\\dwabel\\Documents\\IIASA\\IEA_mappedHistYears.csv')
SSP1 = pd.read_excel('C:\\Users\\dwabel\\Documents\\Message_Oliver\\message_data\\post-processing\\output\\MESSAGE South Africa SSP1_baseline_appended.xlsx')
SSP2 = pd.read_excel('C:\\Users\\dwabel\\Documents\\Message_Oliver\\message_data\\post-processing\\output\\MESSAGE South Africa SSP2_baseline_appended.xlsx')
SSP3 = pd.read_excel('C:\\Users\\dwabel\\Documents\\Message_Oliver\\message_data\\post-processing\\output\\MESSAGE South Africa SSP3_baseline_appended.xlsx')

com_base = pd.concat([hist,SSP1,SSP2,SSP3],ignore_index=True)
com_base.to_excel('C:\\Users\\dwabel\\Documents\\IIASA\\mapped_baselineData.xlsx')
