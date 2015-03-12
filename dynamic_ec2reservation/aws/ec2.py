# -*- coding: utf-8 -*-
""" Ensure connections to EC2 """
from boto.ec2 import connect_to_region
from dynamic_ec2reservation.config_handler import get_global_option
from dynamic_ec2reservation.log_handler import LOGGER as logger

def __get_connection_ec2():
    """ Ensure connection to EC2 """
    region = get_global_option('region')
    try:
        if (get_global_option('aws_access_key_id') and
                get_global_option('aws_secret_access_key')):
            logger.debug(
                'Authenticating to EC2 using credentials in configuration file')
            connection = connect_to_region(
                region,
                aws_access_key_id=get_global_option('aws_access_key_id'),
                aws_secret_access_key=get_global_option(
                    'aws_secret_access_key'))
        else:
            logger.debug(
                'Authenticating using boto\'s authentication handler')
            connection = connect_to_region(region)

    except Exception as err:
        logger.error('Failed connecting to EC2: {0}'.format(err))
        raise

    logger.debug('Connected to EC2 in {0}'.format(region))
    return connection


EC2_CONNECTION = __get_connection_ec2()
