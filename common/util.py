#DESC: Logs and rasies excpetions from the OpenStack REST API
#INPUT: code - https error code
#       reason - message from REST API
#OUTPUT: void
def _http_codes(code,reason):
    if(code):
        logger.sys_error("Response %s with Reason %s" %(code,reason))
        raise Exception("Response %s with Reason %s" %(code,reason))
    else:
        logger.sys_error("Error for unknown reason.")
        raise Exception("Error for unknown reason.")