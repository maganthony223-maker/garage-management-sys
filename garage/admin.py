from django.contrib import admin
from .models import Customer, Mechanic, Service, JobCard, JobCardItem, Bill, Payment


class JobCardItemInline(admin.TabularInline):
    model = JobCardItem
    extra = 1


@admin.register(JobCard)
class JobCardAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'customer', 'mechanic', 'status', 'date_opened')
    list_filter = ('status',)
    inlines = [JobCardItemInline]


admin.site.register([Customer, Mechanic, Service, Bill, Payment])
