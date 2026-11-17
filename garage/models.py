from decimal import Decimal

from django.db import models
from django.db.models import Sum


class Customer(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30)
    address = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Mechanic(models.Model):
    name = models.CharField(max_length=120)
    speciality = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    duration_hours = models.DecimalField(max_digits=5, decimal_places=1, default=1)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.price})'


class JobCard(models.Model):
    STATUS = [
        ('pending', 'Pending'),
        ('in_progress', 'In progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='jobcards')
    mechanic = models.ForeignKey(Mechanic, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='jobcards')
    vehicle_reg = models.CharField('Vehicle plate', max_length=20)
    vehicle_model = models.CharField(max_length=80, blank=True)
    problem = models.TextField()
    recommendation = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS, default='pending')
    date_opened = models.DateField(auto_now_add=True)
    date_closed = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-date_opened', '-id']

    def __str__(self):
        return f'JC-{self.pk:05d} {self.vehicle_reg}'

    @property
    def total_cost(self):
        return sum((i.line_total for i in self.items.all()), Decimal('0'))


class JobCardItem(models.Model):
    jobcard = models.ForeignKey(JobCard, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
                                     help_text='Leave blank to use the service price.')

    def save(self, *args, **kwargs):
        if self.unit_price is None:
            self.unit_price = self.service.price
        super().save(*args, **kwargs)

    @property
    def line_total(self):
        return (self.unit_price or Decimal('0')) * self.quantity

    def __str__(self):
        return f'{self.service.name} x{self.quantity}'


class Bill(models.Model):
    jobcard = models.OneToOneField(JobCard, on_delete=models.PROTECT, related_name='bill')
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    issued_on = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-issued_on', '-id']

    def __str__(self):
        return f'BILL-{self.pk:05d}'

    @property
    def customer(self):
        return self.jobcard.customer

    @property
    def total_bill(self):
        return self.jobcard.total_cost

    @property
    def net_cost(self):
        return max(self.total_bill - self.discount, Decimal('0'))

    @property
    def amount_paid(self):
        return self.payments.aggregate(t=Sum('amount'))['t'] or Decimal('0')

    @property
    def balance(self):
        return self.net_cost - self.amount_paid

    @property
    def status(self):
        if self.net_cost > 0 and self.amount_paid >= self.net_cost:
            return 'Paid'
        if self.amount_paid > 0:
            return 'Partial'
        return 'Unpaid'


class Payment(models.Model):
    METHODS = [('cash', 'Cash'), ('mobile_money', 'Mobile money'), ('card', 'Card'),
               ('bank', 'Bank transfer')]
    bill = models.ForeignKey(Bill, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=15, choices=METHODS, default='cash')
    paid_on = models.DateField(auto_now_add=True)
    receipt_no = models.CharField(max_length=20, blank=True, editable=False)

    class Meta:
        ordering = ['-paid_on', '-id']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.receipt_no:
            self.receipt_no = f'RCT-{self.pk:06d}'
            super().save(update_fields=['receipt_no'])

    def __str__(self):
        return self.receipt_no or 'Payment'
