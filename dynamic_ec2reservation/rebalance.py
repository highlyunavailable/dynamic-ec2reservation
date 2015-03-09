"""
Dynamic EC2 Reservation

Core logic to do a rebalance of instances based on their OS type, network
location and instance type.
"""

from copy import deepcopy
from datetime import datetime
from boto.ec2.reservedinstance import ReservedInstancesConfiguration
from dynamic_ec2reservation.aws.ec2 import EC2_CONNECTION as conn

def get_reservation_pool():
    """ Get a pool of servers that are available to rebalance. Returns a dict in
    the form of:

    {operating_sys: network_platform: instance_type: sum(instance_count per AZ)}

    :returns: dict
    """
    instances = get_reserved_instances()

    pool = deepcopy(instances)
    for platform in instances.keys():
        for netloc in instances[platform].keys():
            for instance_type in instances[platform][netloc].keys():
                pool[platform][netloc][instance_type] = \
                    sum(instances[platform][netloc][instance_type].values())

    return pool

def get_reserved_instances():
    """ Get currently active reservations per AZ. Returns a dict in the form
    of:

    {operating_sys: network_platform: instance_type: az: count}

    :returns: dict
    """
    pool = {}

    reserved_instances = conn.get_all_reserved_instances(
        filters={'state':'active'})

    for ri in reserved_instances:
        netloc = 'EC2-Classic'
        platform = 'linux'

        if 'Amazon VPC' in ri.description:
            netloc = 'EC2-VPC'

        if 'Windows' in ri.description:
            platform = 'windows'

        if platform not in pool.keys():
            pool[platform] = {}

        if netloc not in pool[platform].keys():
            pool[platform][netloc] = {}

        if ri.instance_type not in pool[platform][netloc].keys():
            pool[platform][netloc][ri.instance_type] = {}

        if ri.availability_zone not in pool[platform][netloc][ri.instance_type].keys():
            pool[platform][netloc][ri.instance_type][ri.availability_zone] = 0

        pool[platform][netloc][ri.instance_type][ri.availability_zone] += ri.instance_count

    return pool

def get_running_instances():
    """ Get currently running servers. Returns a dict in the form of:

    {operating_sys: network_platform: instance_type: az: count}

    :returns: dict
    """
    pool = {}

    instances = conn.get_only_instances(filters={'instance-state-name':'running'})

    for i in instances:
        netloc = 'EC2-Classic'
        platform = 'linux'

        if i.vpc_id:
            netloc = 'EC2-VPC'

        if i.platform == 'windows':
            platform = 'windows'

        if not platform in pool.keys():
            pool[platform] = {}

        if netloc not in pool[platform].keys():
            pool[platform][netloc] = {}

        if i.instance_type not in pool[platform][netloc].keys():
            pool[platform][netloc][i.instance_type] = {}

        if not i.placement in pool[platform][netloc][i.instance_type].keys():
            pool[platform][netloc][i.instance_type][i.placement] = 0

        pool[platform][netloc][i.instance_type][i.placement] += 1

    return pool

def get_changes(reserved_pool, instances):
    """ Builds a dictionary of what the reservations "should" be. Returns a
    dict in the form of:

    {operating_sys: network_platform: instance_type: az: count}

    :type reserved_pool: dict
    :param reserved_pool: The pool of reserved instances by OS/network/type
    :type instances: dict
    :param instances: The currently running instance count by AZ
    :returns: dict
    """
    result = deepcopy(instances)

    for platform in instances.keys():
        if platform not in reserved_pool.keys():
            del result[platform]
            continue
        for netloc in instances[platform].keys():
            if netloc not in reserved_pool[platform].keys():
                del result[platform][netloc]
                continue

            for instance_type in instances[platform][netloc].keys():
                if instance_type not in reserved_pool[platform][netloc].keys():
                    del result[platform][netloc][instance_type]
                    continue

                for az in instances[platform][netloc][instance_type].keys():
                    if reserved_pool[platform][netloc][instance_type] == 0:
                        del result[platform][netloc][instance_type][az]
                        continue

                    reserve_count = min(
                        reserved_pool[platform][netloc][instance_type],
                        result[platform][netloc][instance_type][az])

                    reserved_pool[platform][netloc][instance_type] -= reserve_count
                    result[platform][netloc][instance_type][az] = reserve_count

    return result

def get_change_diff(current, new):
    """ Takes two os:netplatform:instancetype:az dictionaries and returns only
    keys where the descendents are different.

    :type current: dict
    :param current: The current list of instances.
    :type new: dict
    :param new: The new list of instances.
    :returns: dict
    """
    result = deepcopy(new)
    if current == new:
        return {}

    for platform in current.keys():
        if current[platform] == new.get(platform):
            del result[platform]
            continue

        for netloc in current[platform].keys():
            if current[platform][netloc] == new[platform].get(netloc):
                del result[platform][netloc]
                continue

            for instance_type in current[platform][netloc].keys():
                if current[platform][netloc][instance_type] == \
                        new[platform][netloc].get(instance_type):
                    del result[platform][netloc][instance_type]
                    continue

    return result

def execute_changes(changes):
    """ Takes an EC2 connection and a list of changes to make, then converts
    the list into operations on actual EC2 reservations. The calling user or
    role must have the ec2:ModifyReservedInstances permission.

    :type changes: dict
    :param changes: The list of reservations to set.
    :returns: dict
    """
    reserved_instances = conn.get_all_reserved_instances(
        filters={'state':'active'})

    for platform, reservations in changes.iteritems():
        for netloc in reservations.keys():
            for instance_type in reservations[netloc].keys():
                reservation_ids = [r.id for r in reserved_instances \
                        if platform in r.description.lower() and r.instance_type == instance_type]
                reservedinstancesconfigurations = []
                for az, count in reservations[netloc][instance_type].iteritems():
                    reservedinstancesconfigurations.append(
                        ReservedInstancesConfiguration(
                            connection=conn,
                            availability_zone=az,
                            platform=netloc,
                            instance_type=instance_type,
                            instance_count=count
                            ))
                conn.modify_reserved_instances(
                    "dynamic-reservation-{0}-{1}-{2}".format(
                        netloc,
                        instance_type,
                        repr(datetime.utcnow())
                        ),
                    reservation_ids,
                    reservedinstancesconfigurations
                    )
