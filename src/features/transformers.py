import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class CutOrdinalEncoder(BaseEstimator, TransformerMixin):
  """Кастомный трансформер для Варианта 9:

  преобразует признак 'cut' в порядковый числовой код.
  """

  CUT_MAPPING = {
      'Fair': 0,
      'Good': 1,
      'Very Good': 2,
      'Premium': 3,
      'Ideal': 4,
  }

  def __init__(self, column_name='cut'):
    self.column_name = column_name

  def fit(self, X, y=None):
    return self

  def transform(self, X):
    X_df = X.copy()
    if self.column_name in X_df.columns:
      # Заменяем категорию числом; неизвестные значения заполняются -1
      X_df[self.column_name] = (
          X_df[self.column_name].map(self.CUT_MAPPING).fillna(-1).astype(float)
      )
    return X_df