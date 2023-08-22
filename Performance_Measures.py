### ISYE 6767: Final Project
### Performance_Measures.py
##
#

import pandas as pd
import numpy as np

class PerformanceMeasures:
    def __init__(self):
        pass


    def extract_ret(self, hour: pd.Timestamp, ticker: str, df: pd.DataFrame):
        """Finds Return for a given Token between the given Hour and the next Hour"""
        temp = df[df['startTime'] >= hour][ticker][0:2].pct_change().iloc[1]

        return temp


    def last_ret(self, tickers: list, hour: pd.Timestamp, df: pd.DataFrame):
        """Finds Return for a given list of Tokens between the given Hour and the previous Hour"""
        # we want the return from the last hour to 'hour', so we'll need to change the hour
        # we feed into extract_ret
        hour = hour - pd.DateOffset(hours=1)
        l = []
        for tick in tickers:
            l.append(self.extract_ret(hour, tick, df))

        return np.array(l).mean()


    def eigen_ret(self, array: np.array, tickers: list, hour: pd.Timestamp, df: pd.DataFrame, x: int):
        """Finds the Return of the given Eigenportfolio in the given Hour, Normalizing only the first Eigenportfolio"""
        l = []
        for tick in tickers:
            l.append(self.extract_ret(hour, tick, df))
        l = np.array(l)

        if x == 2:
            return array @ l
        else:
            return array @ l / array.sum()


    def mdd(self, start: pd.Timestamp, end: pd.Timestamp, df: pd.DataFrame):
        """Calculates the Maximum Drawdown between the two given Dates"""
        # here, df should be portfolio_ret_df
        series = df[(df['Date'] <= end) & (df['Date'] >= start)]['Portfolio Value']

        return (min(series) - max(series)) / max(series)


    def sharpe(self, start: pd.Timestamp, end: pd.Timestamp, df: pd.DataFrame):
        """Calculates the Sharpe Ratio between the two given Dates"""
        # here, df should be portfolio_ret_df
        series = df[(df['Date'] <= end) & (df['Date'] >= start)]['Hourly Return']

        return series.mean() / series.std()


