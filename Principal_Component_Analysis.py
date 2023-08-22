### ISYE 6767: Final Project
### Principal_Component_Analysis.py
##
#

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

class PrincipalComponentAnalysis:
    def __init__(self):
        pass


    def corr_matrix(self, df: pd.DataFrame):
        """Computation of the Empirical Correlation Matrix"""
        r1 = df.iloc[:, 1:].pct_change()
        std_vec = []
        # first row is NaN because of how pct_change() is defined
        r = r1.iloc[1:, :]
        indexes = []
        indexes2 = []
        R = pd.DataFrame()
        tickers = list(df.iloc[:, 1:].columns)
        bad_tickers = []
        
        for i in range(len(r.columns)):
            # fill NaNs with 0 since they are caused by the price being zero before a certain date
            z = r.iloc[:, i].fillna(0)
            # replace inf with 0, since inf is caused by the first price different from 0
            z.replace([np.inf, -np.inf], 0, inplace=True)
            R = pd.concat([R, z], axis=1)
            mean = z.mean()
            std = z.std()
            if std > 0:
                r.iloc[:, i] = (z - mean) / std
            else:
                r.iloc[:, i] = (z - mean)
            
            # condition to check whether all values of a column are zero: in such case, the 
            # correlation matrix would have NaNs so we drop that column 
            if (r.iloc[:, i] == 0).all() == True:
                indexes.append(i)
                indexes2.append(i + 1)
                bad_tickers.append(r.iloc[:, i].name)
            else:
                std_vec.append(std)
                
        r.drop(r.columns[indexes], axis=1, inplace=True)
        R.drop(R.columns[indexes], axis=1, inplace=True)
        df.drop(df.columns[indexes2], axis=1, inplace=True)
        
        temp = [ele for ele in tickers if ele not in bad_tickers]
        tick = temp
        
        return r.corr(), np.array(std_vec), df, R, tick 


    def eigen_p(self, sigma: pd.DataFrame, n_components: int, sig_vec: np.array):
        """Principal Component Analysis & Computation of Eigenportfolios"""
        eigen_values , eigen_vectors = np.linalg.eigh(sigma)
        sorted_index = np.argsort(eigen_values)[::-1]
        eigenvalue_sorted = eigen_values[sorted_index]
        eigenvectors_sorted = eigen_vectors[:, sorted_index]
        eigenvector_subset = eigenvectors_sorted[:, 0:n_components]
        
        Q = eigenvector_subset.T
        Q = Q * (1 / sig_vec)

        return Q


    def factor_returns(self, df: pd.DataFrame, Q: np.array, R: pd.DataFrame):
        """Factor Returns of the Risk Factors j"""
        ret = np.array(R)
        F = ret @ Q.T

        return F.T

    
    def linear_regression1(self, df: pd.DataFrame, F: np.array, R: pd.DataFrame):
        """Estimate Residual Returns of Token S_c_i"""
        X = F.T
        # first value of X is nan because of how pct_change is defined
        X = X[1:]
        
        alpha, beta1, beta2, res = [], [], [], []
        
        for i in range(len(R.columns)):
            Y = R.iloc[1:, i]
            # we have to deal with the case in which X has NaNs:
            
            Z = pd.concat([pd.DataFrame(X), Y])
            reg = LinearRegression().fit(X, Y)
            alpha.append(reg.intercept_)
            beta1.append(reg.coef_[0])
            beta2.append(reg.coef_[1])
            
            new_col = np.ones(X.shape[0]).reshape((X.shape[0], 1))
            Z = np.append(new_col, X, 1)
            res.append(np.array(Y) - Z @ np.array([reg.intercept_, reg.coef_[0], reg.coef_[1]]))

        return alpha, beta1, beta2, res


    def linear_regression2(self, res: np.array):
        """Estimation of the Residual Process"""
        a, b, eta = [], [], []  
        
        for i in range(len(res)):
            X = res[i].cumsum()[:-1].reshape((-1, 1))
            Y = res[i].cumsum()[1:]
            reg = LinearRegression().fit(X, Y)
            a.append(reg.intercept_)
            b.append(reg.coef_[0])
            
            new_col = np.ones(X.shape[0]).reshape((X.shape[0], 1))
            Z = np.append(new_col, X, 1)
            eta.append(np.array(Y) - Z@np.array([reg.intercept_,reg.coef_[0]]))
            
        return a, b, eta


    def OU_parameters(self, a: list, b: list, eta: list):
        """Estimating Co-Integration residuals as Ornstein-Uhlenbeck Processes"""
        # deltaT is 8760 here since we consider the number of hours in one year 
  
        k = -np.log(b) * 8760
        m = np.array(a) / (1 - np.array(b))
        
        var = np.std(np.array(eta), axis=1)**2
        sigma = np.sqrt(var * 2 * k / (1 - np.array(b)**2))
        sigma_eq = np.sqrt(var / (1 - np.array(b)**2))
        
        return k, m, sigma, sigma_eq


    def s_score(self, m: np.array, sigma_eq: np.array):
        """Calculation of the S-Scores"""
        s = (m.mean() - m) / sigma_eq

        return s


    def PCA(self, df: pd.DataFrame):
        """Application of the Principal Component Analysis"""
        sigma, sig_vec, df2, R, tick = self.corr_matrix(df)
        Q = self.eigen_p(sigma, 2, sig_vec)
        F = self.factor_returns(df2, Q, R)
        alpha, b1, b2, res = self.linear_regression1(df2, F, R)
        a, b3, eta = self.linear_regression2(res)
        k, m, sigma, sigma_eq = self.OU_parameters(a, b3, eta)
        s = self.s_score(m, sigma_eq)

        return s, tick, Q




