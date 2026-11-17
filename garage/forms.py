from django import forms
from django.forms import inlineformset_factory

from .models import Customer, Mechanic, Service, JobCard, JobCardItem, Bill, Payment


class StyledMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            w = f.widget
            if isinstance(w, forms.CheckboxInput):
                w.attrs['class'] = 'check'
            else:
                w.attrs['class'] = 'control'


class CustomerForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address']


class MechanicForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Mechanic
        fields = ['name', 'speciality', 'phone', 'email', 'is_active']


class ServiceForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'duration_hours']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}


class JobCardForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = JobCard
        fields = ['customer', 'mechanic', 'vehicle_reg', 'vehicle_model', 'problem',
                  'recommendation', 'status', 'date_closed']
        widgets = {
            'problem': forms.Textarea(attrs={'rows': 3}),
            'recommendation': forms.Textarea(attrs={'rows': 3}),
            'date_closed': forms.DateInput(attrs={'type': 'date'}),
        }


class JobCardItemForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = JobCardItem
        fields = ['service', 'quantity', 'unit_price']


JobCardItemFormSet = inlineformset_factory(
    JobCard, JobCardItem, form=JobCardItemForm, extra=2, can_delete=True)


class BillForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['jobcard', 'discount']


class PaymentForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['bill', 'amount', 'method']

    def clean(self):
        data = super().clean()
        bill, amount = data.get('bill'), data.get('amount')
        if bill and amount is not None:
            if amount <= 0:
                self.add_error('amount', 'Amount must be greater than zero.')
            elif amount > bill.balance:
                self.add_error('amount', f'Amount exceeds the outstanding balance ({bill.balance}).')
        return data
