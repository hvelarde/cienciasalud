# This Python file uses the following encoding: utf-8

"""
$Id: utils.py 57156 2008-01-19 00:08:24Z hvelarde $
"""

import logging

WARNING = logging.WARNING
logger = logging.getLogger('nitf4plone')

# generic log method
def log(message, summary='', severity=logging.INFO):
    logger.log(severity, '%s \n%s', summary, message)
