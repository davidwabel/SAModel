import pandas as pd
import cx_Oracle


QUERY = """
  SELECT d.ryear, e.fuel, Sum(d.VALUE*u.FACTOR) EJ, c.name
  FROM 
    edb_unit_conversion u, 
    (
      (edb_flow f INNER JOIN {table} d ON f.CODE=d.FLOW_CODE)
      INNER JOIN edb_fuel e ON e.PROD_CODE = d.PROD_CODE
    )
  INNER JOIN edb_country c ON d.COUNTRY_CODE=c.CODE
  WHERE (
    (d.ryear>=1971 And d.ryear<=2015)
    And d.rev_code={revision} 
    And d.UNIT=u.UNIT_IN
    And u.UNIT_OUT='EJ'
  )
  And c.name = '{region}'
  And e.scheme='{fuel_scheme}'
  And e.fuel in ({fuel_list})
  And f.name in ({name_list})
  GROUP BY d.ryear, e.fuel ,c.name  ORDER by d.ryear, e.fuel
"""

pe_map = pd.DataFrame({             
    'Fuel': [
        'Coal|Total',
        'Oil|Total',
        'Gas|Total',
        'Biomass|Total',
        'Hydro|Total',
        'Wind|Total',
        'Ocean|Total',
        'Other|Total',
        'Nuclear|Total',
        'Geothermal|Total',
        'Solar|Total',
        'Total',
        'Fossil|Total',
    ],
    'Variable': [
        'Primary Energy|Coal',
        'Primary Energy|Oil',
        'Primary Energy|Gas',
        'Primary Energy|Biomass',
        'Primary Energy|Hydro',
        'Primary Energy|Wind',
        'Primary Energy|Ocean',
        'Primary Energy|Other',
        'Primary Energy|Nuclear',
        'Primary Energy|Geothermal',
        'Primary Energy|Solar',
        'Primary Energy',
        'Primary Energy|Fossil',
    ],
}).set_index('Fuel')['Variable']

pe_elec_map = pd.DataFrame({             
    'Fuel': [
        'Coal|Total',
        'Oil|Total',
        'Gas|Total',
        'Biomass|Total',
    ],
    'Variable': [
        'Primary Energy|Coal|Electricity',
        'Primary Energy|Oil|Electricity',
        'Primary Energy|Gas|Electricity',
        'Primary Energy|Biomass|Electricity',
    ],
}).set_index('Fuel')['Variable']

ele_map = pd.DataFrame({
    'Fuel': [
        'Coal|Total',
        'Oil|Total',
        'Gas|Total',
        'Biomass|Total',
        'Hydro|Total',
        'Wind|Total',
        'Ocean|Total',
        'Other|Total',
        'Nuclear|Total',
        'Geothermal|Total',
        'Solar|Total',
        'Total',
        'Fossil|Total',
    ],
    'Variable': [
        'Secondary Energy|Electricity|Coal',
        'Secondary Energy|Electricity|Oil',
        'Secondary Energy|Electricity|Gas',
        'Secondary Energy|Electricity|Biomass',
        'Secondary Energy|Electricity|Hydro',
        'Secondary Energy|Electricity|Wind',
        'Secondary Energy|Electricity|Ocean',
        'Secondary Energy|Electricity|Other',
        'Secondary Energy|Electricity|Nuclear',
        'Secondary Energy|Electricity|Geothermal',
        'Secondary Energy|Electricity|Solar',
        'Secondary Energy|Electricity',
        'Secondary Energy|Electricity|Fossil',
    ],
}).set_index('Fuel')['Variable']

fe_map = pd.DataFrame({
    'Fuel': [
        'Coal|Total',
        'Oil|Total',
        'Gas|Total',
        'Biomass|Total',
        'Geothermal|Total',
        'Solar|Total',
        'Heat|Total',
        'Total',
        'Fossil|Total',
        'Electricity|Total',
        'Other|Total',
    ],
    'Variable': [
        'Final Energy|Solids|Coal',
        'Final Energy|Liquids',
        'Final Energy|Gases',
        'Final Energy|Solids|Biomass',
        'Final Energy|Geothermal',
        'Final Energy|Solar',
        'Final Energy|Heat',
        'Final Energy',
        'Final Energy|Fossil',
        'Final Energy|Electricity',
        'Final Energy|Other',
    ],
}).set_index('Fuel')['Variable']

