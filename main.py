### ISYE 6767: Final Project
### main.py
##
#

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# To ignore warnings
import warnings
warnings.filterwarnings("ignore")

# Import Classes & Methods
from Data_Processing import DataProcessing
from Principal_Component_Analysis import PrincipalComponentAnalysis
from Trading_Signals import TradingSignals
from Performance_Measures import PerformanceMeasures
from Project_Implementation import ProjectImplementation

### Implementation of the Final Project
DP = DataProcessing()
PCA = PrincipalComponentAnalysis()
TS = TradingSignals()
PM = PerformanceMeasures()
PI = ProjectImplementation()

### Specifying the working directory
path = r'C:/Users/lott7/OneDrive - Georgia Institute of Technology/MATH 6767 Design and Implementation of Systems to Support Computational Finance/Homeworks/Final Project'

### Importing Data & Preprocessing
df_largest40 = DP.clean_df(DP.import_data('./', 'coin_universe_150K_40.csv'), 'startTime', 'time')
df_prices =  DP.clean_df(DP.import_data('./', 'coin_all_prices_full_final_version.csv'), 'startTime', 'time') 


### Part 1
# Implementation Step 1: Origin of the Data 
print("Welcome to the presentation of the results of the Final Project in the course ISYE 6767!\n")
print("The program has already started to compile our strategy: ")

date = pd.Timestamp('2021-09-26 00:00:00+00:00')
portfolio_ret_df, eigen, eig_table_1, eig_table_2, total, stats_closed, stats_current = PI.implementation(240, date, df_largest40, df_prices)

print("The simulations of our statistical arbitrage strategy have been compiled.")


### Part 2
# Implementation: Calculating & Printing Different Statistics

print('Performance Measures:')
start = pd.Timestamp('2021-09-26 00:00:00+00:00')
end = pd.Timestamp('2022-09-25 23:00:00+00:00')
print('Annualized sharpe ratio: ', np.sqrt(8760) * PM.sharpe(start, end, portfolio_ret_df))
print('Maximum Drawdown over whole period: ', PM.mdd(start, end, portfolio_ret_df))
print("")

### Part 3
# Implementation: Plotting the Evolution of our Strategy
df_btc_eth = PI.df_btc_eth(df_prices)

pp = PdfPages('Statistical_Arbitrage_Strategy_Plots.pdf')

# 1st Plot
fig = plt.figure()
sns.set_theme(style="darkgrid")
plt.subplot(411)
plt.plot(eigen['Date'], eigen['Cum Ret 1'])
plt.title('Cumulative Return 1st eigen-portfolio')
plt.subplot(412)
plt.plot(eigen['Date'], eigen['Cum Ret 2'])
plt.title('Cumulative Return 2nd eigen-portfolio')
plt.subplot(413)
plt.plot(df_btc_eth['startTime'], df_btc_eth['Cum Ret BTC'])
plt.title('Cumulative Return BTC')
plt.subplot(414)
plt.plot(df_btc_eth['startTime'], df_btc_eth['Cum Ret ETH'])
plt.title('Cumulative Return ETH')
plt.rcParams["figure.figsize"] = (20, 12)
plt.subplots_adjust(hspace=0.5)
fig.savefig(pp, format='pdf')
# plt.show()

# 2nd & 3rd Plot
d = ['2021-09-26 12:00:00+00:00', '2022-04-15 20:00:00+00:00']
for i in d:
    date = pd.Timestamp(i)
    line = eig_table_1[eig_table_1['Date']==date].iloc[0, 1:].dropna()
    line = line.sort_values(ascending=False)
    fig = plt.figure()
    sns.set_theme(style="darkgrid")
    plt.plot(line, 'b*-')
    plt.rcParams["figure.figsize"] = (20, 8)
    plt.title('1st eigen-portfolio weights @ '+ str(date))
    plt.xticks(rotation=90)
    fig.savefig(pp, format='pdf')
    # plt.show()

    line = eig_table_2[eig_table_2['Date']==date].iloc[0, 1:].dropna()
    line = line.sort_values(ascending=False)
    fig = plt.figure()
    sns.set_theme(style="darkgrid")
    plt.plot(line, 'b*-')
    plt.rcParams["figure.figsize"] = (20, 8)
    plt.title('2nd eigen-portfolio weights @ '+ str(date))
    plt.axhline(y=0, color='r', linestyle='-')
    plt.xticks(rotation=90)
    fig.savefig(pp, format='pdf')
    # plt.show()

# 4th Plot
start = pd.Timestamp('2021-09-26 00:00:00+00:00')
end = pd.Timestamp('2021-10-25 23:00:00+00:00')

btc = total[(total['Ticker']=='BTC') & (total['Date'] <= end) & (total['Date'] >= start)]
eth = total[(total['Ticker']=='ETH') & (total['Date'] <= end) & (total['Date'] >= start)]

fig = plt.figure(figsize=(11.7,8.27))
sns.set_theme(style="darkgrid")
plt.plot(btc['Date'],btc['S-score'])
plt.title('Evolution of BTC s-score over time')
fig.savefig(pp, format='pdf')
# plt.show()

fig = plt.figure(figsize=(11.7,8.27))
sns.set_theme(style="darkgrid")
plt.plot(eth['Date'],eth['S-score'])
plt.title('Evolution of ETH s-score over time')
fig.savefig(pp, format='pdf')
# plt.show()

# 5th Plot
fig = plt.figure(figsize=(11.7,8.27))
sns.set_theme(style="darkgrid")
plt.plot(portfolio_ret_df['Date'], portfolio_ret_df['Return'])
fig.savefig(pp, format='pdf')
# plt.show()

# 6th Plot
fig = plt.figure(figsize=(11.7,8.27))
sns.set_theme(style="darkgrid")
plt.hist(portfolio_ret_df['Hourly Return'], bins=100, range=(-0.05, 0.05))
plt.title('Histogram of Hourly Returns')
fig.savefig(pp, format='pdf')
# plt.show()

pp.close()


### Part 4
# Implementation: Saving the Data as CSV-Files

total.to_csv(path + '/Total.csv', index=None, header=True)
portfolio_ret_df.to_csv(path + '/Portfolio_ret.csv', index=None, header=True)
eigen.to_csv(path + '/Eigen.csv', index=None, header=True)
df_btc_eth.to_csv(path + '/BTC_ETH.csv', index=None, header=True)
eig_table_1.to_csv(path + '/Eigenvector_table1.csv', index=None, header=True)
eig_table_2.to_csv(path + '/Eigenvector_table2.csv', index=None, header=True)
stats_closed.to_csv(path + '/Stats_closes.csv', index=None, header=True)
stats_current.to_csv(path + '/Stats_current.csv', index=None, header=True)

print("Program has terminated!")