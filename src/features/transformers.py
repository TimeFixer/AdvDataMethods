import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.ensemble import IsolationForest


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


class DiamondFeatureGenerator(BaseEstimator, TransformerMixin):
    """Генерация новых признаков (взаимодействия и нелинейности) для числовой матрицы."""

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        # На вход поступает numpy-массив после ColumnTransformer
        X_arr = np.asarray(X, dtype=float)
        
        # Порядок колонок после препроцессора:
        # [carat, depth, table, x, y, z, cut, (плюс one-hot колонки цвета и чистоты)]
        carat = X_arr[:, 0:1]
        depth = X_arr[:, 1:2]
        table = X_arr[:, 2:3]
        x = X_arr[:, 3:4]
        y = X_arr[:, 4:5]
        z = X_arr[:, 5:6]

        volume = x * y * z                          # Приблизительный объем бриллианта
        carat_sq = carat ** 2                       # Нелинейный вес
        depth_table_ratio = depth / (np.abs(table) + 1e-5) # Отношение глубины к площадке

        return np.hstack([X_arr, volume, carat_sq, depth_table_ratio])


class IsolationForestOutlierRemover(BaseEstimator):
    """Удаление выбросов с помощью IsolationForest только из обучающей выборки (train).

    Предназначено для использования внутри imblearn.pipeline.Pipeline через метод fit_resample.
    """
    _sampling_type = "bypass"

    def __init__(self, contamination=0.02, random_state=42):
        self.contamination = contamination
        self.random_state = random_state

    def fit(self, X, y=None):
        self.iso_ = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.iso_.fit(X)
        return self

    def fit_resample(self, X, y):
        self.fit(X, y)
        preds = self.iso_.predict(X)
        mask = preds == 1  # 1 — нормальные объекты, -1 — выбросы

        if isinstance(X, pd.DataFrame):
            X_res = X.iloc[mask]
        else:
            X_res = X[mask]

        if isinstance(y, (pd.Series, pd.DataFrame)):
            y_res = y.iloc[mask]
        else:
            y_res = y[mask]

        return X_res, y_res