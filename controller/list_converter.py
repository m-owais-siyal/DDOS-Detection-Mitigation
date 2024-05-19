from sklearn.base import BaseEstimator, TransformerMixin

class ListConverter(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.apply(lambda x: [str(i) for i in x]).values

