# -*- coding: utf-8 -*-
"""
Created on Sun Nov 19 18:37:55 2023

@author: neshw
"""

from datetime import datetime
import pandas as pd
import pypsa
from Scripts_Viz import plot_stat
import matplotlib.pyplot as plt
import numpy as np

xls = pd.ExcelFile('PyPSA_Data_Input.xlsx')
sheet_names = xls.sheet_names
['bus',
 'Existing_generators',
 'Capital_cost',
 'Load_curve',
 'Fuel_cost',
 'Transmission_line']
bus = pd.read_excel('PyPSA_Data_Input.xlsx', sheet_name='bus')
n = pypsa.Network()

for bus in bus.Bus:
    print(bus)
    n.add("Bus", bus)

# Load_curve = pd.read_excel('PyPSA_Data_Input.xlsx', sheet_name='Load_curve',index_col=0)
number_hourly_timestamps=8760
splits=1
target_year_1 = 2030
start_date_1 = pd.to_datetime(f'{target_year_1 - 1}-01-01 00:00')
end_date_1 = pd.to_datetime(f'{target_year_1}-12-31 23:00')
# Generate timestamps and load curves for target_year_1
timestamps_1 = pd.date_range(start=start_date_1, end=end_date_1, freq="H")[:8760]
growth_factor_1 = (1 + 0.04) ** (target_year_1 - 2023)


#adopt the snapshots from profiles generated in profiles_lg.py
n.snapshots = timestamps_1
n.snapshot_weightings['objective']=n.snapshot_weightings['objective']*(8760/(number_hourly_timestamps/splits))

load = pd.read_excel('PyPSA_Data_Input.xlsx', sheet_name='Load_C',index_col=0)

yearly_load_curve = pd.DataFrame()

# Repeat the daily load curve for each day of the year (365 days)
for _ in range(365):
    yearly_load_curve = pd.concat([yearly_load_curve, load[['Tagape', 'Port Vila']]], ignore_index=True)

# Load_curve = pd.read_excel('PyPSA_Data_Input.xlsx', sheet_name='Load_curve',index_col=0)

for load_centre in yearly_load_curve.columns:
    print(load_centre)
    
    load_list = list(yearly_load_curve[load_centre])
    
    load_fix = pd.Series(
        load_list, index=n.snapshots, name=load_centre
    )
    n.add("Load", load_centre, bus=load_centre, p_set=load_fix)

Existing_generators = pd.read_excel('PyPSA_Data_Input.xlsx', sheet_name='Existing_generators',index_col=0)

Existing_diesel_generators=Existing_generators[Existing_generators.Fuel=='Diesel']

Fuel_cost = pd.read_excel('PyPSA_Data_Input.xlsx', sheet_name='Fuel_cost',index_col=0)
generation_profile = pd.read_excel('PyPSA_Data_Input.xlsx', sheet_name='generation_profile',index_col=0)

# for gen_i in Existing_diesel_generators.index:
#     print(gen_i)

#     n.add("Generator",
#             Existing_diesel_generators.at[gen_i,'name'],
#             bus=Existing_diesel_generators.at[gen_i,'Bus'],
#             p_nom=Existing_diesel_generators.at[gen_i,'Capacity(MW)'],
#             lifetime=100,p_max_pu=1,
#             carrier='Diesel',min_up_time=1,min_down_time=1,up_time_before=0,down_time_before=24,
#             marginal_cost=Existing_diesel_generators.at[gen_i,'Variable cost (Vt/MWh)'],committable=False,p_min_pu=0.3,
#             capital_cost=0,p_nom_extendable=False,ramp_limit_down=1,ramp_limit_up=1)

Existing_wind_generators=Existing_generators[Existing_generators.Fuel=='Wind']

for gen_i in Existing_wind_generators.index:
    print(gen_i)

    n.add("Generator",
            Existing_wind_generators.at[gen_i,'name'],
            bus=Existing_wind_generators.at[gen_i,'Bus'],
            p_nom=Existing_wind_generators.at[gen_i,'Capacity(MW)'],
            lifetime=100,p_max_pu=list(generation_profile['Wind']),
            carrier='Wind',
            marginal_cost=0,
            capital_cost=0,p_nom_extendable=False,ramp_limit_down=1,ramp_limit_up=1)

Existing_solar_generators=Existing_generators[Existing_generators.Fuel=='Solar']

