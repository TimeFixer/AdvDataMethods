import torch
import torch.nn as nn

class DiamondsMLP(nn.Module):
    """
    Гибридная нейросеть для прогнозирования стоимости бриллиантов:
    - Категориальные признаки обрабатываются через обучаемые nn.Embedding.
    - Числовые признаки конкатенируются с эмбеддингами и подаются на MLP.
    """
    def __init__(self, cat_cardinalities, num_numeric_features):
        super().__init__()
        
        # Создаем список эмбеддингов для каждого категориального признака
        # Эмбеддинг-размерность выбирается эвристически: min(50, (cardinality + 1) // 2)
        self.embeddings = nn.ModuleList([
            nn.Embedding(num_classes, embed_dim)
            for num_classes, embed_dim in cat_cardinalities
        ])
        
        total_embed_dim = sum(embed_dim for _, embed_dim in cat_cardinalities)
        input_dim = total_embed_dim + num_numeric_features
        
        self.network = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 1)  # Регрессия: предсказание цены (price)
        )
        
    def forward(self, x_cat, x_num):
        # x_cat: тензор индексов категорий (batch_size, num_cat_features)
        # x_num: тензор числовых признаков (batch_size, num_numeric_features)
        
        embedded = [emb(x_cat[:, i]) for i, emb in enumerate(self.embeddings)]
        x_cat_concat = torch.cat(embedded, dim=1)
        
        x = torch.cat([x_cat_concat, x_num], dim=1)
        return self.network(x).squeeze(-1)