# README FILE

### Problem addressed

In this project we applied a statistical arbitrage method, derived from the paper ‘Statistical Arbitrage in the US equities market’ by Marco Avellaneda and Jeong-Hyun Lee. We are basically trying to create a strategy that profits from the fact that individual securities (in this case cryptocurrencies) have idiosyncratic returns that follow a mean-reverting process. Therefore, if the residuals (which are idiosyncratic returns) of the regression of returns on factors deviate from their mean, we open a position that would profit from the mean- reverting movement of the residuals. We determine the factors F thanks to the PCA, and use those factors F as variables on which to regress the returns and find the residuals, or idiosyncratic returns. Once we find the residuals, under the assumption that they follow a mean-reverting process (namely the Ornstein-Uhlenbeck process) we calculate the parameters of such process and create a trading signal based on such parameters: the s- score. We then construct a trading strategy based, in every hour, on current s-scores and previously opened positions.

### Technical models

The first technical model we use in the project is the PCA. PCA is a statistical technique used for reducing the dimensionality of a dataset. In our case, we are interested in describing the returns of single cryptocurrencies with two factors (components) at each time point (hours in our case). The two factors that we calculate are a simple transformation of the two eigen- vectors corresponding to the two greatest eigenvalues of the empirical correlation matrix of the normalized returns. From a modelization point of view, the greatest the eigenvalue, the greatest is the amount of variance of the returns that is explained. We therefore choose the two eigenvalues that represent the greatest amount of variance of the returns.
The second technical model we use is the linear regression. Once we calculate the factors thanks to a linear transformation of the eigenvectors coming from the PCA, we regress the returns on the factors (that is, we try to explain the returns of the cryptocurrencies with the factors). We perform a regression for every coin in the top 40, every hour. The residuals of such regressions represent the idiosyncratic component of the returns and are the starting point for the rest of the project.
Once we have a set of residuals for each coin at each hour, we apply the third technical model: we assume the residuals follow the Ornstein-Uhlenbeck process. To estimate the parameters of such a process we define an auxiliary process as the sum of the residuals coming from the previous regression (separately for each coin). This auxiliary process can be seen as a discrete version of the process followed theoretically by the residuals. We then run a second regression on the lagged partial sums of the auxiliary process, finding the parameters of the original OU process and the quantities necessary to calculate the s-score.
Explanation of the functionalities of key classes/functions and their inputs/outputs
We implemented our code with the use of 5 classes: DataProcessing, TradingSignals, PrincipalComponentAnalysis and PerformanceMeasures and Project_Implementation.

### DataProcessing class:

This class is responsible for importing, cleaning and pre-processing data. The importing and cleaning is done with the import_data and clean_df functions, which have the role to prepare the dataframes containing the prices of tokens and the top 40 tokens for each hour. While cleaning, a forward fill is done to handle any eventuals NaNs.
The token_price_data function makes use of the find_top_40 function to return, for a given hour t, a DataFrame containing the hourly data going back m hours for the top 40 tokens in that given hour. Given that later in the code we will need the data for ETH and BTC regardless if they are in the top 40 or not, we add a part of code in find_top40 function to deal with the case in which they are not present. Thus, theorically the token_price_data function can return data for up to 42 tokens.

### PrincipalComponentAnalysis class:

This class deals with the implementation of all the technical models discussed previously. The PCA function in this class is responsible for running all the other functions of the class and returning key variables for the rest of the project: s-scores, corresponding tickers and the two eigenportfolios (stored in Q). The input of the PCA function is a DataFrame containing the prices of the top-40 tokens for a given hour h, with data going back to h-m.

Here are the functions that appear, first to last, in the PCA function:

The corr_matrix function receives the afore-mentioned DataFrame of prices and, after calculating the returns and normalizing them, it returns the empirical correlation matrix. It also returns other quantities that will be used in the next functions: a DataFrame containing the returns before the normalization (R), an array containing the sd of the returns of each token (std_vec), the tickers and the original DataFrame of prices. All these outputs account for the fact that in some cases the price of the token was 0 for all the hours before the last one, which would have led to a correlation matrix with NaNs. We therefore opted to drop the return column that caused this in all the outputs (for arrays/lists, this means dropping the element).

The eigen_p function calculates the first n_components eigenportfolios as defined in the paper, starting from the empirical correlation matrix.

The factor_returns function calculates the factor returns as defined in the paper starting from the returns and the eigenportfolios calculated before.

The linear_regression1 function performs the first linear regression cited in the models section (‘second technical model’). As said before, it finds the coefficients that explain the returns starting from the factor returns calculated above. The estimated parameters of the regression are stored in alpha, beta1 and beta2 lists, while the residuals are manually calculated and stores in a list of arrays: res. One regression is performed for each token.

The linear_regression2 function applies the second linear regression cited in models section. Starting from the residuals of the previous regression, it constructs the auxiliary process and uses it to estimate the parameters a and b. Also, residuals eta from this second regression are calculated, again manually.

The functions OU_parameters and s_score simply apply the formulas in the paper to calculate the parameters of the original OU process modelling the idiosyncratic returns and the s-scores, which are the starting point for the rest of the project.

### Trading_Signals class:

The Trading_Signals class is responsible for the implementation of the trading strategy given
the s-scores calculated thanks to the PCA class.
We decided to implement the strategy with the use of dictionaries. At every hour, we update the dictionary of opened positions and create a dictionary with the newly closed positions. We do so by confronting the dictionary of opened positions with (*) a DataFrame containing the s-scores and prices for all the tokens in a given hour. We thought of this approach because this way we could keep track of the previously opened positions and, at the same time, record important statistics on the trades that we made (open price, current/close price, open date, close/current date).
Practically, in the implementation function of the Project_Implementation class we first define the empty dictionary for closed positions and empty DataFrames for the trade statistics. For each step of the while loop (which means at each hour) we call the strategy function of the Trading_Signals class, which updates the opened positions dictionary and the trading statistics.
The update_pos function, called in the strategy function, is the key element of the strategy implementation. Here, we use (*) (named df in the function) to confront the current s- scores with the opened positions from an hour earlier. We always update the current price of the positions and, if certain conditions are met, we close the position. This means practically (1) adding the closing price and closing date information to the element of the dictionary, (2) appending the position to the closed_positions list, (3) eliminating the position from the current positions’ dictionary (positions).
The update_stats_closed and update_stats_current functions make use, respectively, of the newly created closed_positions and the newly updated positions to update DataFrames containing useful information for the closed and open trades. In such DataFrames, each row represents a single trade. The ‘Position’ column is 1 when the position was long and -1 when a position was short.

### Performance_Measures class:

This class contains a set of functions used to calculate the performance measures of the strategy. To facilitate with the calculation of the returns of a given portfolio, we constructed the extract_ret function that calculates the returns for a given token between the given

hour and the next hour. The eigen_ret function makes use of such function to calculate the returns of the eigenportfolios in a given hour.

### Project_ Implementation class:

This class is mainly responsible for the implementation of the totality of our code, from the start (importing and preprocessing) to the finish (calculation of performance measures and various portfolio returns). This is done in the implementation function. The update_eig_table and df_btc_eth functions are responsible for building DataFrames for the visualization of the strategy performance.
In the implementation function, a while loop on the hours is created and functions from each of the 4 other classes are called. A set of DataFrames, lists and dictionaries is updated at each step of the loop in order to have data on which to compute performance measures and evaluate the strategy.
