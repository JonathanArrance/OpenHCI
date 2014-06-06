import transcirrus.common.logger as logger

# Call the function required to get everything setup for logging.
logger.InitLogging()

# This function will setup the listener which listens for changes
# to the logging config file and will reload the config when a 
# change is made.
# We aren't going to use this yet since we have some sort of
# port conflict with something else. This needs to be fixed! 
#logger.StartConfigListener()
