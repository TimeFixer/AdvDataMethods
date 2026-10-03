# Практическое задание: Автоматическая генерация признаков (Featuretools, DFS)

Ветка: `feat/featuretools_dfs`  
Ноутбук с решением: `notebooks/pract_featuretools_dfs.ipynb` (или `notebooks/02_featuretools_dfs.ipynb`)[cite: 75]

---

## 1. Цель работы

Освоить автоматическую инженерию признаков для реляционных структур данных с помощью библиотеки **Featuretools** и алгоритма **Deep Feature Synthesis (DFS)**[cite: 66, 73]:
* Синтезировать взаимосвязанный набор из 4 реляционных таблиц[cite: 73].
* Построить граф связей в контейнере `EntitySet`[cite: 67, 69, 73].
* Сгенерировать многоуровневые агрегационные и трансформационные признаки с глубиной `max_depth=2` для сущности `customers`[cite: 70, 73].
* Проанализировать полученную матрицу признаков[cite: 73].

---

## 2. Схема данных и связи

Для имитации предметной области интернет-магазина сгенерированы следующие сущности[cite: 68, 73, 75]:

| Таблица | Первичный ключ | Внешние ключи | Описание | Размерность |
|---|---|---|---|---|
| **`customers`** | `client_id` | — | Данные клиентов (`name`, `join_date`, `region`)[cite: 73, 75] | 50 строк[cite: 75] |
| **`products`** | `product_id` | — | Каталог товаров (`category`, `price`)[cite: 73, 75] | 20 строк[cite: 75] |
| **`orders`** | `order_id` | `client_id` | Заказы клиентов (`order_date`, `total_amount`)[cite: 73, 75] | 150 строк[cite: 75] |
| **`order_items`** | `item_id` | `order_id`, `product_id` | Позиции в заказах (`quantity`)[cite: 73, 75] | 400 строк[cite: 75] |

### Реляционный граф:
```text
[customers] ──(1:N)──> [orders] ──(1:N)──> [order_items] <──(N:1)── [products]
```
* `customers.client_id` $\rightarrow$ `orders.client_id`[cite: 75]
* `orders.order_id` $\rightarrow$ `order_items.order_id`[cite: 75]
* `products.product_id` $\rightarrow$ `order_items.product_id`[cite: 75]

---

## 3. Настройка EntitySet и параметры DFS

1. **Контейнер `EntitySet`**:
   * Все таблицы добавлены в сущность `retail_store` с явным указанием индексов и временных меток (`time_index='order_date'`)[cite: 69, 75].
   * Добавлен патч совместимости аксессуаров `Woodwork` для работы с Pandas 2.x[cite: 75].

2. **Конфигурация алгоритма DFS (`ft.dfs`)**[cite: 70, 75]:
   * **Целевая таблица**: `customers`[cite: 70, 75].
   * **Глубина связей (`max_depth`)**: `2` (позволяет агрегировать данные с уровня позиций заказов на уровень клиента через заказы)[cite: 70, 71, 73].
   * **Агрегационные примитивы (`agg_primitives`)**: `sum`, `mean`, `count`, `max`, `min`, `std`[cite: 70, 75].
   * **Трансформационные примитивы (`trans_primitives`)**: `day`, `month`, `year`[cite: 70, 75].

---

## 4. Результаты работы

* **Размерность итоговой матрицы признаков**: `(50, 46)` (для 50 клиентов создано 46 признаков вместо исходных 3)[cite: 75].
* **Всего сгенерировано признаков**: 46[cite: 75].

### Примеры сгенерированных признаков по уровням глубины:
* **Прямые признаки сущности (`Identity / Transform`)**:
  * `DAY(join_date)`, `MONTH(join_date)`, `YEAR(join_date)`[cite: 75].
* **Глубина 1 (прямая агрегация `orders` $\rightarrow$ `customers`)**:
  * `COUNT(orders)` — суммарное число заказов[cite: 71, 75].
  * `SUM(orders.total_amount)` — общий объём покупок клиента[cite: 71, 75].
  * `MEAN(orders.total_amount)` — средний чек[cite: 75].
  * `STD(orders.total_amount)` — дисперсия чеков[cite: 75].
* **Глубина 2 (двухуровневая агрегация `order_items` $\rightarrow$ `orders` $\rightarrow$ `customers`)**:
  * `MEAN(orders.MEAN(order_items.quantity))` — среднее средних количеств единиц товара в корзине[cite: 75].
  * `MAX(orders.SUM(order_items.quantity))` — максимальное суммарное число позиций в одном заказе клиента[cite: 75].
  * `SUM(order_items.orders.total_amount)` — совокупная стоимость через сквозные связи позиций[cite: 75].

---

## 5. Воспроизводимость

1. Установите зависимости:
   ```bash
   pip install featuretools "setuptools<70"