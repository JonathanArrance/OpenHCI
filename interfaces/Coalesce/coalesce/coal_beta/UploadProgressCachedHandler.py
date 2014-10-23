from django.core.files.uploadhandler import FileUploadHandler
from django.core.cache import cache

class UploadProgressCachedHandler(FileUploadHandler):
    """
    Tracks progress for file uploads.
    This is not really being used to track progress at this point because the browser is giving the UI the data.
    """

    def __init__(self, request=None):
        super(UploadProgressCachedHandler, self).__init__(request)
        self.progress_id = None
        self.cache_key = None

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        self.content_length = content_length
        self.progress_id = self.request.META['PATH_INFO'].split('/')[8]
        self.cache_key = "%s_%s" % (self.request.META['REMOTE_ADDR'], self.progress_id )
        cache.set (self.cache_key, {'length': self.content_length, 'uploaded' : 0})
        return
 
    def new_file(self, field_name, file_name, content_type, content_length, charset=None):
        return

    # Required function for this class.
    def receive_data_chunk(self, raw_data, start):
        if self.cache_key:
            data = cache.get(self.cache_key)
            data['uploaded'] += self.chunk_size
            cache.set(self.cache_key, data)
        return raw_data
    
    # Required function for this class.
    def file_complete(self, file_size):
        return

    def upload_complete(self):
        if self.cache_key:
            cache.delete(self.cache_key)
        return
