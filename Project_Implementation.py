### ISYE 6767: Final Project
### Project_Implementation.py
##
#

import pandas as pd
import numpy as np

# Import Classes & Methods
from Data_Processing import DataProcessing
from Principal_Component_Analysis import PrincipalComponentAnalysis
from Trading_Signals import TradingSignals
from Performance_Measures import PerformanceMeasures

### Implementation of the Final Project
DP = DataProcessing()
PCA = PrincipalComponentAnalysis()
TS = TradingSignals()
PM = PerformanceMeasures()

class ProjectImplementation:
    def __init__(self):
        pass


    def update_eig_table(self, df_tot: pd.DataFrame, tick: list, eigen_vector: np.array, date: pd.Timestamp):
        """Updating DataFrame containing the i-th Eigenportfolio at each Hour"""
        eig_temp_1 = pd.DataFrame()

        eig_temp_1['Ticker'] = tick
        eig_temp_1['Value'] = eigen_vector
        eig_temp_1 = eig_temp_1.transpose()

        eig_temp_1.columns = eig_temp_1.loc['Ticker']
        eig_temp_1.drop(labels='Ticker', inplace=True)
        eig_temp_1.reset_index(inplace=True, drop=True)
        eig_temp_1['Date'] = date

        # change the order, such that first column is date:
        # first we need to have a list of ordered columns
        col = [['Date']]
        col.append(tick)
        # we now flatten the list 
        col2 = list(np.concatenate(col).flat)
        # we can now change the order of the columns
        eig_temp_1 = eig_temp_1[col2]
        df_tot = pd.concat([df_tot, eig_temp_1], axis=0)

        return df_tot


    def implementation(self, m: int, date: pd.Timestamp, df_token_universe: pd.DataFrame, df_token_prices: pd.DataFrame):
        """Function to Implement the whole Program"""
        #count = 1
        s, tick_tot, last_tickers, portfolio_ret, portfolio_ret_current, dates = [], [], [], [], [], []
        portfolio_value, hour_returns, eigen_ret_1, eigen_ret_2 = [], [], [], []
        positions, closed_positions = {}, {}
        total, stats_closed, stats_current = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        eig_table_1, eig_table_2 = pd.DataFrame(), pd.DataFrame()

        while date <= pd.Timestamp('2022-09-25 23:00:00+00:00'):
            # print('Doing number ',count)
            # count = count + 1
        
            df = DP.token_price_data(m, date, df_token_universe, df_token_prices)
            s, tick, Q = PCA.PCA(df)

            dates.append(date) # used in building general tables 

            temp = pd.DataFrame()
            temp['Date'] = [date]*len(tick)
            temp['Ticker'] = tick
            temp['S-score'] = s
            total = pd.concat([total, temp],axis=0)
            
            # calculate opened and closed positions every hour:    
            prices = TS.find_prices(tick, date, df_token_prices)
            temp['Price'] = prices
            temp = temp.reset_index(drop=True)
            
            # before updating the positions, we want to calculate the return in the last hour, 
            # so we'll need the 'last' current positions
            if not stats_current.empty:
                last_tickers = list(stats_current['Ticker'])

            positions, stats_closed, stats_current = TS.strategy(positions, stats_closed, stats_current, temp)
            
            # part to calculate the return of the open and cumulative portfolio 
            s1, s2, l1, l2 = 0, 0, 0, 0

            if not stats_closed.empty:
                s1 = stats_closed['Return'].sum()
                l1 = len(stats_closed)
                
            if not stats_current.empty:
                s2 = stats_current['Return'].sum()
                l2 = len(stats_current)
            
            if l1 + l2 == 0:
                l2 = 1
            
            portfolio_value.append(s2 + l2)
            portfolio_ret_current.append(s2 / l2)
            portfolio_ret.append((s1 + s2)/(l1 + l2))
            
            # part to calculate the hourly returns:    
            if last_tickers == []:
                hour_returns.append(0)
            else:
                hour_returns.append(PM.last_ret(last_tickers, date, df_token_prices))
            
            # part to find return of eigen-vectors:    
            eigen_ret_1.append(PM.eigen_ret(Q[0], tick, date, df_token_prices, 1))
            eigen_ret_2.append(PM.eigen_ret(Q[1], tick, date, df_token_prices, 2))
            
            # part to create the eigen-vector csv:    
            eig_table_1 = self.update_eig_table(eig_table_1, tick, Q[0], date)
            eig_table_2 = self.update_eig_table(eig_table_2, tick, Q[1], date)
            
            # last step: update the time for the while statement to be updated    
            date = date + pd.DateOffset(hours=1)

        portfolio_ret_df = pd.DataFrame()
        portfolio_ret_df['Date'] = dates
        portfolio_ret_df['Return'] = portfolio_ret
        portfolio_ret_df['Portfolio Value'] = portfolio_value
        portfolio_ret_df['Current Portfolio Return'] = portfolio_ret_current

        # Hourly returns represents the returns of the portfolio composed of the opened 
        # positions in the last hour (so for hour h, the hourly return is from h-1 to h)
        portfolio_ret_df['Hourly Return'] = hour_returns

        eigen = pd.DataFrame()
        eigen['Date'] = dates
        eigen['Return 1'] = eigen_ret_1
        eigen['Return 2'] = eigen_ret_2
        eigen['Cum Ret 1'] = (1 + eigen['Return 1']).cumprod()
        eigen['Cum Ret 2'] = (1 + eigen['Return 2']).cumprod()

        return portfolio_ret_df, eigen, eig_table_1, eig_table_2, total, stats_closed, stats_current


    def df_btc_eth(self, df_token_prices: pd.DataFrame):
        """Creating a DataFrame for the Tokens BTC and ETH"""
        cols = ['startTime', 'BTC', 'ETH']
        # change start date to 1 hour before start so that we can have return in the first hour

        start_date = pd.Timestamp('2021-09-25 23:00:00+00:00')
        end_date = pd.Timestamp('2022-09-25 23:00:00+00:00')

        btc_eth = df_token_prices[cols]
        btc_eth = btc_eth[(btc_eth['startTime'] >= start_date) & (btc_eth['startTime'] <= end_date)]
        
        btc_eth['Ret BTC'] = btc_eth['BTC'].pct_change()
        btc_eth['Ret ETH'] = btc_eth['ETH'].pct_change()
        btc_eth['Cum Ret BTC'] = (1 + btc_eth['Ret BTC']).cumprod()
        btc_eth['Cum Ret ETH'] = (1 + btc_eth['Ret ETH']).cumprod()
        btc_eth.dropna(inplace=True)
        
        return btc_eth