from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    path('jobcards/', views.JobCardList.as_view(), name='jobcard_list'),
    path('jobcards/new/', views.JobCardCreate.as_view(), name='jobcard_create'),
    path('jobcards/<int:pk>/', views.JobCardDetail.as_view(), name='jobcard_detail'),
    path('jobcards/<int:pk>/edit/', views.JobCardUpdate.as_view(), name='jobcard_update'),
    path('jobcards/<int:pk>/delete/', views.JobCardDelete.as_view(), name='jobcard_delete'),
    path('bills/<int:pk>/', views.BillDetail.as_view(), name='bill_detail'),
]

for prefix, (L, C, U, D) in views.CRUD.items():
    plural = prefix + 's'
    urlpatterns += [
        path(f'{plural}/', L.as_view(), name=f'{prefix}_list'),
        path(f'{plural}/new/', C.as_view(), name=f'{prefix}_create'),
        path(f'{plural}/<int:pk>/edit/', U.as_view(), name=f'{prefix}_update'),
        path(f'{plural}/<int:pk>/delete/', D.as_view(), name=f'{prefix}_delete'),
    ]
