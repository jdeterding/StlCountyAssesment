import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

pd.set_option('display.max_columns', None)


if __name__ == '__main__':
    # Load / Parse Data
    converters = {'Distance (miles)': lambda x: float(x),
                  'Total Living Area': lambda x : float(x.replace(',','')),
                  'Sale Price':lambda x : float(x.replace(',','').replace('$','')) * 1E-3}
    data = pd.read_csv('2023_RealestateSearch.txt', delimiter='\t', converters=converters) 
    # Split data that are input as ratios
    data['Bed Rooms'] = data['Bed / Total Rooms'].apply(lambda x: int(x.split('/')[0].strip()))
    data['Total Rooms'] = data['Bed / Total Rooms'].apply(lambda x: int(x.split('/')[1].strip()))
    del data['Bed / Total Rooms']
    data['Full Bath'] = data['Full / Half Baths'].apply(lambda x: int(x.split('/')[0].strip()))
    data['Half Bath'] = data['Full / Half Baths'].apply(lambda x: int(x.split('/')[1].strip()))
    del data['Full / Half Baths']
    data['Living Units'] = data['Living Units / Story Height'].apply(lambda x: int(x.split('/')[0].strip()))
    data['Story Height'] = data['Living Units / Story Height'].apply(lambda x: float(x.split('/')[1].strip()))
    del data['Living Units / Story Height']
    
    # Filter Comparable homes
    c1 = (data['Total Living Area'] <= 1350 + 500) & (data['Total Living Area'] >= 1350 - 500)
    c2 = data['Living Units'] == 1
    c3 = data['Story Height'] == 1.0
    c4 = data['Architectural Style'] != 'pass' #Ranch'
    c5 = data['Exterior Wall Type'] != 'pass' #Aluminum / Vinyl'
    c6 = data['Basement'] == 'Full'
    c7 = data['Bed Rooms'] == 3 
    c8 = (data['Total Rooms'] <= 6 + 1) & (data['Total Rooms'] >= 6 - 1)
    c9 = data['Full Bath'] == 2
    c10 = (data['Half Bath'] <= 0 + 1) & (data['Half Bath'] >= 0)
    c11 = data['Sale Validity'] == 'X'
    c12 = (data['Total Acres'] <= 0.2571 + 0.2) & (data['Total Acres'] >= 0.2571 - 0.1)
    
    comps = data[c1 & c2 & c3 & c4 & c5 & c6 & c7 & c8 & c9 & c10 & c11 & c12]
    comps = comps.sort_values(by=['Distance (miles)'])

    # Compute Statistical outliers
    quartiles = comps["Sale Price"].quantile([0.25, 0.75])
    iqr = quartiles[0.75] - quartiles[0.25]
    q_upper_bound = quartiles[0.75] + 1.5 * iqr
    q_lower_bound = quartiles[0.25] - 1.5 * iqr
    comps_q = comps[(comps['Sale Price'] < q_upper_bound) & (comps['Sale Price'] > q_lower_bound)]
    

    # Output Statistics
    print(f'Total Number of Comps. found: {comps.shape[0]}')
    print(f'Outliers identified         : {comps.shape[0] - comps_q.shape[0]}')
    
    bins = np.linspace(comps["Sale Price"].min(), comps["Sale Price"].max(), num=12)
    ax = comps["Sale Price"].plot.hist(bins=bins, alpha=0.25, label='Comparables')
    ax.set_xlabel('Sale Price (In thousands of $)')
    ax.set_ylabel('Count')
    ax.vlines(q_upper_bound, ymin=0, ymax=25, linestyles='--', color='k', label='IQR-Upper Bound')
    ax.vlines(261.0, ymin=0, ymax=25, linestyles='-', color='k', label='421 Talbert Ct.')
    ax.vlines(406.0, ymin=0, ymax=25, linestyles='-', color='r', label='432 Talbert Ct.')
    plt.legend()
    plt.savefig('Distribution.png')
    plt.clf()

    comps.to_csv('ComparableProperties.csv', sep=',')
