from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    '',
    url(r'^upload/', 'ckeditor.views.upload', name='ckeditor_upload'),
    url(r'^browse/', 'ckeditor.views.browse', name='ckeditor_browse'),
    url(r'^browse_ajax/', 'ckeditor.views.browse_ajax', name='ckeditor_browse_ajax'),
)
