from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView

from home.views import home

from search.views import search

from contact.views import contact, contact_success

urlpatterns = [
    url(r'^$', home, name='home'),

    url(r'^admin/', admin.site.urls),

    url(r'^search/$', search, name='search'),

    url(r'', include('products.urls')),

    url(r'^contact/$', contact, name='contact'),
    url(r'^contact/success/$', contact_success, name='contact_success'),

    url(r'^about/$', TemplateView.as_view(template_name="about.html")),
    url(r'^terms/$', TemplateView.as_view(template_name="terms.html")),
    url(r'^privacy/$', TemplateView.as_view(template_name="privacy.html")),
    url(r'^disclosure/$', TemplateView.as_view(template_name="disclosure.html")),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
