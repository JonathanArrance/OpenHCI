from django.core.files.uploadhandler import FileUploadHandler
from django.core.cache import cache

class UploadProgressCachedHandler(FileUploadHandler):
    """
    Tracks progress for file uploads.
    The http post request must contain a header or query parameter, 'X-Progress-ID'
    which should contain a unique string to identify the upload to be tracked.
    """

    def __init__(self, request=None):
        super(UploadProgressCachedHandler, self).__init__(request)
        self.progress_id = None
        self.cache_key = None

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        print "--handle_raw_input"
        print "  content_length %s" % content_length

        self.content_length = content_length
        self.progress_id = self.request.META['PATH_INFO'].split('/')[8]

        print "  self.progress_id: %s" % self.progress_id
        print "  self.content_length: %s" % self.content_length

        self.cache_key = "%s_%s" % (self.request.META['REMOTE_ADDR'], self.progress_id )
        cache.set (self.cache_key, {'length': self.content_length, 'uploaded' : 0})
        return
 
    def new_file(self, field_name, file_name, content_type, content_length, charset=None):
        print "--new_file"
        return

    # Required function for this class.
    def receive_data_chunk(self, raw_data, start):
        print "--receive_data_chunk"
        if self.cache_key:
            data = cache.get(self.cache_key)
            data['uploaded'] += self.chunk_size
            print "data: %s" % data
            cache.set(self.cache_key, data)
        return raw_data
    
    # Required function for this class.
    def file_complete(self, file_size):
        print "--file_complete"
        return

    def upload_complete(self):
        print "--upload_complete"
        if self.cache_key:
            cache.delete(self.cache_key)
        return
