from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import datetime, time, timedelta
from django.utils.html import format_html

from .models import DeliveryCustomer


class DeliveryForm(forms.Form):
    delivery_phone_number = forms.CharField(label='Номер телефона', validators=[RegexValidator(regex=r'^\d{10}$', message='Номер телефона должен содержать ровно 10 цифр')])

class DeliveryCustomerForm(forms.ModelForm):
    city = forms.ChoiceField(choices=[('חיפה', 'Хайфа'), ('נשר', ('Нэшер')), ('טירת כרמל', 'Тира'), ('כפר גלים', 'Кфар Галим'),('קריית חיים', 'Кирият Хаим'), ('קריית אתא', 'Кирият Ата'), ('קריית ביאליק', 'Кирият Биалик'), ('קריית מוצקין', 'Кирият Моцкин'), ('קריית ים', ('Кирият Ям'))], widget=forms.Select(attrs={'class': 'form-control', 'required': True}))

    class Meta:
        model = DeliveryCustomer
        fields = ['delivery_phone_number', 'name', 'city', 'street', 'house_number', 'floor', 'apartment_number', 'intercom_code']
        widgets = {
            'delivery_phone_number': forms.TextInput(attrs={'readonly': 'readonly'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'street': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'house_number': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'floor': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'apartment_number': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'intercom_code': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProductQuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=10000, initial=1, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'style': 'width: 100px; display: inline-block;'
    }))


def generate_time_intervals(start_time, end_time, delta_minutes):
    current_time = datetime.combine(datetime.today(), start_time)
    end_datetime = datetime.combine(datetime.today(), end_time)
    time_intervals = []

    while current_time <= end_datetime:
        time_intervals.append(current_time.strftime('%H:%M'))
        current_time += timedelta(minutes=delta_minutes)

    return time_intervals

class DeliveryDateTimeForm(forms.Form):
    form_type = forms.CharField(widget=forms.HiddenInput(), initial='delivery_date_time')
    start_time = time(12, 0)
    end_time = time(22, 0)
    delta_minutes = 15

    date = forms.DateField(label='Дата', widget=forms.DateInput(attrs={'type': 'date'}))
    time_choices = generate_time_intervals(start_time, end_time, delta_minutes)
    time = forms.ChoiceField(label='Время', choices=[(time, time) for time in time_choices])

class SelectOrderForm(forms.Form):
    form_type = forms.CharField(widget=forms.HiddenInput(), initial='select_order')
    order = forms.ModelChoiceField(
        queryset=None,  # Queryset будет передан позже
        label="Выберите заказ",
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        orders = kwargs.pop('orders', None)
        super().__init__(*args, **kwargs)

        self.fields['order'].queryset = orders
        # Изменение отображения каждого заказа в списке
        self.fields['order'].label_from_instance = self._order_label

    def _order_label(self, order):
        # Форматирование метки для каждого заказа в списке
        return format_html(
            "{} - {} - {} - {}, {}",
            order.delivery_date.strftime('%Y-%m-%d'),
            order.customer.name,
            order.customer.delivery_phone_number,
            order.customer.street,
            order.customer.house_number
        )