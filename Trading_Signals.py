### ISYE 6767: Final Project
### Trading_Signals.py
##
#

import pandas as pd

class TradingSignals:
    def __init__(self):
        pass


    def find_prices(self, tick: list, date: pd.Timestamp , df: pd.DataFrame):
        """Get the Prices for given Tokens in a given Hour"""
        prices = []
        df = df[df['startTime'] == date]
        for i in tick:
            prices.append(float(df[i]))

        return prices


    def strategy(self, positions: dict, stats_closed: pd.DataFrame, stats_current: pd.DataFrame, df: pd.DataFrame):
        """Updates Open Positions and Statistics for both closed Positions and current Positions"""
        sbo = 1.25
        sso = 1.25
        sbc = 0.75
        ssc = 0.5

        positions, closed_positions = self.update_pos(positions, df, sbo, sso, sbc, ssc)
        stats_closed1 = self.update_stats_closed(closed_positions, stats_closed)
        date = df.loc[0, 'Date']
        stats_current = self.update_stats_current(positions, stats_current, date)

        return positions, stats_closed1, stats_current


    def update_pos(self, positions: dict, df: pd.DataFrame, sbo: float, sso: float, sbc: float, ssc: float):
        """Updates Open Positions and stores newly closed Positions"""
        closed_positions = []

        for i in range(len(df)):
            line = df.iloc[i, :]
            tick = line['Ticker']
            price = line['Price']
            s = line['S-score']
            date = pd.Timestamp(line['Date'])
            
            if tick in positions.keys():                
                positions[tick]['Current_Price'] = price
                
                if s < sbc and positions[tick]['Pos'] == -1:
                    positions[tick]['Close_Price'] = price
                    positions[tick]['Close_Date'] = date
                    closed_positions.append({tick:positions[tick]})
                    positions.pop(tick)
                    if s < -sbo:
                        positions[tick] = {'Pos':1, 'Open_Price':price, 'Open_Date':date, 'Current_Price':price}
                
                if tick in positions.keys():
                    if s > -ssc and positions[tick]['Pos'] == 1:
                        positions[tick]['Close_Price'] = price
                        positions[tick]['Close_Date'] = date
                        closed_positions.append({tick:positions[tick]})
                        positions.pop(tick)
                        if s > sso:
                            positions[tick] = {'Pos':-1, 'Open_Price':price, 'Open_Date':date, 'Current_Price':price}               
            
            if tick not in positions.keys():
                if s > sso:
                    positions[tick] = {'Pos':-1, 'Open_Price':price, 'Open_Date':date, 'Current_Price':price}
                if s < -sbo:
                    positions[tick] = {'Pos':1, 'Open_Price':price, 'Open_Date':date, 'Current_Price':price}
            
        return positions, closed_positions  
    

    def update_stats_closed(self, closed_positions: list, stats_closed: pd.DataFrame):
        """Updates the DataFrame with the newly closed Positions"""
        temp = pd.DataFrame()

        for i in closed_positions:
            ticker = list(i.keys())[0]
            temp['Ticker'] = [ticker]
            temp['Close_Date'] = i[ticker]['Close_Date']
            temp['Position'] = i[ticker]['Pos']
            temp['Open_Date'] = i[ticker]['Open_Date']
            temp['Open_Price'] = i[ticker]['Open_Price']
            temp['Close_Price'] = i[ticker]['Close_Price']
            temp['Return'] = (i[ticker]['Close_Price'] - i[ticker]['Open_Price']) / i[ticker]['Open_Price'] * i[ticker]['Pos']
            
            stats_closed = pd.concat([stats_closed, temp], axis=0)

        return stats_closed

    
    def update_stats_current(self, positions: dict, stats_curr: pd.DataFrame, date: pd.Timestamp):
        """Updates the DataFrame of currently opened Positions"""
        stats_curr = pd.DataFrame()
        temp = pd.DataFrame()

        for i in positions.keys():
            ticker = i
            temp['Date'] = [date]
            temp['Ticker'] = [ticker]
            temp['Position'] = positions[ticker]['Pos']
            temp['Open_Date'] = positions[ticker]['Open_Date']
            temp['Open_Price'] = positions[ticker]['Open_Price']
            temp['Current_Price'] = positions[ticker]['Current_Price']
            temp['Return'] = (positions[ticker]['Current_Price'] - positions[ticker]['Open_Price']) / positions[ticker]['Open_Price'] * positions[ticker]['Pos']
            
            stats_curr = pd.concat([stats_curr, temp], axis=0)

        return stats_curr