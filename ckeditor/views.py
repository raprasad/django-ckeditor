import os
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils import simplejson

from directory_details import DirectoryDetails 

try: 
    from PIL import Image, ImageOps 
except ImportError: 
    import Image, ImageOps

try:
    from django.views.decorators.csrf import csrf_exempt
except ImportError:
    # monkey patch this with a dummy decorator which just returns the same function
    # (for compatability with pre-1.1 Djangos)
    def csrf_exempt(fn):
        return fn
        
THUMBNAIL_SIZE = (75, 75)
    
def get_available_name(name):
    """
    Returns a filename that's free on the target storage system, and
    available for new content to be written to.
    """
    dir_name, file_name = os.path.split(name)
    file_root, file_ext = os.path.splitext(file_name)
    # If the filename already exists, keep adding an underscore (before the
    # file extension, if one exists) to the filename until the generated
    # filename doesn't exist.
    while os.path.exists(name):
        file_root += '_'
        # file_ext includes the dot.
        name = os.path.join(dir_name, file_root + file_ext)
    return name

def get_thumb_filename(file_name):
    """
    Generate thumb filename by adding _thumb to end of filename before . (if present)
    """
    return '%s_thumb%s' % os.path.splitext(file_name)

def create_thumbnail(filename):
    image = Image.open(filename)
        
    # Convert to RGB if necessary
    # Thanks to Limodou on DjangoSnippets.org
    # http://www.djangosnippets.org/snippets/20/
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')
       
    # scale and crop to thumbnail
    imagefit = ImageOps.fit(image, THUMBNAIL_SIZE, Image.ANTIALIAS)
    imagefit.save(get_thumb_filename(filename))
        
def get_media_url(path):
    """
    Determine system file's media URL.
    """
    upload_prefix = getattr(settings, "CKEDITOR_UPLOADED_MEDIA_PREFIX", None)
    if upload_prefix:
        url = upload_prefix + path.replace(settings.CKEDITOR_UPLOAD_PATH, '')
    else:
        url = settings.MEDIA_URL + path.replace(settings.MEDIA_ROOT, '')
   
    # Remove any double slashes.
    return url.replace('//', '/')

def get_upload_filename(upload_name, user):
    # If CKEDITOR_RESTRICT_BY_USER is True upload file to user specific path.
    if getattr(settings, 'CKEDITOR_RESTRICT_BY_USER', False):
        user_path = user.username
    else:
        user_path = ''

    # Generate date based path to put uploaded file.
    date_path = datetime.now().strftime('%Y/%m')
    
    # Complete upload path (upload_path + date_path).
    upload_path = os.path.join(settings.CKEDITOR_UPLOAD_PATH, user_path, date_path)
   
    # Make sure upload_path exists.
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    
    # Get available name and return.
    return get_available_name(os.path.join(upload_path, upload_name))
     
    
@csrf_exempt
def upload(request):
    """
    Uploads a file and send back its URL to CKEditor.

    TODO:
        Validate uploads
    """
    
    # Get the uploaded file from request.
    upload = request.FILES['upload']
    upload_ext = os.path.splitext(upload.name)[1]
   
    # Open output file in which to store upload. 
    upload_filename = get_upload_filename(upload.name, request.user)
    out = open(upload_filename, 'wb+')

    # Iterate through chunks and write to destination.
    for chunk in upload.chunks():
        out.write(chunk)
    out.close()

    #create_thumbnail(upload_filename)

    # Respond with Javascript sending ckeditor upload url.
    url = get_media_url(upload_filename)
    return HttpResponse("""
    <script type='text/javascript'>
        window.parent.CKEDITOR.tools.callFunction(%s, '%s');
    </script>""" % (request.GET['CKEditorFuncNum'], url))

def get_image_files(user=None):
    """
    Recursively walks all dirs under upload dir and generates a list of
    full paths for each file found.

    """
    # If a user is provided and CKEDITOR_RESTRICT_BY_USER is True,
    # limit images to user specific path, but not for superusers.
    if user and not user.is_superuser and getattr(settings, 'CKEDITOR_RESTRICT_BY_USER', False):
        user_path = user.username
    else:
        user_path = ''


    browse_path = os.path.join(settings.CKEDITOR_UPLOAD_PATH, user_path)

    for root, dirs, files in os.walk(browse_path):
        for filename in [ os.path.join(root, x) for x in files ]:
            # bypass for thumbs
            if os.path.splitext(filename)[0].endswith('_thumb') or os.path.basename(filename).startswith('.'):
                 continue
            yield filename


        
        
