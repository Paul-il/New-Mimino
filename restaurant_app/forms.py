from django import forms
from django.forms import CheckboxSelectMultiple
from .models.tables import Booking
from .models.orders import Order, OrderItem, Product
from datetime import time, timedelta, datetime
from django.utils import timezone  # Убедимся, что timezone импортирован

def generate_time_intervals(start_time, end_time, delta_minutes):
    # Преобразование объектов datetime.time в datetime.datetime для выполнения арифметических операций
    current_datetime = timezone.combine(timezone.now().date(), start_time)  # Изменили здесь
    end_datetime = timezone.combine(timezone.now().date(), end_time)  # Изменили здесь
    time_intervals = []

    while current_datetime.time() <= end_datetime.time():
        time_intervals.append((current_datetime.strftime('%H:%M'), current_datetime.strftime('%H:%M')))
        current_datetime += timedelta(minutes=delta_minutes)

    return time_intervals

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
    class Meta:
        model = Booking
        exclude = ['are_guests_here', 'is_deleted', 'created_at', 'guests_did_not_arrive']
        widgets = {
            'reserved_date': forms.TextInput(attrs={'type': 'date'}),
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
        self.fields['table'].widget.attrs['disabled'] = True
        self.fields['table'].widget.attrs['style'] = 'display:none'
        self.fields['table'].label = ''
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['user'].initial = self.request.user
        self.fields['description'].widget.attrs['rows'] = 3


        if self.table:
            self.fields['table'].widget = forms.HiddenInput()
            self.fields['table'].initial = self.table
            
    def clean(self):
        cleaned_data = super().clean()
        table = cleaned_data.get('table')
        reserved_date = cleaned_data.get('reserved_date')
        reserved_time = cleaned_data.get('reserved_time')

        num_of_people = cleaned_data.get('num_of_people')
        description = cleaned_data.get('description')

        if num_of_people and num_of_people > 10 and not description:
            raise forms.ValidationError('Поле "Комментарий" обязательно для заполнения, если количество гостей больше 10.')

        # Check if the selected table is already booked at the selected date and time
        if Booking.objects.filter(table=table, reserved_date=reserved_date, reserved_time=reserved_time, is_deleted=False).exists():
            raise forms.ValidationError('Этот стол уже занят в выбранное время, пожалуйста, выберите другое время или стол.')

        # Check if the user has already made a booking at the selected date and time
        if Booking.objects.filter(user=self.request.user, reserved_date=reserved_date, reserved_time=reserved_time, is_deleted=False).exists():
            raise forms.ValidationError('Вы уже забронировали стол на выбранное время, пожалуйста, выберите другое время.')
        
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
        (1, 'Один день'),
        (7, 'Семь дней'),
        (14, '14 дней'),
        (21, '21 день'),
        (30, 'Месяц'),
    ]
    date_range = forms.ChoiceField(choices=DATERANGE_CHOICES, required=False)
