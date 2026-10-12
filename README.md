# Автоматическая генерация признаков (Featuretools, DFS)
Ветка: `feat/featuretools_dfs`
Ноутбук с решением: `notebooks/pract_featuretools_dfs.ipynb`

---

## 1. Цель работы
Освоить автоматическую инженерию признаков для реляционных структур данных с помощью библиотеки **Featuretools** и алгоритма **Deep Feature Synthesis (DFS)**:
* Синтезировать взаимосвязанный набор из 4 реляционных таблиц.
* Построить граф связей в контейнере `EntitySet`.
* Сгенерировать многоуровневые агрегационные и трансформационные признаки с глубиной `max_depth=2` для сущности `customers`.
* Проанализировать полученную матрицу признаков.

---

## 2. Схема данных и связи
Для имитации предметной области интернет-магазина сгенерированы следующие сущности:

| Таблица | Первичный ключ | Внешние ключи | Описание | Размерность |
|---|---|---|---|---|
| **`customers`** | `client_id` | — | Данные клиентов (`name`, `join_date`, `region`) | 50 строк |
| **`products`** | `product_id` | — | Каталог товаров (`category`, `price`) | 20 строк |
| **`orders`** | `order_id` | `client_id` | Заказы клиентов (`order_date`, `total_amount`) | 150 строк |
| **`order_items`** | `item_id` | `order_id`, `product_id` | Позиции в заказах (`quantity`) | 400 строк |

### Реляционный граф:
```text
[customers] ──(1:N)──> [orders] ──(1:N)──> [order_items] <──(N:1)── [products]
```
* `customers.client_id` → `orders.client_id`
* `orders.order_id` → `order_items.order_id`
* `products.product_id` → `order_items.product_id`

---

## 3. Настройка EntitySet и параметры DFS
1. **Контейнер `EntitySet`**:
   * Все таблицы добавлены в сущность `retail_store` с явным указанием индексов и временных меток (`time_index='order_date'`).
   * Добавлен патч совместимости аксессуаров `Woodwork` для работы с Pandas 2.x.
2. **Конфигурация алгоритма DFS (`ft.dfs`)**:
   * **Целевая таблица**: `customers`.
   * **Глубина связей (`max_depth`)**: `2` (позволяет агрегировать данные с уровня позиций заказов на уровень клиента через заказы).
   * **Агрегационные примитивы (`agg_primitives`)**: `sum`, `mean`, `count`, `max`, `min`, `std`.
   * **Трансформационные примитивы (`trans_primitives`)**: `day`, `month`, `year`.

---

## 4. Результаты работы
* **Размерность итоговой матрицы признаков**: `(50, 46)` (для 50 клиентов создано 46 признаков вместо исходных 3).
* **Всего сгенерировано признаков**: 46.

### Примеры сгенерированных признаков по уровням глубины:
* **Прямые признаки сущности (`Identity / Transform`)**:
  * `DAY(join_date)`, `MONTH(join_date)`, `YEAR(join_date)`.
* **Глубина 1 (прямая агрегация `orders` → `customers`)**:
  * `COUNT(orders)` — суммарное число заказов.
  * `SUM(orders.total_amount)` — общий объём покупок клиента.
  * `MEAN(orders.total_amount)` — средний чек.
  * `STD(orders.total_amount)` — дисперсия чеков.
* **Глубина 2 (двухуровневая агрегация `order_items` → `orders` → `customers`)**:
  * `MEAN(orders.MEAN(order_items.quantity))` — среднее средних количеств единиц товара в корзине.
  * `MAX(orders.SUM(order_items.quantity))` — максимальное суммарное число позиций в одном заказе клиента.
  * `SUM(order_items.orders.total_amount)` — совокупная стоимость через сквозные связи позиций.

---

## 5. Воспроизводимость
1. Установите зависимости:
```bash
pip install featuretools "setuptools<70"
```
