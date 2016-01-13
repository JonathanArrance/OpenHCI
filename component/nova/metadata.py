import os
import base64
from transcirrus.common import extras
from transcirrus.component.glance.glance_ops_v2 import glance_ops

# If the file xxx exists, then read it in and encode it to base64 and return the encoded string.
# If the file does not exist then return and empty string "".
# We use the metadata from the image to determine if we need to get a linux or windows version of the script.
def get_user_data(image_id, exports={}):
    auth = extras.shadow_auth()
    glance = glance_ops(auth)
    image_details = glance.get_image(image_id)

    filename = "/home/transuser/%s-cloud-init-script.sh" % image_details['os_type']

    if not os.path.exists(filename):
        return ("")

    # Open and read in the entire file and replace the export section with any given exports.
    with open (filename, "r") as file:
        data=[]
        for line in file:
            if "<exports>" not in line:
                data.append(line)
            else:
                if exports == {}:
                    continue
                if image_details['os_type'] == "linux":
                    data.append("# Defined exports\n")
                    for key, value in exports.iteritems():
                        data.append('export %s="%s"\n' % (key,value))

    buff = ''.join(data)
    b64_buff = base64.b64encode(buff)
    return (b64_buff)

# Build a dictonary with the key/value pairs for any data we want to export to our user_data script.
def build_export_data(username):
    exports = {}
    exports['USER'] = username
    return (exports)
