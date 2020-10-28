from arprequest import ArpRequest
ip = '192.168.90.1'
dev = 'ens33'
print("ip = ", ip, "dev = ", dev)
ar = ArpRequest(ip, dev)

print("Request returned", ar.request())
print("getHardwareAddress() = ", ar.getHardwareAddress())
print("getHardwareAddressStr() = ", ar.getHardwareAddressStr())

from pyping import Ping

for i in range(4):
    is_raw = ( i >= 2 )
    is_quiet = ( i % 2 == 0 )
    print("is_raw=", is_raw, "is_quiet=", is_quiet)
    p = Ping(destination=ip,
             timeout=1,
             raw=is_raw,
             source_interface=dev,
             dest_mac=ar.getHardwareAddress(),
             quiet_output=is_quiet)

    res = p.run(4)
    if res is not None:
        print("Ping %s via %s RTT=%.3f,%.3f,%.3fms" % (ip, dev,
					               res.min_rtt, res.avg_rtt,
                                                       res.max_rtt))
