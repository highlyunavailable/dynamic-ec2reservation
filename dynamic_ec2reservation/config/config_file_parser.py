# -*- coding: utf-8 -*-
""" Command line configuration parser """
import sys
import os.path
import ConfigParser

def __parse_options(config_file, section, options):
    """ Parse the section options

    :type config_file: ConfigParser object
    :param config_file: The config file object to use
    :type section: str
    :param section: Which section to read in the configuration file
    :type options: list of dicts
    :param options:
        A list of options to parse. Example list::
        [{
            'key': 'aws_access_key_id',
            'option': 'aws-access-key-id',
            'required': False,
            'type': str
        }]
    :returns: dict
    """
    configuration = {}
    for option in options:
        try:
            if option.get('type') == 'str':
                configuration[option.get('key')] = \
                    config_file.get(section, option.get('option'))
            elif option.get('type') == 'int':
                try:
                    configuration[option.get('key')] = \
                        config_file.getint(section, option.get('option'))
                except ValueError:
                    print('Error: Expected an integer value for {0}'.format(
                        option.get('option')))
                    sys.exit(1)
            elif option.get('type') == 'float':
                try:
                    configuration[option.get('key')] = \
                        config_file.getfloat(section, option.get('option'))
                except ValueError:
                    print('Error: Expected an float value for {0}'.format(
                        option.get('option')))
                    sys.exit(1)
            elif option.get('type') == 'bool':
                try:
                    configuration[option.get('key')] = \
                        config_file.getboolean(section, option.get('option'))
                except ValueError:
                    print('Error: Expected an boolean value for {0}'.format(
                        option.get('option')))
                    sys.exit(1)
            else:
                configuration[option.get('key')] = \
                    config_file.get(section, option.get('option'))
        except ConfigParser.NoOptionError:
            if option.get('required'):
                print 'Missing [{0}] option "{1}" in configuration'.format(
                    section, option.get('option'))
                sys.exit(1)

    return configuration


def parse(config_path):
    """ Parse the configuration file

    :type config_path: str
    :param config_path: Path to the configuration file
    """
    config_path = os.path.expanduser(config_path)

    # Read the configuration file
    config_file = ConfigParser.RawConfigParser()
    config_file.optionxform = lambda option: option
    config_file.read(config_path)

    #
    # Handle [global]
    #
    if 'global' in config_file.sections():
        global_config = __parse_options(
            config_file,
            'global',
            [
                {
                    'key': 'aws_access_key_id',
                    'option': 'aws-access-key-id',
                    'required': False,
                    'type': 'str'
                },
                {
                    'key': 'aws_secret_access_key',
                    'option': 'aws-secret-access-key-id',
                    'required': False,
                    'type': 'str'
                },
                {
                    'key': 'region',
                    'option': 'region',
                    'required': False,
                    'type': 'str'
                },
                {
                    'key': 'check_interval',
                    'option': 'check-interval',
                    'required': False,
                    'type': 'int'
                }
            ])

    #
    # Handle [logging]
    #
    if 'logging' in config_file.sections():
        logging_config = __parse_options(
            config_file,
            'logging',
            [
                {
                    'key': 'log_level',
                    'option': 'log-level',
                    'required': False,
                    'type': 'str'
                },
                {
                    'key': 'log_file',
                    'option': 'log-file',
                    'required': False,
                    'type': 'str'
                },
                {
                    'key': 'log_config_file',
                    'option': 'log-config-file',
                    'required': False,
                    'type': 'str'
                }
            ])

    return dict(
        global_config.items() +
        logging_config.items())
