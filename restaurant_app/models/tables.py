from django.db import models
from django.contrib.auth.models import User
from django import forms


class Room(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class Table(models.Model):
    table_id = models.IntegerField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='tables', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_booked = models.BooleanField(default=False)
    is_ordered = models.BooleanField(default=False)
    reserved_date = models.DateField(null=True, blank=True)
    reserved_time = models.TimeField(null=True, blank=True)
    num_of_people = models.IntegerField(null=True, blank=True)
    order_time = models.DateTimeField(null=True, blank=True)
    are_guests_here = models.BooleanField(default=False)
    capacity = models.IntegerField()
    active_order = models.BooleanField(default=False)

    def get_active_order(self):
        from .orders import Order  # Импортируем модель Order внутри метода, чтобы избежать цикличного импорта
        return Order.objects.filter(table=self, is_completed=False).last()

    def __str__(self):
        return f'Table {self.table_id}'

    def orders(self):
        from .orders import Order
        return Order.objects.filter(table=self)

    class Meta:
        ordering = ['table_id']


class Booking(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    reserved_date = models.DateField()
    reserved_time = models.TimeField()
    num_of_people = models.IntegerField()
    are_guests_here = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    guests_did_not_arrive = models.BooleanField(default=False)

    def __str__(self):
        return f"Бронирование {self.id} - стол {self.table.table_id} ({self.reserved_date} {self.reserved_time} {self.user.first_name})"
        
class GuestsHereForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['are_guests_here']
        widgets = {'are_guests_here': forms.HiddenInput()}

class Tip(models.Model):
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='tips', null=True, blank=True)  # Используйте правильный app_label

    def __str__(self):
        return f"Total tip: {self.amount} on {self.date}"


class TipDistribution(models.Model):
    tip = models.ForeignKey(Tip, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = (('tip', 'user'),)

    def __str__(self):
        return f"{self.user.username} gets {self.amount} from tip {self.tip.id}"

    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tips = models.FloatField(default=0)  # Или любое другое поле, которое вам нужно

class TipGoal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    goal = models.FloatField(default=0)
