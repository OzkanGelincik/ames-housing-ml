import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

# ==========================================
# 1. CORRELATION THRESHOLD (Redundancy Remover)
# ==========================================
class CorrelationThreshold(BaseEstimator, TransformerMixin):
    def __init__(self, threshold=0.9):
        self.threshold = threshold
        self.to_drop_ = []

    def fit(self, X, y=None):
        if isinstance(X, pd.DataFrame):
            corr_matrix = X.corr().abs()
        else:
            corr_matrix = pd.DataFrame(X).corr().abs()
        
        # Select upper triangle of correlation matrix
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        
        # Find features with correlation greater than threshold
        self.to_drop_ = [column for column in upper.columns if any(upper[column] > self.threshold)]
        return self

    def transform(self, X, y=None):
        if isinstance(X, pd.DataFrame):
            return X.drop(columns=self.to_drop_)
        return X.drop(columns=self.to_drop_)

# ==========================================
# 2. FEATURE ENGINEER (Geospatial & Logic)
# ==========================================
class FeatureEngineer(BaseEstimator, TransformerMixin):
    def __init__(self, coords_dict=None):
        """
        coords_dict: A dictionary mapping Neighborhood codes to (Lat, Lon).
                     Example: {'NAmes': (42.042, -93.613), ...}
        """
        self.coords_dict = coords_dict

    def fit(self, X, y=None):
        # This transformer doesn't need to learn anything from the data,
        # so fit just returns self.
        return self
    
    def transform(self, X):
        # Create a copy to avoid SettingWithCopy warnings
        X = X.copy()
        
        # --- LOGIC 1: Total Square Footage (The "King" Feature) ---
        bsmt = X['TotalBsmtSF'] if 'TotalBsmtSF' in X.columns else 0
        first = X['1stFlrSF'] if '1stFlrSF' in X.columns else 0
        second = X['2ndFlrSF'] if '2ndFlrSF' in X.columns else 0
        X['TotalHouseSqFt'] = bsmt + first + second
        
        # --- LOGIC 2: House Age ---
        if 'YearBuilt' in X.columns and 'YrSold' in X.columns:
            X['HouseAge'] = X['YrSold'] - X['YearBuilt']
            
        # --- LOGIC 3: Total Bathrooms ---
        full = X['FullBath'] if 'FullBath' in X.columns else 0
        half = X['HalfBath'] if 'HalfBath' in X.columns else 0
        bsmt_full = X['BsmtFullBath'] if 'BsmtFullBath' in X.columns else 0
        bsmt_half = X['BsmtHalfBath'] if 'BsmtHalfBath' in X.columns else 0
        X['TotalBath'] = full + (0.5 * half) + bsmt_full + (0.5 * bsmt_half)

        # --- LOGIC 4: Geospatial Mapping ---
        if self.coords_dict is not None and 'Neighborhood' in X.columns:
            # We use .map() to look up the tuple (Lat, Lon)
            # If a neighborhood is missing from the dict, we default to a central point
            # Taking [0] for Lat and [1] for Lon
            X['Lat'] = X['Neighborhood'].map(lambda x: self.coords_dict.get(x, (42.0347, -93.6200))[0])
            X['Lon'] = X['Neighborhood'].map(lambda x: self.coords_dict.get(x, (42.0347, -93.6200))[1])

        return X
