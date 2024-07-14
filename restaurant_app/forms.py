from django import forms
from django.forms import CheckboxSelectMultiple
from .models.tables import Booking, Table
from .models.orders import Order, OrderItem, Product
from datetime import time, timedelta, datetime
from django.utils import timezone  # Убедимся, что timezone импортирован
from django.core.exceptions import ValidationError
from .models.product import ProductStock
from .models.message import Message

class CombinedFilterForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    day_of_week = forms.ChoiceField(
        choices=[
            ('', 'Все дни недели'),
            ('1', 'Понедельник'),
            ('2', 'Вторник'),
            ('3', 'Среда'),
            ('4', 'Четверг'),
            ('5', 'Пятница'),
            ('6', 'Суббота'),
            ('7', 'Воскресенье')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    category = forms.ChoiceField(
        choices=[('', 'Все категории')] + list(Product.CATEGORY_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class CategoryFilterForm(forms.Form):
    category = forms.ChoiceField(
        choices=[('', 'Все категории')] + list(Product.CATEGORY_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class CategorySelectForm(forms.Form):
    category = forms.ChoiceField(
        choices=[('', 'Выберите категорию')] + Product.CATEGORY_CHOICES,
        required=False,
        label='Категория'
    )

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control'}),
        }
        labels = {
            'body': 'Сообщение',
        }

        
class ProductStockForm(forms.ModelForm):
    class Meta:
        model = ProductStock
        fields = ['product', 'received_quantity']

class PasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())


def generate_time_intervals(start_time, end_time, delta_minutes):
    # Преобразование объектов datetime.time в datetime.datetime для выполнения арифметических операций
    current_datetime = datetime.combine(datetime.today(), start_time)
    end_datetime = datetime.combine(datetime.today(), end_time)
    time_intervals = []

    while current_datetime.time() <= end_datetime.time():
        time_intervals.append((current_datetime.strftime('%H:%M'), current_datetime.strftime('%H:%M')))
        current_datetime += timedelta(minutes=delta_minutes)

    return time_intervals

start_time = time(11, 0)
end_time = time(23, 0)
delta_minutes = 15
TIME_CHOICES = generate_time_intervals(start_time, end_time, delta_minutes)


class BookingForm(forms.ModelForm):
    reserved_time = forms.ChoiceField(choices=TIME_CHOICES, label='Время')

    # Добавление выпадающего списка для количества гостей
    NUM_OF_PEOPLE_CHOICES = [(i, str(i)) for i in range(1, 60)]  # Например, от 1 до 20 гостей
    num_of_people = forms.ChoiceField(choices=NUM_OF_PEOPLE_CHOICES, label='Количество гостей')

    class Meta:
        model = Booking
        fields = ['reserved_date', 'reserved_time', 'num_of_people', 'description']
        widgets = {
            'reserved_date': forms.TextInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'reserved_date': 'Дата',
            'reserved_time': 'Время',
            'num_of_people': 'Количество гостей',
            'description': 'Комментарий',
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.table = kwargs.pop('table', None)
        super().__init__(*args, **kwargs)
        
        # Проверка и настройка поля table
        if 'table' in self.fields:
            if self.table:
                self.fields['table'].initial = self.table
                self.fields['table'].widget = forms.HiddenInput()
            else:
                self.fields['table'].widget = forms.HiddenInput()

        # Проверка и настройка поля user
        if 'user' in self.fields:
            self.fields['user'].widget = forms.HiddenInput()
            if self.request:
                self.fields['user'].initial = self.request.user


    def clean(self):
        cleaned_data = super().clean()
        table_id = cleaned_data.get('table')  # Получаем ID стола
        num_of_people = int(cleaned_data.get('num_of_people'))  # Преобразование в число
        reserved_date = cleaned_data.get('reserved_date')
        reserved_time_str = cleaned_data.get('reserved_time')

        try:
            reserved_time = datetime.strptime(reserved_time_str, "%H:%M").time()
        except ValueError:
            raise forms.ValidationError('Неверный формат времени.')

        # Получение даты и времени бронирования
        reserved_datetime = datetime.combine(reserved_date, reserved_time)

        # Проверка статуса последнего заказа для выбранного стола
        last_order = Order.objects.filter(table_id=table_id).order_by('-created_at').first()

        if last_order and not last_order.is_completed:
            # Проверка на количество человек и соответствующее ограничение времени
            if num_of_people <= 3:
                one_hour_later = timezone.now() + timedelta(hours=1)
                if reserved_time < one_hour_later.time():
                    raise forms.ValidationError('Для бронирования столика на группу до трех человек доступно только время через час после текущего.')
            
            elif 3 < num_of_people <= 6:
                two_hours_later = timezone.now() + timedelta(hours=2)
                if reserved_time < two_hours_later.time():
                    raise forms.ValidationError('Для бронирования столика на группу от трех до шести человек доступно только время через два часа после текущего.')

        if num_of_people > 10 and not cleaned_data.get('description'):
            raise forms.ValidationError('Поле "Комментарий" обязательно для заполнения, если количество гостей больше 10.')

        # Получение всех бронирований для выбранного стола на эту дату
        existing_bookings = Booking.objects.filter(table_id=table_id, reserved_date=reserved_date)

        # Проверка, что новое время бронирования не пересекается с существующими
        for booking in existing_bookings:
            booking_start = datetime.combine(booking.reserved_date, booking.reserved_time)
            booking_end = booking_start + timedelta(hours=1)  # Предполагаем, что бронь длится один час

            # Создаем диапазон времени, когда столик не доступен
            unavailable_start = booking_start - timedelta(hours=1)
            unavailable_end = booking_end + timedelta(hours=1)

            # Проверяем, попадает ли запрашиваемое время в недоступный диапазон
            if unavailable_start <= reserved_datetime <= unavailable_end:
                raise forms.ValidationError('Этот столик недоступен для бронирования за час до и после существующего бронирования.')

        # Поиск доступных столов на указанную дату и время
        available_tables = Table.objects.filter(
            capacity__gte=num_of_people,
            is_booked=False
        ).exclude(
            bookings__reserved_date=reserved_date,
            bookings__reserved_time=reserved_time,
            bookings__is_deleted=False
        )

        if not available_tables:
            raise ValidationError('Нет доступных столов на выбранное время и дату для указанного количества гостей.')

        # Выбор первого доступного стола
        cleaned_data['table'] = available_tables.first()

        return cleaned_data

class GuestsHereForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['are_guests_here']
        widgets = {'are_guests_here': forms.HiddenInput()}


class OrderForm(forms.ModelForm):
    PAYMENT_CHOICES = (
        ('cash', 'Наличные'),
        ('card', 'Кредитная карта'),
    )

    payment_method = forms.MultipleChoiceField(widget=CheckboxSelectMultiple, choices=PAYMENT_CHOICES)

    class Meta:
        model = Order
        fields = ['payment_method']

    
class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

class ProductQuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=10000, initial=1, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'style': 'width: 100px; display: inline-block;'
    }))

class ProductForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all())

class DateRangeForm(forms.Form):
    DATERANGE_CHOICES = [
        ('1', 'Последний день'),
        ('7', 'Последние 7 дней'),
        ('30', 'Последний месяц'),
        ('365', 'Последний год'),
        # Добавьте другие опции по вашему выбору
    ]
    date_range = forms.ChoiceField(choices=DATERANGE_CHOICES, required=False, label="Выберите диапазон")
    DAY_OF_WEEK_CHOICES = [
        ('', 'Выбрать день недели'),
        ('1', 'Понедельник'),
        ('2', 'Вторник'),
        ('3', 'Среда'),
        ('4', 'Четверг'),
        ('5', 'Пятница'),
        ('6', 'Суббота'),
        ('7', 'Воскресенье'),
    ]
    day_of_week = forms.ChoiceField(choices=DAY_OF_WEEK_CHOICES, required=False, label="День недели")

