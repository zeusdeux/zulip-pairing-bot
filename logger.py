import os
import logging

def logger_setup(name):
    loglevel = ''
    try:
        if os.environ['PB_LOGLEVEL'] == 'DEBUG':
            loglevel = logging.DEBUG

        if os.environ['PB_LOGLEVEL'] == 'INFO':
            loglevel = logging.INFO

        if os.environ['PB_LOGLEVEL'] == 'WARN':
            loglevel = logging.WARN
    except:
        loglevel = logging.DEBUG

    # from https://docs.python.org/2/howto/logging.html#configuring-logging
    # set up new logger for this file
    logger = logging.getLogger(name)
    logger.setLevel(loglevel)

    # console handler for logging
    conLog = logging.StreamHandler()
    conLog.setLevel(loglevel)

    # formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # format console logs using formatter
    conLog.setFormatter(formatter)

    # add console logging transport to logger
    logger.addHandler(conLog)

    return logger
