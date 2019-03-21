#!/usr/bin/env python

import yaml
from arprequest import ArpRequest
from pyping import *
import subprocess
import re

def get_route_gw(route):
    res = subprocess.check_output([ 'ip', 'route', 'list', route ])
    #print res

    p = re.compile(".*via ([^ ]*) .*")
    m = p.match(res)
    if not m:
        return None
    else:
        return m.group(1)


def replace_route(route, gw):
    res = subprocess.check_output([ 'ip', 'route', 'replace', route, 'via', gw])
    #print res
    return True

def main():
    config_file = "failover_gw.yaml"

    config = yaml.safe_load(open(config_file, 'r'))

    poll_interval = config['poll_interval'] or 10
    gw_interface = config['gw_interface'] or 'eth0'
    check_ip = config['check_ip']
    managed_route = config['managed_route']
    primary_gw = config['primary_gw']
    backup_gw = config['backup_gw']
    ping_timeout = config['ping_timeout'] or 2000
    ping_count = config['ping_count'] or  3

    print("Started")

    while True:
        # Arp request primary and backup gateway looking for a response
        arp_primary = ArpRequest(primary_gw, gw_interface)
        primary_is_up = arp_primary.request()

        if primary_is_up:
            ping_via_primary = Ping(check_ip,
                                    ping_timeout,
                                    raw=True,
                                    source_interface=gw_interface,
                                    dest_mac=arp_primary.getHardwareAddress())
            res = ping_via_primary.run(ping_count)

            if res.ret_code == 0:
                print("Ping {} via {} RTT={},{},{}ms".format(
                        check_ip, primary_gw, res.min_rtt, res.avg_rtt, res.max_rtt))
                primary_gw_up = True
            else:
                print("Ping {} via {} failed : {}",format(
                        check_ip, primary_gw, res.output))
                primary_gw_up = False
        else:
            print("Primary gateway {} is down".format(primary_gw))
            primary_gw_up = False

        arp_backup = ArpRequest(backup_gw, gw_interface)
        backup_is_up = arp_backup.request()

        if backup_is_up:
            ping_via_backup = Ping(check_ip,
                                   ping_timeout,
                                   raw=True,
                                   source_interface=gw_interface,
                                   dest_mac=arp_backup.getHardwareAddress())
            res = ping_via_backup.run(ping_count)

            if res.ret_code == 0:
                print("Ping {} via {} RTT={},{},{}ms".format(
                        check_ip, backup_gw, res.min_rtt, res.avg_rtt, res.max_rtt))
                backup_gw_up = True
            else:
                print("Ping {} via {} failed : {}",format(
                        check_ip, backup_gw, res.output))
                backup_gw_up = False
            backup_gw_up = (res.ret_code == 0)
        else:
            print("Backup gateway {} is down".format(backup_gw))
            backup_gw_up = False

        print("primary ARP is {} GW is {} secondary ARP is {} GW is {}".format(
                primary_is_up, primary_gw_up, backup_is_up, backup_gw_up))

        current_gw = get_route_gw(managed_route)
        if primary_gw_up:
            if managed_route and current_gw != primary_gw:
                print("Switch route {} to primary gateway {}".format(managed_route, primary_gw))
                replace_route(managed_route, primary_gw)
        elif backup_gw_up:
            if managed_route and current_gw != backup_gw:
                print("Switch route {} to backup gateway {}".format(managed_route, backup_gw))
                replace_route(managed_route, backup_gw)
        else:
            print("No routes for {} as neither gateway responding for {}".format(managed_route, check_ip))

        time.sleep(config['poll_interval'])


if __name__ == '__main__':
    main()
