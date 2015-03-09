# -*- coding: utf-8 -*-
""" Command line configuration parser """
import sys
import os.path
import argparse
import ConfigParser

def parse():
    """ Parse command line options """
    parser = argparse.ArgumentParser(
        description='Dynamic EC2 Reservation - Auto rebalance EC2 reservations')
    parser.add_argument(
        '-c', '--config',
        help='Read configuration from a configuration file')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without making any changes to your EC2 reservations')
    parser.add_argument(
        '--run-once',
        action='store_true',
        help='Run once and then exit Dynamic EC2 Reservation, instead of looping')
    parser.add_argument(
        '--check-interval',
        type=int,
        help="""How many seconds should we wait between
                the checks (default: 300)""")
    parser.add_argument(
        '--log-file',
        help='Send output to the given log file')
    parser.add_argument(
        '--log-level',
        choices=['debug', 'info', 'warning', 'error'],
        help='Log level to use (default: info)')
    parser.add_argument(
        '--log-config-file',
        help=(
            'Use a custom Python logging configuration file. Overrides both '
            '--log-level and --log-file.'
        ))
    parser.add_argument(
        '--version',
        action='store_true',
        help='Print current version number')
    parser.add_argument(
        '--aws-access-key-id',
        help="Override Boto configuration with the following AWS access key")
    parser.add_argument(
        '--aws-secret-access-key',
        help="Override Boto configuration with the following AWS secret key")
    daemon_ag = parser.add_argument_group('Daemon options')
    daemon_ag.add_argument(
        '--daemon',
        help=(
            'Run Dynamic EC2 Reservation in daemon mode. Valid modes are '
            '[start|stop|restart|foreground]'))
    daemon_ag.add_argument(
        '--instance',
        default='default',
        help=(
            'Name of the Dynamic EC2 Reservation instance. '
            'Used to run multiple instances of Dynamic EC2 Reservation. '
            'Give each instance a unique name and control them separately '
            'with the --daemon flag. (default: default)'))
    daemon_ag.add_argument(
        '--pid-file-dir',
        default='/tmp',
        help='Directory where pid file is located in. Defaults to /tmp')
    ec2_ag = parser.add_argument_group('EC2 options')
    ec2_ag.add_argument(
        '-r', '--region',
        help='AWS region to operate in (default: us-east-1')

    args = parser.parse_args()

    # Print the version and quit
    if args.version:
        # Read the dynamic-ec2reservation.conf configuration file
        internal_config_file = ConfigParser.RawConfigParser()
        internal_config_file.optionxform = lambda option: option
        internal_config_file.read(
            os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__), '../dynamic-ec2reservation.conf')))

        print 'Dynamic EC2 Reservation version: {0}'.format(
            internal_config_file.get('general', 'version'))
        sys.exit(0)

    # Replace any new values in the configuration
    configuration = {}
    for arg in args.__dict__:
        if args.__dict__.get(arg) is not None:
            configuration[arg] = args.__dict__.get(arg)

    return configuration
