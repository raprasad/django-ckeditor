import os
from datetime import datetime

from django.conf import settings


class DirectoryItem:
    TYPE_FILE = 'file'
    TYPE_DIR= 'dir'
    ATTRS = ['name', 'item_type', 'mod_datetime', 'fsize']
    IMG_EXTENSIONS = ['png', 'jpg', 'gif', 'jpeg']
    def __init__(self, name, item_type, mod_datetime, dirname=None, fsize=0):
        self.name = name
        self.item_type = item_type
        self.mod_datetime = mod_datetime
        self.fsize = fsize
        self.dirname = dirname
        
        if self.item_type == DirectoryItem.TYPE_FILE:
            ext_str = self.name.split('.')[-1].lower()
            self.ext_str_class = 'ext_%s' %  ext_str
            
            # Is this an image file that can be previewed?
            if ext_str in DirectoryItem.IMG_EXTENSIONS:
                self.is_image_file = True
            else:
                self.is_image_file = False

        elif self.item_type == DirectoryItem.TYPE_DIR:
            self.ext_str_class = 'directory'
            self.is_image_file = False
    
    def get_file_or_dir_path(self):
        return os.path.join(self.dirname, self.name)


    def is_directory(self):
        if self.item_type == DirectoryItem.TYPE_DIR:
            return True
        return False
    
class DirectoryPart:
    def __init__(self, folder_name, dir_path):
        self.folder_name = folder_name
        self.dir_path = dir_path
                    
class DirectoryDetails:
    def __init__(self, dirname, sort_field='name'):
        self.dirname = dirname
        self.full_dirname = None    # evaluated later
        self.dir_contents = []      # list of DirectoryItem objects
        self.directory_parts = None # used for making a clickable directory path
        self.num_items = 0
        self.sort_field = sort_field
            
        self.load_directory_details()
        self.sort_directory_contents()
        self.make_directory_parts()
    
    def get_current_directory(self):
        if self.dirname == None or self.dirname =='' or str(self.dirname).strip()=='':
            return ''    
            
        if self.dirname[0] == '/':
            return self.dirname[0:]

        return self.dirname
        
    def make_directory_parts(self):
        if self.dirname is None:
            self.directory_parts = None
            return
        
        curr_path = ''
        self.directory_parts = []
        for folder in self.dirname.split(os.path.sep):
            curr_path = os.path.join(curr_path, folder)
            if folder in ['', '/']:
                dir_part = DirectoryPart('home', curr_path)
            else:
                dir_part = DirectoryPart(folder, curr_path)
            self.directory_parts.append(dir_part)
        
    
    def evaluate_directory_name(self):
        if self.dirname is None:
            # continues, will become base of settings.CKEDITOR_UPLOAD_PATH
            self.dirname = ''   
        
        # Make sure the CKEDITOR_UPLOAD_PATH exists
        if not os.path.isdir(settings.CKEDITOR_UPLOAD_PATH):
            os.makedirs(settings.CKEDITOR_UPLOAD_PATH)
        
        # Join the CKEDITOR_UPLOAD_PATH and specified directory
        full_dirname = os.path.join(settings.CKEDITOR_UPLOAD_PATH, self.dirname)
        
        # remove attempts to move the path above the CKEDITOR_UPLOAD_PATH
        # e.g. remove an attempt such as "?d=imgs/../../other_dir/../"
        full_dirname = os.path.abspath(full_dirname)     
        if not full_dirname.startswith(settings.CKEDITOR_UPLOAD_PATH):
            full_dirname = settings.CKEDITOR_UPLOAD_PATH
            self.dirname = ''
            self.full_dirname = full_dirname
            return
            
        self.dirname = full_dirname[len(settings.CKEDITOR_UPLOAD_PATH):]    

        # If the directory doesn't exist, revert to the CKEDITOR_UPLOAD_PATH
        if not os.path.isdir(full_dirname): 
            full_dirname = settings.CKEDITOR_UPLOAD_PATH
            self.dirname = ''
            
        self.full_dirname = full_dirname
    
    def load_directory_details(self):
        
        self.evaluate_directory_name()

        # list directory items
        # remove items starting with '.' or ending with '.py'
        items = os.listdir(self.full_dirname)   
        items = filter(lambda x: not (x.startswith('.') or x.endswith('.py')), items)

        self.dir_contents = []      # initialize array
        
        # add files and directories to the list, 
        # including file type, modification date, and size
        for item in items:
            fullpath = os.path.join(self.full_dirname, item)
            stats = os.stat(fullpath)

            if os.path.isfile(fullpath):
                di = DirectoryItem(item,\
                                    DirectoryItem.TYPE_FILE, \
                                    datetime.fromtimestamp(stats.st_mtime),\
                                    dirname=self.dirname,\
                                    fsize=stats.st_size\
                                     )
            elif os.path.isdir(fullpath):
                di = DirectoryItem(item, \
                                    DirectoryItem.TYPE_DIR, \
                                    datetime.fromtimestamp(stats.st_mtime), \
                                    dirname=self.dirname )
            self.dir_contents.append(di)    
            
        self.num_items = len(self.dir_contents)

    def sort_directory_contents(self):
        # sort the directory contents (array of DirectoryItem objects)
        # based on the sort_field
        if self.sort_field is None:
            self.sort_field = ''
            return

        if self.sort_field.startswith('-'):
            reverse_sort = True
            sort_param = self.sort_field[1:]
        else:
            reverse_sort = False
            sort_param = self.sort_field
            
        if sort_param in DirectoryItem.ATTRS:
            self.dir_contents.sort(key=lambda obj: eval('obj.%s' % sort_param), reverse=reverse_sort)
    
    
    
    
    
    