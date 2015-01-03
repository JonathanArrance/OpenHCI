import json
import transcirrus.common.logger as logger

def error_codes(rest):
    load = json.loads(rest['data'])
    if(rest['response'] == 400):
        logger.sys_error("%s ERROR: 400"%(str(load)))
        raise Exception("%s ERROR: 400"%(str(load)))
    elif(rest['response'] == 401):
        logger.sys_error("%s ERROR: 401"%(str(load)))
        raise Exception("%s ERROR: 401"%(str(load)))
    elif(rest['response'] == 403):
        logger.sys_error("%s ERROR: 403"%(str(load)))
        raise Exception("%s ERROR: 403"%(str(load)))
    elif(rest['response'] == 404):
        logger.sys_error("%s ERROR: 404"%(str(load)))
        raise Exception("%s ERROR: 404"%(str(load)))
    elif(rest['response'] == 405):
        logger.sys_error("%s ERROR: 405"%(str(load)))
        raise Exception("%s ERROR: 405"%(str(load)))
    elif(rest['response'] == 409):
        logger.sys_error("%s ERROR: 409"%(str(load['QuantumError'])))
        raise Exception("%s ERROR: 409"%(str(load['QuantumError'])))
    elif(rest['response'] == 413):
        logger.sys_error("%s ERROR: 413"%(str(load)))
        raise Exception("%s ERROR: 413"%(str(load)))
    elif(rest['response'] == 415):
        raise Exception("%s ERROR: 415"%(str(load)))
        raise Exception("%s ERROR: 415"%(str(load)))
    elif(rest['response'] == 501):
        logger.sys_error("%s ERROR: 501"%(str(load)))
        raise Exception("%s ERROR: 501"%(str(load)))
    elif(rest['response'] == 503):
        logger.sys_error("%s ERROR: 503"%(str(load)))
        raise Exception("%s ERROR: 503"%(str(load)))
    else:
        logger.sys_error("An unknown error occured. ERROR:555")
        raise Exception("An unknown error occured. ERROR:555")