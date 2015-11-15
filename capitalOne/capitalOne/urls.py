from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView
from capitalOne import views 
from django.contrib import admin


urlpatterns = patterns(
    "",
    url(r"^$", views.homepageview, name="home"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/signup/$", views.SignupView.as_view(), name="account_signup"),
    url(r"^account/", include("account.urls")),
    url(r"^get_vis_data/", views.get_vis_data, name="get_vis_data"),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
