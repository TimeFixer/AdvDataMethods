"""
src/data/make_dataset.py

Скрипт для подготовки датасета Diamonds к Лабораторной работе 1.
Требование методички:
Если в датасете нет пропусков — внести искусственно 10% пропусков
в две числовые колонки для последующей отработки импутации.
"""

from pathlib import Path
import numpy as np
import pandas as pd


def inject_missing_values(
    df: pd.DataFrame, columns: list[str], frac: float = 0.10, seed: int = 42
) -> pd.DataFrame:
  """Искусственно вносит пропуски (NaN) в указанные колонки."""
  np.random.seed(seed)
  df_modified = df.copy()

  for col in columns:
    mask = np.random.rand(len(df_modified)) < frac
    df_modified.loc[mask, col] = np.nan
    print(
        f"Колонка '{col}': внесено {mask.sum()} пропусков"
        f' ({mask.mean() * 100:.2f}%)'
    )

  return df_modified


def main():
    project_dir = Path(__file__).resolve().parents[2]
    
    # Исходный чистый датасет
    raw_data_path = project_dir / 'data' / 'raw' / 'diamonds.csv'
    
    # Новое имя для датасета с пропусками
    output_data_path = project_dir / 'data' / 'raw' / 'diamonds_with_missing.csv'

    df = pd.read_csv(raw_data_path)

    # Вносим пропуски
    df_modified = inject_missing_values(df, columns=['carat', 'depth'], frac=0.10, seed=42)

    # Сохраняем под новым именем
    df_modified.to_csv(output_data_path, index=False)
    print(f"Сохранено в: {output_data_path}")


if __name__ == '__main__':
  main()