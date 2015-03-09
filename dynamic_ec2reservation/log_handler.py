# -*- coding: utf-8 -*-
"""
Logging management for Dynamic EC2 Resrevations
"""
from __future__ import print_function
from logutils import dictconfig
import logging
import os.path
import sys
import config_handler

LOG_CONFIG = {
    'version': 1,
    'disable_existing_LOGGERs': False,
    'formatters': {
        'standard': {
            'format': (
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        },
        'dry-run': {
            'format': (
                '%(asctime)s - %(name)s - %(levelname)s - dryrun - %(message)s'
            )
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True
        },
        'dynamic-ec2reservation': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

if config_handler.get_logging_option('log_config_file'):
    # Read configuration from an external Python logging file
    logging.config.fileConfig(os.path.expanduser(
        config_handler.get_logging_option('log_config_file')))
else:
    # File handler
    if config_handler.get_logging_option('log_file'):
        log_file = os.path.expanduser(
            config_handler.get_logging_option('log_file'))
        LOG_CONFIG['handlers']['file'] = {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'standard',
            'filename': log_file,
            'when': 'midnight',
            'backupCount': 5
        }
        LOG_CONFIG['loggers']['']['handlers'].append('file')
        LOG_CONFIG['loggers']['dynamic-ec2reservation']['handlers'].append('file')

    # Configure a custom log level
    if config_handler.get_logging_option('log_level'):
        LOG_CONFIG['handlers']['console']['level'] = \
            config_handler.get_logging_option('log_level').upper()
        if 'file' in LOG_CONFIG['handlers']:
            LOG_CONFIG['handlers']['file']['level'] = \
                config_handler.get_logging_option('log_level').upper()

    # Add dry-run to the formatter if in dry-run mode
    if config_handler.get_global_option('dry_run'):
        LOG_CONFIG['handlers']['console']['formatter'] = 'dry-run'
        if 'file' in LOG_CONFIG['handlers']:
            LOG_CONFIG['handlers']['file']['formatter'] = 'dry-run'

    try:
        dictconfig.dictConfig(LOG_CONFIG)
    except ValueError as error:
        print('Error configuring logger: {0}'.format(error))
        sys.exit(1)
    except:
        raise

LOGGER = logging.getLogger('dynamic-ec2reservation')
