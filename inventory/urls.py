from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("vehicles/", views.vehicle_list, name="vehicle_list"),
    path("vehicles/add/", views.vehicle_create, name="vehicle_create"),
    path("vehicles/<int:pk>/", views.vehicle_detail, name="vehicle_detail"),
    path("vehicles/<int:pk>/edit/", views.vehicle_edit, name="vehicle_edit"),
    path("vehicles/<int:pk>/archive/", views.vehicle_archive, name="vehicle_archive"),
    path("vehicles/<int:pk>/sell/", views.vehicle_sell, name="vehicle_sell"),
    path("vehicles/<int:pk>/expense/", views.expense_add, name="expense_add"),
]