for gen_i in Existing_solar_generators.index:
    print(gen_i)

    n.add("Generator",
            Existing_solar_generators.at[gen_i,'name'],
            bus=Existing_solar_generators.at[gen_i,'Bus'],
            p_nom=Existing_solar_generators.at[gen_i,'Capacity(MW)'],
            lifetime=100,p_max_pu=list(generation_profile['Solar']),
            carrier='Solar',
            marginal_cost=0)    


#add slack
n.add("Generator",
            'slack',
            bus='Melemart',
            p_nom=1000,p_max_pu=1,marginal_cost=1000000000000000000000000000000,
            carrier='slack')


Tranmission_lines = pd.read_excel('PyPSA_Data_Input.xlsx', sheet_name='Transmission_line',index_col=0)

#add transmission

for t_i in Tranmission_lines.index:
    print(t_i)
    n.add(
        "Link",str(t_i),
        bus0=Tranmission_lines.at[t_i,'From'],
        bus1=Tranmission_lines.at[t_i,'To'],
        p_nom=Tranmission_lines.at[t_i,'Transfer_capacity(MW)']+10,
        efficiency=0.9,
        p_nom_extendable=False,p_max_pu=1,p_min_pu=-1,
    )

#Add new generators
def calculate_annuity(capital_cost, interest_rate, lifetime):
    annuity = (capital_cost * interest_rate) / (1 - (1 + interest_rate) ** -lifetime)
    return annuity
Fuel_cost = pd.read_excel('PyPSA_Data_Input.xlsx', sheet_name='Fuel_cost',index_col=0)
Capital_cost= pd.read_excel('PyPSA_Data_Input.xlsx', sheet_name='Capital_cost',index_col=0)
# Diesel
# Wind
# Solar
# Bio Power- CNO
pipeline_generators = pd.read_excel('PyPSA_Data_Input.xlsx', sheet_name='pipeline_generators',index_col=0)

#New Solar 
for gen_i in pipeline_generators[pipeline_generators.Fuel=='Solar'].index:
    print(gen_i)
    n.add("Generator",
            pipeline_generators.at[gen_i,'name'],
            bus=pipeline_generators.at[gen_i,'Bus'],
            p_nom_max=pipeline_generators.at[gen_i,'Capacity(MW)'],
            lifetime=100,p_max_pu=list(generation_profile['Solar']),
            carrier='Solar',p_nom_extendable=True,
            marginal_cost=0,capital_cost=calculate_annuity(pipeline_generators.at[gen_i,'Capital_cost (Vt/MW)'],0.10,15)) 

for gen_i in pipeline_generators[pipeline_generators.Fuel=='Wind'].index:
    print(gen_i)
    n.add("Generator",
            pipeline_generators.at[gen_i,'name'],
            bus=pipeline_generators.at[gen_i,'Bus'],
            p_nom_max=pipeline_generators.at[gen_i,'Capacity(MW)'],
            lifetime=100,p_max_pu=list(generation_profile['Wind']),
            carrier='Wind',
            marginal_cost=0,
            p_nom_extendable=True,capital_cost=calculate_annuity(pipeline_generators.at[gen_i,'Capital_cost (Vt/MW)'],0.10,15))


for gen_i in pipeline_generators[pipeline_generators.Fuel=='Bio Power- CNO'].index:
    print(gen_i)
    n.add("Generator",
            pipeline_generators.at[gen_i,'name'],
            bus=pipeline_generators.at[gen_i,'Bus'],
            p_nom_max=pipeline_generators.at[gen_i,'Capacity(MW)'],
            lifetime=100,p_max_pu=1,
            carrier='Bio Power- CNO',
            marginal_cost=pipeline_generators.at[gen_i,'Variable cost (Vt/MWh)'],committable=False,p_min_pu=0.3,
            p_nom_extendable=True,capital_cost=calculate_annuity(pipeline_generators.at[gen_i,'Capital_cost (Vt/MW)'],0.10,10))


n.add("Store", "battery storage", bus='Tagape', e_cyclic=True, e_nom_max=100.0,e_nom_extendable=True,capital_cost=0.2*calculate_annuity(750000000,0.10,10))
solver_options = {'BarHomogeneous': 1,'MIPGap':0.05,'MIPFocus':3,'LogFile':'vnuatu.log'}
snps=int(number_hourly_timestamps/splits)
for i in range(splits):
    overlap=0
    n.optimize(snapshots=n.snapshots[i * snps : (i + 1) * snps + overlap],solver_name='gurobi',**solver_options) 
    
    
## Import visualizations
plot_stat(n)


n.export_to_csv_folder(r'D:\Github\Vanuatu_country_model\Network')