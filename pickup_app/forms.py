from django import forms

from .models import PickupOrder
from restaurant_app.models.orders import OrderItem

class PickupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PickupForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = False
        self.fields['phone'].widget.attrs['style'] = 'width: 300px;'
        self.fields['name'].widget.attrs['style'] = 'width: 300px;'

    class Meta:
        model = PickupOrder
        fields = ['phone', 'name']
        labels = {
            'phone': 'Номер телефона',
            'name': 'Имя',
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'phone_number']


class ProductQuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=10000, initial=1, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'style': 'width: 100px; display: inline-block;'
    }))

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поиск'}))