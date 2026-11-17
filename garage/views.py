from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (TemplateView, ListView, CreateView, UpdateView,
                                  DeleteView, DetailView)

from .forms import (CustomerForm, MechanicForm, ServiceForm, JobCardForm,
                    JobCardItemFormSet, BillForm, PaymentForm)
from .models import Customer, Mechanic, Service, JobCard, Bill, Payment


class IndexView(TemplateView):
    template_name = 'garage/index.html'


class HomeView(TemplateView):
    template_name = 'garage/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['services'] = Service.objects.all()
        return ctx


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'garage/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        bills = list(Bill.objects.select_related('jobcard'))
        total = JobCard.objects.count() or 1
        stats = []
        for key, label in JobCard.STATUS:
            n = JobCard.objects.filter(status=key).count()
            stats.append({'key': key, 'label': label, 'n': n, 'pct': round(n * 100 / total)})
        ctx.update(
            status_stats=stats,
            recent_payments=Payment.objects.select_related('bill')[:5],
            customers=Customer.objects.count(),
            mechanics=Mechanic.objects.filter(is_active=True).count(),
            open_jobs=JobCard.objects.filter(status__in=['pending', 'in_progress']).count(),
            unpaid_bills=sum(1 for b in bills if b.status != 'Paid'),
            revenue=Payment.objects.aggregate(t=Sum('amount'))['t'] or Decimal('0'),
            recent_jobs=JobCard.objects.select_related('customer', 'mechanic')[:5],
        )
        return ctx


def make_crud(model, form_class, prefix, title, columns):
    """Build list / create / update / delete views for one model."""
    ctx = {'prefix': prefix, 'title': title, 'columns': columns}

    class Ctx:
        def get_context_data(self, **kw):
            c = super().get_context_data(**kw)
            c.update(ctx)
            return c

    class List(LoginRequiredMixin, Ctx, ListView):
        template_name = 'garage/object_list.html'
        paginate_by = 15

        def get_queryset(self):
            qs = model.objects.all()
            q = self.request.GET.get('q')
            if q:
                from django.db.models import Q
                text_fields = [f.name for f in model._meta.fields
                               if f.get_internal_type() in ('CharField', 'TextField')]
                cond = Q()
                for f in text_fields:
                    cond |= Q(**{f'{f}__icontains': q})
                qs = qs.filter(cond)
            status = self.request.GET.get('status')
            if status and any(f.name == 'status' for f in model._meta.fields):
                qs = qs.filter(status=status)
            return qs

        def get_context_data(self, **kw):
            from urllib.parse import urlencode
            c = super().get_context_data(**kw)
            f = [x for x in model._meta.fields if x.name == 'status' and x.choices]
            c['status_choices'] = f[0].choices if f else None
            c['active_status'] = self.request.GET.get('status', '')
            c['qs'] = urlencode({k: v for k, v in self.request.GET.items() if k != 'page'})
            return c

    class Create(LoginRequiredMixin, Ctx, CreateView):
        template_name = 'garage/object_form.html'
        form_class_ = form_class
        success_url = reverse_lazy(f'{prefix}_list')

        def get_form_class(self):
            return form_class

        def get_initial(self):
            return self.request.GET.dict()

        def form_valid(self, form):
            messages.success(self.request, f'{title[:-1] if title.endswith("s") else title} saved.')
            return super().form_valid(form)

    class Update(LoginRequiredMixin, Ctx, UpdateView):
        template_name = 'garage/object_form.html'
        success_url = reverse_lazy(f'{prefix}_list')

        def get_form_class(self):
            return form_class

        def form_valid(self, form):
            messages.success(self.request, 'Changes saved.')
            return super().form_valid(form)

    class Delete(LoginRequiredMixin, Ctx, DeleteView):
        template_name = 'garage/object_confirm_delete.html'
        success_url = reverse_lazy(f'{prefix}_list')

        def post(self, request, *args, **kwargs):
            from django.db.models import ProtectedError
            try:
                return super().post(request, *args, **kwargs)
            except ProtectedError:
                messages.error(request, 'Cannot delete: other records depend on this one.')
                return redirect(f'{prefix}_list')

    for cls in (List, Create, Update, Delete):
        cls.model = model
    return List, Create, Update, Delete


CRUD = {
    'customer': make_crud(Customer, CustomerForm, 'customer', 'Customers',
                          [('Name', 'name'), ('Email', 'email'), ('Phone', 'phone'),
                           ('Address', 'address')]),
    'mechanic': make_crud(Mechanic, MechanicForm, 'mechanic', 'Mechanics',
                          [('Name', 'name'), ('Speciality', 'speciality'), ('Phone', 'phone'),
                           ('Active', 'is_active')]),
    'service': make_crud(Service, ServiceForm, 'service', 'Services',
                         [('Service', 'name'), ('Price', 'price'),
                          ('Duration (hrs)', 'duration_hours')]),
    'bill': make_crud(Bill, BillForm, 'bill', 'Customer bills',
                      [('Bill', '__str__'), ('Customer', 'customer'), ('Total', 'total_bill'),
                       ('Discount', 'discount'), ('Net cost', 'net_cost'),
                       ('Paid', 'amount_paid'), ('Balance', 'balance'), ('Status', 'status')]),
    'payment': make_crud(Payment, PaymentForm, 'payment', 'Payments',
                         [('Receipt', 'receipt_no'), ('Bill', 'bill'), ('Amount', 'amount'),
                          ('Method', 'method'), ('Date', 'paid_on')]),
}

JobCardList, _jc_c, _jc_u, JobCardDelete = make_crud(
    JobCard, JobCardForm, 'jobcard', 'Job cards',
    [('Job card', '__str__'), ('Customer', 'customer'), ('Mechanic', 'mechanic'),
     ('Status', 'status'), ('Total', 'total_cost'), ('Opened', 'date_opened')])


class JobCardFormMixin(LoginRequiredMixin):
    model = JobCard
    form_class = JobCardForm
    template_name = 'garage/jobcard_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['formset'] = JobCardItemFormSet(self.request.POST, instance=self.object)
        else:
            ctx['formset'] = JobCardItemFormSet(instance=self.object)
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        formset = ctx['formset']
        if not formset.is_valid():
            return self.render_to_response(ctx)
        with transaction.atomic():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
        messages.success(self.request, 'Job card saved.')
        return redirect('jobcard_detail', pk=self.object.pk)


class JobCardCreate(JobCardFormMixin, CreateView):
    pass


class JobCardUpdate(JobCardFormMixin, UpdateView):
    pass


class JobCardDetail(LoginRequiredMixin, DetailView):
    model = JobCard
    template_name = 'garage/jobcard_detail.html'


class BillDetail(LoginRequiredMixin, DetailView):
    model = Bill
    template_name = 'garage/bill_detail.html'
