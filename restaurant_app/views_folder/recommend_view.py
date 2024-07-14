from django.shortcuts import render
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
from ..models.orders import Order, OrderItem
from ..models.product import Product
import pandas as pd

def recommend_view(request, order_id):
    # Получаем заказ пользователя
    user_order = Order.objects.get(id=order_id)
    table = user_order.table  # Получаем стол, связанный с заказом
    user_order_items = OrderItem.objects.filter(order=user_order)
    user_products = [item.product for item in user_order_items]

    # Получаем идентификатор активного стола
    active_table_id = user_order.table.table_id

    # Получаем все завершенные заказы и сопутствующие объекты OrderItem и Product
    completed_orders = Order.objects.filter(is_completed=True).prefetch_related('order_items__product')
    # Создаем список транзакций (список списков), где каждый внутренний список - это продукты в одном заказе
    transactions = [[item.product.product_name_rus for item in order.order_items.all()] for order in completed_orders]

    # Преобразование транзакций в формат, который может быть использован библиотекой mlxtend
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)

    # Преобразование в DataFrame
    df = pd.DataFrame(te_ary, columns=te.columns_)

    # Поиск часто встречающихся наборов продуктов с помощью алгоритма apriori
    frequent_itemsets = apriori(df, min_support=0.001, use_colnames=True)

    # Генерация ассоциативных правил
    rules = association_rules(frequent_itemsets, metric="leverage", min_threshold=0.001)

    # Создаем список для хранения рекомендаций для каждого продукта
    recommendations = []
    all_recommended_products = set()  # Добавляем set для отслеживания всех рекомендованных продуктов
    for product in user_products:
        product_recommendations = []
        for rule in rules.itertuples():
            antecedents = ', '.join(sorted(list(rule.antecedents)))
            consequents = ', '.join(sorted(list(rule.consequents)))
            # Проверяем, является ли любой из продуктов пользователя антецедентом и не является ли он последствием 
            if any(product.product_name_rus in antecedents for product in user_products) and consequents not in [product.product_name_rus for product in user_products] and consequents not in all_recommended_products:
                recommended_product = Product.objects.get(product_name_rus=consequents)
                product_recommendations.append({
                    'product': recommended_product,
                    'confidence': rule.confidence
                })
                all_recommended_products.add(consequents)  # Добавляем продукт в set всех рекомендованных продуктов
                if len(product_recommendations) >= 3:  # Ограничиваем количество рекомендаций до трех
                    break
        recommendations.append({
            'product': product,
            'recommendations': product_recommendations
        })

    # Отправка рекомендаций и стола в шаблон
    context = {
        'recommendations': recommendations,
        'table': table,  # Передаем стол в контекст
        'active_table_id': table.id  # Добавляем id стола в контекст
    }
    return render(request, 'recommendations.html', context)
