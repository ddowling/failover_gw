#!/usr/bin/env python

import yaml
from arprequest import ArpRequest
from pyping import *

def main():
    config_file = "failover_gw.yaml"

    config = yaml.safe_load(open(config_file, 'r'))

    print("Started")

    while True:
        # Arp request primary and backup gateway looking for a response
        arp_primary = ArpRequest(config['primary_gw'], config['gw_interface'])
        primary_is_up = arp_primary.request()

        if primary_is_up:
            ping_via_primary = Ping(config['check_ip'],
                                    config['ping_timeout'],
                                    raw=True,
                                    source_interface=config['gw_interface'],
                                    dest_mac=arp_primary.getHardwareAddress())
            res = ping_via_primary.run(config['ping_count'])

            print(res.max_rtt, res.min_rtt, res.avg_rtt, res.ret_code)

            primary_gw_up = (res.ret_code == 0)
        else:
            primary_gw_up = False

        arp_backup = ArpRequest(config['backup_gw'], config['gw_interface'])
        backup_is_up = arp_backup.request()

        if backup_is_up:
            ping_via_backup = Ping(config['check_ip'],
                                   config['ping_timeout'],
                                   raw=True,
                                   source_interface=config['gw_interface'],
                                   dest_mac=arp_backup.getHardwareAddress())
            res = ping_via_backup.run(config['ping_count'])
            backup_gw_up = (res.ret_code == 0)
        else:
            backup_gw_up = False

        print("primary ARP is {} GW is {} secondary ARP is {} GW is {}".format(
                primary_is_up, primary_gw_up, backup_is_up, backup_gw_up))

        time.sleep(config['poll_interval'])


if __name__ == '__main__':
    main()
