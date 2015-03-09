# -*- coding: utf-8 -*-
""" Configuration management """
import sys
from dynamic_ec2reservation.config import config_file_parser
from dynamic_ec2reservation.config import command_line_parser

DEFAULT_OPTIONS = {
    'global': {
        # Command line only
        'config': None,
        'daemon': False,
        'instance': 'default',
        'dry_run': False,
        'pid_file_dir': '/tmp',
        'run_once': False,

        # [global]
        'region': 'us-east-1',
        'aws_access_key_id': None,
        'aws_secret_access_key': None,
        'check_interval': 3600
        },
    'logging': {
        # [logging]
        'log_file': None,
        'log_level': 'info',
        'log_config_file': None
        }
    }

def get_configuration():
    """ Get the configuration from command line and config files """
    # This is the dict we will return
    configuration = {
        'global': {},
        'logging': {},
        'tables': {}
    }

    # Read the command line options
    cmd_line_options = command_line_parser.parse()

    # If a configuration file is specified, read that as well
    conf_file_options = None
    if 'config' in cmd_line_options:
        conf_file_options = config_file_parser.parse(
            cmd_line_options['config'])

    # Extract global config
    configuration['global'] = __get_global_options(
        cmd_line_options,
        conf_file_options)

    # Extract logging config
    configuration['logging'] = __get_logging_options(
        cmd_line_options,
        conf_file_options)

    # Ensure some basic rules
    __check_logging_rules(configuration)

    return configuration

def __get_global_options(cmd_line_options, conf_file_options=None):
    """ Get all global options
    :type cmd_line_options: dict
    :param cmd_line_options: Dictionary with all command line options
    :type conf_file_options: dict
    :param conf_file_options: Dictionary with all config file options
    :returns: dict
    """
    options = {}

    for option in DEFAULT_OPTIONS['global'].keys():
        options[option] = DEFAULT_OPTIONS['global'][option]

        if conf_file_options and option in conf_file_options:
            options[option] = conf_file_options[option]

        if cmd_line_options and option in cmd_line_options:
            options[option] = cmd_line_options[option]

    return options


def __get_logging_options(cmd_line_options, conf_file_options=None):
    """ Get all logging options
    :type cmd_line_options: dict
    :param cmd_line_options: Dictionary with all command line options
    :type conf_file_options: dict
    :param conf_file_options: Dictionary with all config file options
    :returns: dict
    """
    options = {}

    for option in DEFAULT_OPTIONS['logging'].keys():
        options[option] = DEFAULT_OPTIONS['logging'][option]

        if conf_file_options and option in conf_file_options:
            options[option] = conf_file_options[option]

        if cmd_line_options and option in cmd_line_options:
            options[option] = cmd_line_options[option]

    return options

def __check_logging_rules(configuration):
    """ Check that the logging values are proper """
    valid_log_levels = [
        'debug',
        'info',
        'warning',
        'error'
    ]
    if configuration['logging']['log_level'].lower() not in valid_log_levels:
        print('Log level must be one of {0}'.format(
            ', '.join(valid_log_levels)))
        sys.exit(1)