feind_map = pd.DataFrame({        
    'Fuel': [
        'Coal|Total',
        'Oil|Total',
        'Gas|Total',
        'Biomass|Total',
        'Geothermal|Total',
        'Solar|Total',
        'Heat|Total',
        'Total',
        'Fossil|Total',
        'Electricity|Total',
        'Other|Total',
    ],
    'Variable': [
        'Final Energy|Industry|Solids|Coal',
        'Final Energy|Industry|Liquids',
        'Final Energy|Industry|Gases',
        'Final Energy|Industry|Solids|Biomass',
        'Final Energy|Industry|Geothermal',
        'Final Energy|Industry|Solar',
        'Final Energy|Industry|Heat',
        'Final Energy|Industry',
        'Final Energy|Industry|Fossil',
        'Final Energy|Industry|Electricity',
        'Final Energy|Industry|Other',
    ],
}).set_index('Fuel')['Variable']

fetrp_map = pd.DataFrame({   
    'Fuel': [
        'Coal|Total',
        'Oil|Total',
        'Gas|Total',
        'Biomass|Total',
        'Geothermal|Total',
        'Solar|Total',
        'Heat|Total',
        'Total',
        'Fossil|Total',
        'Electricity|Total',
    ],
    'Variable': [
        'Final Energy|Transportation|Solids|Coal',
        'Final Energy|Transportation|Liquids',
        'Final Energy|Transportation|Gases',
        'Final Energy|Transportation|Solids|Biomass',
        'Final Energy|Transportation|Geothermal',
        'Final Energy|Transportation|Solar',
        'Final Energy|Transportation|Heat',
        'Final Energy|Transportation',
        'Final Energy|Transportation|Fossil',
        'Final Energy|Transportation|Electricity',
    ],
}).set_index('Fuel')['Variable']

ferc_map = pd.DataFrame({  
    'Fuel': [
        'Coal|Total',
        'Oil|Total',
        'Gas|Total',
        'Biomass|Total',
        'Geothermal|Total',
        'Solar|Total',
        'Heat|Total',
        'Total',
        'Fossil|Total',
        'Electricity|Total',
        'Other|Total',
    ],
    'Variable': [
        'Final Energy|Residential and Commercial|Solids|Coal',
        'Final Energy|Residential and Commercial|Liquids',
        'Final Energy|Residential and Commercial|Gases',
        'Final Energy|Residential and Commercial|Solids|Biomass',
        'Final Energy|Residential and Commercial|Geothermal',
        'Final Energy|Residential and Commercial|Solar',
        'Final Energy|Residential and Commercial|Heat',
        'Final Energy|Residential and Commercial',
        'Final Energy|Residential and Commercial|Fossil',
        'Final Energy|Residential and Commercial|Electricity',
        'Final Energy|Residential and Commercial|Other',
    ],
}).set_index('Fuel')['Variable']

fene_map = pd.DataFrame({  
    'Fuel': [
        'Coal|Total',
        'Oil|Total',
        'Gas|Total',
        'Biomass|Total',
        'Total',
        'Fossil|Total',
    ],
    'Variable': [
        'Final Energy|Non-Energy Use|Coal',
        'Final Energy|Non-Energy Use|Oil',
        'Final Energy|Non-Energy Use|Gas',
        'Final Energy|Non-Energy Use|Biomass',
        'Final Energy|Non-Energy Use',
        'Final Energy|Non-Energy Use|Fossil',
    ],
}).set_index('Fuel')['Variable']

def get_output(mapping, names):
    query = QUERY.format(
        table=table,
        revision=revision,
        region=region,
        fuel_scheme=fuel_scheme,
        fuel_list=' ,'.join("'{}'".format(x) for x in mapping.index),
        name_list=' ,'.join("'{}'".format(x) for x in names),
    )
    cursor.execute(query)
    output = list(cursor)
    return output


def output_to_df(mapping, output):
    df = (
        pd.DataFrame(output, columns=['Year', 'Fuel', 'Value', 'Region'])
        .pivot_table(
            columns=['Year'],
            index=['Region', 'Fuel']
        )
        .Value
        .rename_axis(None, axis=1)
        .reset_index()
        .join(mapping, on='Fuel')
        .drop('Fuel', axis=1)
    )
    df['Unit'] = 'EJ/yr'
    df['Model'] = 'History'
    df['Scenario'] = 'IEA Energy Statistics ({})'.format(revision)
    df = df.set_index(['Model', 'Scenario', 'Region', 'Variable', 'Unit'])
    return df

