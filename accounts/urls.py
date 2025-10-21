from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ---------------- Landing and Authentication ----------------
    path('', views.landing_view, name='landing'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('request-otp/', views.request_otp_view, name='request_otp'),
    
    # ---------------- Dashboard Routes ----------------
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('doctor-dashboard/', views.doctor_dashboard_view, name='doctor_dashboard'),
    path('management-dashboard/', views.management_dashboard_view, name='management_dashboard'),
    
    # ---------------- Admin Management Routes ----------------
    path('admin/manage-doctors/', views.manage_doctors_view, name='manage_doctors'),
    path('admin/manage-management/', views.manage_management_view, name='manage_management'),
    path('admin/remove-user/<int:user_id>/', views.remove_user_view, name='remove_user'),
    
    # ---------------- File and Patient Management ----------------
    path('access-file/<int:file_id>/', views.access_patient_file_view, name='access_patient_file'),  # Changed name
    path('access-patient-pdf/<int:patient_id>/', views.access_patient_pdf_view, name='access_patient_pdf'),
]