def get_directory_contents(dirname, sort_field=None):
    """The directory is joined with the CKEDITOR_UPLOAD_PATH.
    A check is made not to go to directories below the CKEDITOR_UPLOAD_PATH.
    """
    if dirname is None:
        return None
        
    # Make sure the CKEDITOR_UPLOAD_PATH exists
    if not os.path.isdir(CKEDITOR_UPLOAD_PATH):
        os.makedirs(CKEDITOR_UPLOAD_PATH)
        
    # Join the CKEDITOR_UPLOAD_PATH and specified directory
    full_dirname = os.path.join(settings.CKEDITOR_UPLOAD_PATH, dirname)
    full_dirname = os.abspath(full_dirname)     # remove attempts to move the path upwards
    # If the directory doesn't exist, revert to the CKEDITOR_UPLOAD_PATH
    if not os.path.isdir(full_dirname): 
        full_dirname = settings.CKEDITOR_UPLOAD_PATH
    
    # array to hold directory contents
    dir_contents = []
    items = os.listdir(full_dirname)
    items = filter(lambda x: not x.startswith('.'), items)
    for item in items:
        fullpath = os.path.join(full_dirname, item)
        stats = os.stat(fullpath)
        # strftime('%y%m%d',localtime(os.stat('thefile' )[ST_MTIME])
        #print stats
        if os.path.isfile(fullpath):
            dli = DirListItem(item, DirListItem.TYPE_FILE, datetime.fromtimestamp(stats.st_mtime),  fsize=stats.st_size )
        elif os.path.isdir(fullpath):
            dli = DirListItem(item, DirListItem.TYPE_DIR, datetime.fromtimestamp(stats.st_mtime),  )
        dir_contents.append(dli)    
    
    if sort_field is not None and sort_field.startswith('-'):
        reverse_sort = True
        sort_field = sort_field[1:]
    else:
        reverse_sort = False
        
    if sort_field in DirListItem.ATTRS:
        dir_contents.sort(key=lambda obj: eval('obj.%s' % sort_field), reverse=reverse_sort)
    return dir_contents
    
def get_image_browse_urls(user=None):
    """
    Recursively walks all dirs under upload dir and generates a list of
    thumbnail and full image URL's for each file found.
    """
    images = []
    for filename in get_image_files(user=user):
        images.append({ 'thumb': get_media_url(get_thumb_filename(filename)), \
            'src': get_media_url(filename), \
            'basename' : os.path.basename(filename)
    })
        if len(images)==10: break
    return images


def get_json_str_as_http_response2(request, success, msg, json_str='', callback=None):
    """ Return a JSON object with the HTTP Response """

    if success:
         success_str = 'true'
    else:
         success_str = 'false'

    json_str = """{ "success": %s,
               "msg" : "%s"  %s }""" % (success_str, msg.replace('"',''), json_str)

    if callback is not None:
        json_str = '%s(%s)' % (callback, json_str)

    return HttpResponse(json_str)

def get_json_str_as_http_response(request, success, msg, lu_vals={}):
    """ Return a JSON object with the HTTP Response """

    return HttpResponse(get_json_str(success, msg, lu_vals))    


def render_to_string_remove_spaces(template_name, lookup={}):
    if template_name is None or lookup is None:
        return None

    rendered_str = render_to_string(template_name, lookup)
    return rendered_str.replace('\n', ' ').replace('\t', ' ')

def browse_ajax(request, callback=None):
    #print '-' * 50
    #print 'browse_ajax'
    if request.GET:
        callback = request.GET.get('jsoncallback', None)
        dirname = request.GET.get('d', '')
        sort_field = request.GET.get('sf', None)
    else:
        callback=None
        dirname = ''
        sort_field = None
    
    if len(dirname) > 0 and dirname[0] == '/':
        dirname = dirname[1:]   # doesn't throw err if dirname == '/'
        
    #print 'dirname', dirname
    #print 'sort_field', sort_field
    #print 'callback', callback
    
    lu = {'directory_details' : DirectoryDetails(dirname, sort_field=sort_field) }
    
    dir_files_html = render_to_string_remove_spaces('browse_ajax.html', lu)
    
    return get_json_str_as_http_response2(request, True, msg='', json_str=',"dir_files_html" : %s' % simplejson.dumps(dir_files_html), callback=callback)
        
    
def browse(request, dirname=''):
    #print get_directory_contents(dirname)

    context = RequestContext(request, {
        'directory_details' : DirectoryDetails('')  #imgs/news/thumb
        ,'current_folder' : dirname
        ,'CKEDITOR_MEDIA_URL' : settings.CKEDITOR_MEDIA_URL
        ,'CKEDITOR_UPLOADED_MEDIA_PREFIX' : settings.CKEDITOR_UPLOADED_MEDIA_PREFIX
    })
    return render_to_response('browse.html', context)
