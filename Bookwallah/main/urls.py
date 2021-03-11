from django.urls import path, include
from django.conf import settings
from django.shortcuts import redirect
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('',views.landing, name='landing'),
    path('dashboard/main', views.main_dashboard, name='main_dashboard'),
    path('dashboard/volunteer', views.vol_dashboard, name='vol_dashboard'),
    path('dashboard/donor', views.donor_dashboard, name='donor_dashboard'),
    path('dashboard/project', views.proj_dashboard, name='proj_dashboard'),
    path('dashboard/kid', views.child_dashboard, name='child_dashboard'),
    path('dashboard/recruitment', views.rec_dashboard, name='rec_dashboard'),
   # path('mailchimp', views.mailchimp, name='mailchimp'),
    path('location/project', views.p_location, name='p_location'),
    path('location/donor', views.d_location, name='d_location'),
    path('session_gallery', views.session_gallery, name='session_gallery'),
    path('project_gallery', views.project_gallery, name='project_gallery'),
    path('kid_gallery', views.kid_gallery, name='kid_gallery'),
    path('donor_gallery', views.donor_gallery, name='donor_gallery'),
    path('accounts/signin', views.signin, name='signin'),
    path('accounts/signout', views.signout, name='signout'),
    path('accounts/profile', views.profile, name='profile'),
    path('accounts/calender', views.calender, name='calender'),
path('password-reset/',
     auth_views.PasswordResetView.as_view(
             template_name='profile/password-reset/password_reset_form.html',
             subject_template_name='profile/password-reset/password_reset_subject.txt',
             email_template_name='profile/password-reset/password_reset_email.html',
             # success_url='/login/'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='profile/password-reset/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='profile/password-reset/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='profile/password-reset/password_reset_complete.html'
         ),
         name='password_reset_complete')
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)