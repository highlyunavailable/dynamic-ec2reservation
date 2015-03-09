# -*- coding: utf-8 -*-
"""
Dynamic EC2 Reservation

Automatic rebalancing of AWS EC2 Reserved Instances between Availability Zones
"""
from __future__ import print_function

from dynamic_ec2reservation.config_handler import get_global_option
from dynamic_ec2reservation.daemon import Daemon
from dynamic_ec2reservation.log_handler import LOGGER as logger
from dynamic_ec2reservation.rebalance import (
    get_reservation_pool, get_reserved_instances, get_running_instances,
    get_changes, get_change_diff, execute_changes)

from boto.exception import JSONResponseError, BotoServerError

import sys
import time

class DynamicEC2ReservationDaemon(Daemon):
    """ Daemon for Dynamic DynamoDB"""
    def run(self):
        """ Run the daemon
        :type check_interval: int
        :param check_interval: Delay in seconds between checks
        """
        try:
            while True:
                execute()
        except Exception as error:
            logger.exception(error)

def main():
    """ Main function called from dynamic-ec2reservation """
    try:
        if get_global_option('daemon'):
            daemon = DynamicEC2ReservationDaemon(
                '{0}/dynamic-ec2reservation.{1}.pid'.format(
                    get_global_option('pid_file_dir'),
                    get_global_option('instance')))

            if get_global_option('daemon') == 'start':
                logger.debug('Starting daemon')
                try:
                    daemon.start()
                    logger.info('Daemon started')
                except IOError as error:
                    logger.error('Could not create pid file: {0}'.format(error))
                    logger.error('Daemon not started')
            elif get_global_option('daemon') == 'stop':
                logger.debug('Stopping daemon')
                daemon.stop()
                logger.info('Daemon stopped')
                sys.exit(0)

            elif get_global_option('daemon') == 'restart':
                logger.debug('Restarting daemon')
                daemon.restart()
                logger.info('Daemon restarted')

            elif get_global_option('daemon') in ['foreground', 'fg']:
                logger.debug('Starting daemon in foreground')
                daemon.run()
                logger.info('Daemon started in foreground')

            else:
                print(
                    'Valid options for --daemon are start, '
                    'stop, restart, and foreground')
                sys.exit(1)
        else:
            if get_global_option('run_once'):
                execute()
            else:
                while True:
                    execute()

    except Exception as error:
        logger.exception(error)


def execute():
    reserved_instances = get_reserved_instances()
    reservation_pool = get_reservation_pool()
    running_instances = get_running_instances()

    changes = get_changes(reservation_pool, running_instances)

    logstring = "Changing platform: {0}; network type: {1}; instance type: {2} to AZ members: {3}"
    diff = get_change_diff(reserved_instances, changes)

    if diff != {}:
        for platform in diff.keys():
            for netloc in diff[platform].keys():
                for instance_type in diff[platform][netloc].keys():
                    logger.info(
                        logstring.format(
                            platform, netloc, instance_type,
                            '; '.join("{0}: {1}".format(key, val) for (key, val) in diff[platform][netloc][instance_type].items())))

        if not get_global_option('dry_run'):
            execute_changes(diff)

    else:
        logger.debug('No changes needed')


    # Sleep between the checks
    if not get_global_option('run_once'):
        logger.debug('Sleeping {0} seconds until next check'.format(
            get_global_option('check_interval')))
        time.sleep(get_global_option('check_interval'))