def append_Convert(df,out_Variable,PE_name,FE_name,PEELEC_name):
    a1 = df.loc[('History','IEA Energy Statistics (2017)','South Africa',PE_name,'EJ/yr')]
    a2 = df.loc[('History','IEA Energy Statistics (2017)','South Africa',FE_name,'EJ/yr')]
    a3 = df.loc[('History','IEA Energy Statistics (2017)','South Africa',PEELEC_name,'EJ/yr')]
    
    df_test = (a1-a2-a3)
    df_test['Unit'] = 'EJ/yr'
    df_test['Model'] = 'History'
    df_test['Scenario'] = 'IEA Energy Statistics ({})'.format(revision)
    df_test['Region'] = 'South Africa'
    df_test['Variable'] = out_Variable
    df.reset_index(inplace=True)
    df2 = df.append(df_test,ignore_index=True)
    print(df2.tail())
    df2 = df2.set_index(['Model', 'Scenario', 'Region', 'Variable', 'Unit'])
    return df2

def addPopAndGDP(IEA_name):
    #read in files
    gdp_pop_in = pd.read_csv('C:\\Users\\dwabel\\Documents\\IIASA\\zaf_ssp_data.csv')
    reporting_in = pd.read_excel('C:\\Users\\dwabel\\Documents\\IIASA\\'+IEA_name+'.xlsx')
    
    #Add gdp and population
    df = gdp_pop_in
    df = df[['scenario', 'year', 'pop', 'gdp']]
    #convert 2010 USD to 2005 Euro
    df['gdp'] = df['gdp']*0.84431747
    df = df[(df.scenario == 'SSP2') & (df.year <=2015)]
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
    reporting_in.to_excel('C:\\Users\\dwabel\\Documents\\IIASA\\'+IEA_name+'_appended.xlsx')


def flip_negative_PE_ELEC(df,coal_name,gas_name,oil_name,biomass_name):
    
    df.loc[('History','IEA Energy Statistics (2017)','South Africa',coal_name,'EJ/yr')] = (
            df.loc[('History','IEA Energy Statistics (2017)','South Africa',coal_name,'EJ/yr')]*-1)
    df.loc[('History','IEA Energy Statistics (2017)','South Africa',gas_name,'EJ/yr')] = (
            df.loc[('History','IEA Energy Statistics (2017)','South Africa',gas_name,'EJ/yr')]*-1)
    df.loc[('History','IEA Energy Statistics (2017)','South Africa',oil_name,'EJ/yr')] = (
            df.loc[('History','IEA Energy Statistics (2017)','South Africa',oil_name,'EJ/yr')]*-1)
    df.loc[('History','IEA Energy Statistics (2017)','South Africa',biomass_name,'EJ/yr')] = (
            df.loc[('History','IEA Energy Statistics (2017)','South Africa',biomass_name,'EJ/yr')]*-1)
    return df

revision = 2017
table = 'edb_data_2017'
fuel_scheme = 'OTHER'
region = 'South Africa'


data = {
    ('elect.output in gwh',): ele_map,
    ('total final consumption',): fe_map,
    ('total primary energy supply',):pe_map,
    ('industry sector',):feind_map,
    ('transport sector',):fetrp_map,
    ('other sectors',):ferc_map,
    ('non-energy use',):fene_map,
    ('main activity producer electricity plants',):pe_elec_map,
}

dfs = []

# Query the SQL comand
connection = cx_Oracle.connect("iea/iea@//gp3.iiasa.ac.at:1521/GP3")
cursor = connection.cursor()
for name, mapping in data.items():
    output = get_output(mapping, name)
    df = output_to_df(mapping, output)
    dfs.append(df)
cursor.close()
connection.close()

df = pd.concat(dfs)

df = flip_negative_PE_ELEC(df,
                           'Primary Energy|Coal|Electricity',
                           'Primary Energy|Gas|Electricity',
                           'Primary Energy|Oil|Electricity',
                           'Primary Energy|Biomass|Electricity'
                           )

df = append_Convert(df,
                    'Primary Energy|Coal|Convert',
                    'Primary Energy|Coal',
                    'Final Energy|Solids|Coal',
                    'Primary Energy|Coal|Electricity'
                    )
df = append_Convert(df,
                    'Primary Energy|Gas|Convert',
                    'Primary Energy|Gas',
                    'Final Energy|Gases',
                    'Primary Energy|Gas|Electricity'
                    )
df = append_Convert(df,
                    'Primary Energy|Oil|Convert',
                    'Primary Energy|Oil',
                    'Final Energy|Liquids',
                    'Primary Energy|Oil|Electricity'
                    )

df.to_excel('IEA_mappedHistYears_v2.xlsx', index=True)

df = addPopAndGDP('IEA_mappedHistYears_v2')
