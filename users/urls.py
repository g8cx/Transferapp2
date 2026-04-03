from django.urls import path
from . import views

urlpatterns = [
    path('', views.register, name='register'),
    path('auth/', views.auth_page, name='auth'),
    path('login-existing/', views.existing_users_login, name='login_existing'),
    path('home/', views.home, name='home'),
    path('waybills/', views.waybill_list, name='waybill_list'),
    path('waybills/export/', views.export_waybills_csv, name='export_waybills_csv'),
    path('waybills/<int:waybill_id>/export/', views.export_waybill_csv, name='export_waybill_csv'),
    path('register/', views.register),
]
