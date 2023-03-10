from django import forms
from django.forms import CheckboxSelectMultiple
from .models.tables import Table, Booking
from .models.orders import Order, OrderItem


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        exclude = ['are_guests_here', 'is_deleted', 'created_at']
        widgets = {
            'reserved_date': forms.TextInput(attrs={'type': 'date'}),
            'reserved_time': forms.TextInput(attrs={'type': 'time'}),
        }
        labels = {
            'Table': 'Стол',
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
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['user'].initial = self.request.user

        if self.table:
            self.fields['table'].widget = forms.HiddenInput()
            self.fields['table'].initial = self.table

    table = forms.ModelChoiceField(
        queryset=Table.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        table = cleaned_data.get('table')
        reserved_date = cleaned_data.get('reserved_date')
        reserved_time = cleaned_data.get('reserved_time')

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

