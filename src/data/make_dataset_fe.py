from pathlib import Path
import numpy as np
import pandas as pd

def main():
    project_dir = Path(__file__).resolve().parents[2]
    
    # Берем данные с пропусками из первого модуля
    input_path = project_dir / 'data' / 'raw' / 'diamonds_with_missing.csv'
    output_path = project_dir / 'data' / 'raw' / 'diamonds_fe.csv'

    df = pd.read_csv(input_path)
    rng = np.random.default_rng(42)
    
    # Добавляем синтетические выбросы в числовые колонки (умножаем на 5..10)
    outlier_cols = ["carat", "table", "x"]
    n_outliers = int(0.005 * len(df))
    
    for col in outlier_cols:
        valid_idx = df[df[col].notna()].index
        chosen_idx = rng.choice(valid_idx, size=n_outliers, replace=False)
        factors = rng.uniform(5.0, 10.0, size=n_outliers)
        df.loc[chosen_idx, col] = df.loc[chosen_idx, col] * factors
        print(f"В колонку '{col}' добавлено {n_outliers} выбросов.")

    df.to_csv(output_path, index=False)
    print(f"Сохранено в: {output_path}")

if __name__ == '__main__':
    main()