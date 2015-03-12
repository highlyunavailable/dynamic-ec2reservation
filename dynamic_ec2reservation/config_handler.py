# -*- coding: utf-8 -*-
""" Configuration handler """
from  dynamic_ec2reservation import config

CONFIGURATION = config.get_configuration()

def get_global_option(option):
    """ Returns the value of the option
    :returns: str or None
    """
    try:
        return CONFIGURATION['global'][option]
    except KeyError:
        return None

def get_logging_option(option):
    """ Returns the value of the option
    :returns: str or None
    """
    try:
        return CONFIGURATION['logging'][option]
    except KeyError:
        return None
