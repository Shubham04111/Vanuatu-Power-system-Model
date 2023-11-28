# -*- coding: utf-8 -*-
"""

"""

# describe the statistics

def plot_stat(n):
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    #curtailment
    
    curtailment = n.statistics.curtailment()
    curtailment_1 = curtailment[curtailment != 0]
    curtailment_1.plot(kind='bar')
    plt.ylabel('MWh')
    plt.title('Curtailment')
    plt.show()
    
    
    ######################
    
    # Capacity Factor
    capacity_factor_data = n.statistics.capacity_factor()*100
    capacity_factor_data=capacity_factor_data['Generator']    
    fig, ax = plt.subplots()
    capacity_factor_data.plot(kind='bar', ax=ax)
    ax.set_xlabel("")
    ax.set_ylabel("%")
    ax.set_title("Capacity Factor")
    plt.show()
    
    ######################
    #Existing and New capacity
    
    expanded_capacity = n.statistics.expanded_capacity()
    installed_capacity = n.statistics.installed_capacity()

    # Combine the results into a DataFrame
    capacity_df = pd.DataFrame({
        'Existing Capacity': installed_capacity,
        'New Built Capacity': expanded_capacity - installed_capacity
    })

    capacity_df = capacity_df[~capacity_df.index.get_level_values(1).str.contains('slack')]
    capacity_df.loc[('Link', 'AC')]['New Built Capacity']=0


    # Plot the bar chart
    ax = capacity_df.plot(kind='bar', stacked=True)
    ax.set_xlabel('')
    ax.set_ylabel('Capacity (MW/MVA)')
    ax.set_title('Existing vs. New Built Capacity')

    plt.show()
    
    
    
    ######################
    
    
    # Sub Category Energy Balance
    
    fig, ax = plt.subplots()
    
    n.statistics.energy_balance(aggregate_time=False).loc[:, :, "AC"].droplevel(0).iloc[:, :4].groupby("carrier").sum().where(lambda x: np.abs(x) > 1).fillna(0).T.plot.area(ax=ax, title="Energy Balance Timeseries by Sub-category")
    
    ax.legend(bbox_to_anchor=(1, 0), loc="lower left", title=None, ncol=1)
    
    
    ax.set_ylabel("Generation (MWh)")
    
    plt.show()

if __name__ == "__main__":
    pass



