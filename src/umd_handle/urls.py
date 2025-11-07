"""
URL configuration for umd_handle project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from djangosaml2 import views as saml_views

urlpatterns = [
    path("api/", include("umd_handle.api.urls")),
    path('admin/', admin.site.urls),
    path('saml2/', include('djangosaml2.urls')),

    # Following path is necessary because "users/auth/saml/callback" was the
    # path in the "AssertionConsumerService" tag provided in the service
    # provider XML configuration sent to DIT for the Rails "umd-handle"
    # application, and CAS requires an exact match.
    path('users/auth/saml/callback', saml_views.AssertionConsumerServiceView.as_view(), name='saml2_acs'),
]
