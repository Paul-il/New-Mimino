import pandas as pd
from django.core.management import BaseCommand
from restaurant_app.models.orders import Order

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        # Получаем все объекты Order
        orders = Order.objects.all()

        # Создаем словарь для данных
        data = {
            "ID": [],
            "Table": [],
            "Created By": [],
            "Created At": [],
            "Updated At": [],
            "Is Completed": [],
            "Comments": [],
            "Last Printed Comments": [],
            "Table Number": [],
            "Total Price": [],
            "Status": [],
            "Payment Method": [],
            "Total Sum": [],
        }

        # Заполняем словарь данными из каждого объекта
        for order in orders:
            data["ID"].append(order.pk)
            data["Table"].append(str(order.table))
            data["Created By"].append(order.created_by.username)
            data["Created At"].append(order.created_at)
            data["Updated At"].append(order.updated_at)
            data["Is Completed"].append(order.is_completed)
            data["Comments"].append(order.comments)
            data["Last Printed Comments"].append(order.last_printed_comments)
            data["Table Number"].append(order.table_number)
            data["Total Price"].append(order.total_price)
            data["Status"].append(order.status)
            data["Payment Method"].append(order.payment_method)
            data["Total Sum"].append(order.total_sum())

        # Преобразуем словарь в DataFrame
        df = pd.DataFrame(data)

        # Убираем информацию о часовом поясе из столбцов с датами/временем
        df['Created At'] = df['Created At'].dt.tz_localize(None)
        df['Updated At'] = df['Updated At'].dt.tz_localize(None)

        # Сохраняем DataFrame в файл Excel
        df.to_excel('orders_data.xlsx', index=False, engine='openpyxl')
