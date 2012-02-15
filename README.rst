# This fork is a "hasty" fix to include browsing of uploaded files.

# It also includes a fix for IE/FF issues where the "kama" theme is misaligned in the django admin.

Django CKEditor
================
**Django admin CKEditor integration.**

Provides a ``RichTextField`` and ``CKEditorWidget`` utilizing CKEditor with image upload and browsing support included.

.. contents:: Contents
    :depth: 5

Installation
------------

* File icon source: http://www.abeautifulsite.net/blog/2008/03/jquery-file-tree/


#. Install or add django-ckeditor to your python path.

#. Add ``ckeditor`` to your INSTALLED_APPS setting.

#. In your project's settings.py, add the following attributes:
    * CKEDITOR_STATIC_URL -  Specifies a URL prefix to the ckeditor JS and CSS media (not uploaded media). Make sure to use a trailing slash
        * CKEDITOR_STATIC_URL = "media.myprojectsite.com/media/ckeditor/"
    
    * CKEDITOR_UPLOAD_PATH - Specifies an absolute path to your ckeditor media upload directory. Make sure you have write permissions for the path, i.e.::
        * CKEDITOR_UPLOAD_PATH = "/home/media/media.myprojectsite.com/ckeditor/uploads"
    
    * CKEDITOR_UPLOADED_MEDIA_PREFIX - specifies a URL prefix to media uploaded through ckeditor
        * e.g. CKEDITOR_UPLOADED_MEDIA_PREFIX = "http://media.myprojectsite.com/media/ckeditor/uploads'
        * (If CKEDITOR_UPLOADED_MEDIA_PREFIX is not provided, the media URL will fall back to MEDIA_URL with the difference of MEDIA_ROOT and the uploaded resource's full path and filename appended.)

#. In your project's urls.py, add the following:
    
    (r'^ckeditor/', include('ckeditor.urls')),    

#. Optionally, add CKEDITOR_CONFIGS setting to the project's ``settings.py`` file. This specifies sets of CKEditor settings that are passed to CKEditor (see CKEditor's `Setting Configurations <http://docs.cksource.com/CKEditor_3.x/Developers_Guide/Setting_Configurations>`_), i.e.::

       CKEDITOR_CONFIGS = {
           'awesome_ckeditor': {
               'toolbar': 'Basic',
           },
       }
   
   The name of the settings can be referenced when instantiating a RichTextField::

       content = RichTextField(config_name='awesome_ckeditor')

   The name of the settings can be referenced when instantiating a CKEditorWidget::

       widget = CKEditorWidget(config_name='awesome_ckeditor')
   
   By specifying a set named ``default`` you'll be applying its settings to all RichTextField and CKEditorWidget objects for which ``config_name`` has not been explicitly defined ::
       
       CKEDITOR_CONFIGS = {
           'default': {
               'toolbar': 'Full',
               'height': 300,
               'width': 300,
           },
       }

Usage
-----

Field
~~~~~
The quickest way to add rich text editing capabilities to your models is to use the included ``RichTextField`` model field type. A CKEditor widget is rendered as the form field but in all other regards the field behaves as the standard Django ``TextField``. For example::

    from django.db import models
    from ckeditor.fields import RichTextField

    class Post(models.Model):
        content = RichTextField()


Widget
~~~~~~
Alernatively you can use the included ``CKEditorWidget`` as the widget for a formfield. For example::

    from django import forms
    from django.contrib import admin
    from ckeditor.widgets import CKEditorWidget

    from post.models import Post

    class PostAdminForm(forms.ModelForm):
        content = forms.CharField(widget=CKEditorWidget())
        class Meta:
            model = Post

    class PostAdmin(admin.ModelAdmin):
        form = PostAdminForm
    
    admin.site.register(Post, PostAdmin)

**NOTE**: If you're using custom views remember to include ckeditor.js in your form's media either through ``{{ form.media }}`` or through a ``<script>`` tag. Admin will do this for you automatically. See `Django's Form Media docs <http://docs.djangoproject.com/en/dev/topics/forms/media/>`_ for more info.
