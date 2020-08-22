from django.urls import path, include
from django.conf import settings
from django.shortcuts import redirect
from django.conf.urls.static import static
from . import views
urlpatterns = [
    path('main-dashboard', views.main_dashboard, name='main_dashboard'),
    path('vol-dashboard', views.vol_dashboard, name='vol_dashboard'),
    path('donor-dashboard', views.donor_dashboard, name='donor_dashboard'),
    path('child-dashboard', views.child_dashboard, name='child_dashboard'),
    path('rec-dashboard', views.rec_dashboard, name='rec_dashboard'),
    path('mailchimp', views.mailchimp, name='mailchimp'),
    path('session_gallery', views.session_gallery, name='session_gallery'),
    path('project_gallery', views.project_gallery, name='project_gallery'),
    path('kid_gallery', views.kid_gallery, name='kid_gallery'),
    path('donor_gallery', views.donor_gallery, name='donor_gallery'),
    path('accounts/signin', views.signin, name='signin'),
    path('accounts/signout', views.signout, name='signout'),
    path('accounts/profile', views.profile, name='profile'),
    path('accounts/calender', views.calender, name='calender'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)