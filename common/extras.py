from transcirrus.common.auth import authorization
from random import choice
from Crypto.Cipher import AES
import binascii as bin

def shadow_auth():
    """
    DESC:   authenticate as shadow_admin to perform tasks that need authentication but don't have an easy way to do so
    INPUT:  none
    OUTPUT: auth_dict: {
                            username
                            status_level    -   0 = not enabled, 1 = transcirrus only, 2 = transcirrus and keystone (mostly don't worry about this)
                            token
                            project_id
                            user_id
                            is_admin        -   0 = not admin, 1 = is admin
                            user_level      -   0 = admin, 1 = power user, 2 = user
                            password
                            db_object
                            adm_token       -   "" if not admin, otherwise some token
                        }
    ACCESS: wide open, but with great power comes great responsibility
    NOTE:   THIS IS A MAJOR HACK
    """
    #a = authorization('shadow_admin', 'manbehindthecurtain')
    a = authorization('admin', 'password')
    auth_dict = a.get_auth()
    return auth_dict


def make_password(length=16):
    """
    DESC:   generate a random password of length 16, used for third party authentication
    INPUT:  none
    OUTPUT: password
    ACCESS: wide open, but with great power comes great responsibility
    NOTE:
    """
    char_set = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ^!\$%&/()=?{[]}+~#-_.:,;<>|\\'
    pwd = []
    while len(pwd) < length:
        next = choice(char_set)
        pwd.append(next)
    return "".join(pwd)


def encrypt(plaintext):
    """
    DESC:   encrypt plaintext of length 16 using AES, used for third party authentication
    INPUT:  plaintext   -   req, usually coming from make_password function above
    OUTPUT: encrypted password
    ACCESS: wide open, but with great power comes great responsibility
    NOTE:   must be length 16
    """
    # check input string length
    if len(plaintext) % 16 != 0:
        raise Exception("String must be of length 16 for encryption.")

    # use shadow_admin's id as the key and initialization vector
    id = shadow_auth()['user_id']
    key, iv = id[:len(id)/2], id[len(id)/2:]
    crypt_obj = AES.new(key, AES.MODE_CBC, iv)
    return bin.b2a_base64(crypt_obj.encrypt(plaintext))


def decrypt(ciphertext):
    """
    DESC:   decrypt ciphertext using AES, used for third party authentication
    INPUT:  ciphertext  -   req, usually coming from encrypt function above
    OUTPUT: plaintext password
    ACCESS: wide open, but with great power comes great responsibility
    NOTE:
    """
    # use shadow_admin's id as the key and initialization vector
    id = shadow_auth()['user_id']
    key, iv = id[:len(id)/2], id[len(id)/2:]
    crypt_obj = AES.new(key, AES.MODE_CBC, iv)
    return crypt_obj.decrypt(bin.a2b_base64(ciphertext))