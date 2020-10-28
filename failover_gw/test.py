from arprequest import ArpRequest
ip = '192.168.90.1'
dev = 'ens33'
print("ip = ", ip, "dev = ", dev)
ar = ArpRequest(ip, dev)

print("Request returned", ar.request())
print("getHardwareAddress() = ", ar.getHardwareAddress())
print("getHardwareAddressStr() = ", ar.getHardwareAddressStr())

from pyping import Ping

p = Ping(destination=ip,
         timeout=2,
         source_interface=dev,
         dest_mac=ar.getHardwareAddress(),
         quiet_output=True)

res = p.run(4)
print("Ping %s via %s RTT=%.3f,%.3f,%.3fms" % (ip, dev,
					       res.min_rtt, res.avg_rtt,
                                               res.max_rtt))
