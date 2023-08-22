### ISYE 6767: Final Project
### Data_Processing.py
##
#

import pandas as pd

class DataProcessing:
    def __init__(self):
        pass


    def import_data(self, path: str, CSV_file: str):
        """Importing CSV File with a Header"""
        data = pd.read_csv(path + '/' + CSV_file)
        
        return data


    def clean_df(self, df: pd.DataFrame, col_name1: str, col_name2: str):
        """Data Cleaning with Forward Fill"""
        df[col_name1] = pd.to_datetime(df[col_name1])
        df.drop(col_name2, axis=1, inplace=True)
        df = df.sort_values(col_name1)
        df.fillna(method='ffill', inplace=True)
        
        return df


    def find_top40(self, t: pd.Timestamp, df: pd.DataFrame):
        """Evaluate the Set of the 40 largest Market-Cap Tokens in a given Hour"""
        temp = df[df['startTime']==t].iloc[0, 1:]
        l = list(temp)
        # we add BTC and ETH in the case they are not present since we need the s-scores for both 
        # in the period from inception to 2021-10-25 23:00:00

        if 'ETH' not in l:
            l.append('ETH')

        if 'BTC' not in l:
            l.append('BTC')

        return l


    def token_price_data(self, m: int, t: pd.Timestamp, df_token_universe: pd.DataFrame, df_token_prices: pd.DataFrame):
        """Get the Intersection of the largest 40 Tokens and the Market Data"""
        # m is window, t is starting time, df_token_prices is dataframe with top 40 cryptos at time t 
        l = self.find_top40(t, df_token_universe)
        l.append('startTime')
        df = df_token_prices[df_token_prices.columns.intersection(l)]
        start = t - pd.DateOffset(hours=m)
        df = df[(df['startTime'] <= t) & (df['startTime'] >= start)]

        # we now deal with possible missing values
        df = df.fillna(method='ffill')

        return df


    