import json
import transcirrus.common.logger as logger

def error_codes(rest):
    load = json.loads(rest['data'])
    if(rest['response'] == 400):
        logger.sys_error("%s ERROR: 400"%(str(load['badRequest']['message'])))
        raise Exception("%s ERROR: 400"%(str(load['badRequest']['message'])))
    elif(rest['response'] == 401):
        logger.sys_error("%s ERROR: 401"%(str(load['unauthorized']['message'])))
        raise Exception("%s ERROR: 401"%(str(load['unauthorized']['message'])))
    elif(rest['response'] == 403):
        logger.sys_error("%s ERROR: 403"%(str(load['forbidden']['message'])))
        raise Exception("%s ERROR: 403"%(str(load['forbidden']['message'])))
    elif(rest['response'] == 404):
        logger.sys_error("%s ERROR: 404"%(str(load['itemNotFound']['message'])))
        raise Exception("%s ERROR: 404"%(str(load['itemNotFound']['message'])))
    elif(rest['response'] == 405):
        logger.sys_error("%s ERROR: 405"%(str(load['badMethod']['message'])))
        raise Exception("%s ERROR: 405"%(str(load['badMethod']['message'])))
    elif(rest['response'] == 409):
        logger.sys_error("%s ERROR: 409"%(str(load['conflictingRequest']['message'])))
        raise Exception("%s ERROR: 409"%(str(load['conflictingRequest']['message'])))
    elif(rest['response'] == 413):
        logger.sys_error("%s ERROR: 413"%(str(load['overLimit']['message'])))
        raise Exception("%s ERROR: 413"%(str(load['overLimit']['message'])))
    elif(rest['response'] == 415):
        raise Exception("%s ERROR: 415"%(str(load['badMediaType']['message'])))
        raise Exception("%s ERROR: 415"%(str(load['badMediaType']['message'])))
    elif(rest['response'] == 501):
        logger.sys_error("%s ERROR: 501"%(str(load['notImplemented']['message'])))
        raise Exception("%s ERROR: 501"%(str(load['notImplemented']['message'])))
    elif(rest['response'] == 503):
        logger.sys_error("%s ERROR: 503"%(str(load['serviceUnavailable']['message'])))
        raise Exception("%s ERROR: 503"%(str(load['serviceUnavailable']['message'])))
    else:
        logger.sys_error("An unknown error occured. ERROR:555")
        raise Exception("An unknown error occured. ERROR:555")