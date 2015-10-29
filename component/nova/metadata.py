import os
import base64
from transcirrus.common import extras
from transcirrus.component.glance.glance_ops_v2 import glance_ops

# If the file xxx exists, then read it in and encode it to base64 and return the encoded string.
# If the file does not exist then return and empty string "".
# We use the metadata from the image to determine if we need to get a linux or windows version of the script.
def get_user_data(image_id):
    auth = extras.shadow_auth()
    glance = glance_ops(auth)
    image_details = glance.get_image(image_id)

    filename = "/home/transuser/%s-cloud-init-script.sh" % image_details['os_type']

    if not os.path.exists(filename):
        return ("")

    # Open and read in the entire file.
    with open (filename, "r") as file:
        data = file.read()

    b64_data = base64.b64encode(data)

    return (b64_data)
