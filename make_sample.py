"""Write a classroom PCAP fixture without transmitting packets."""

from ipaddress import IPv4Address

import dpkt

SOURCE = IPv4Address("192.0.2.1").packed
DESTINATION = IPv4Address("192.0.2.2").packed
MAC_SOURCE = bytes.fromhex("020000000001")
MAC_DESTINATION = bytes.fromhex("020000000002")


def ethernet(payload, kind=dpkt.ethernet.ETH_TYPE_IP):
    return dpkt.ethernet.Ethernet(src=MAC_SOURCE, dst=MAC_DESTINATION, type=kind, data=payload)


def ipv4(protocol, transport):
    return dpkt.ip.IP(src=SOURCE, dst=DESTINATION, p=protocol, data=transport)


def main():
    packets = [
        ethernet(ipv4(dpkt.ip.IP_PROTO_TCP, dpkt.tcp.TCP(sport=12345, dport=80))),
        ethernet(ipv4(dpkt.ip.IP_PROTO_TCP, dpkt.tcp.TCP(sport=80, dport=12345))),
        ethernet(ipv4(dpkt.ip.IP_PROTO_UDP, dpkt.udp.UDP(sport=12345, dport=9000))),
        ethernet(ipv4(dpkt.ip.IP_PROTO_ICMP, dpkt.icmp.ICMP(type=8, data=dpkt.icmp.ICMP.Echo()))),
        ethernet(dpkt.arp.ARP(sha=MAC_SOURCE, spa=SOURCE, tpa=DESTINATION), dpkt.ethernet.ETH_TYPE_ARP),
        ethernet(b"example", 0x88B5),
    ]
    with open("sample.pcap", "wb") as output:
        writer = dpkt.pcap.Writer(output)
        for timestamp, packet in enumerate(packets, start=1):
            writer.writepkt(packet, ts=timestamp)
    print("Wrote sample.pcap (six synthetic packets)")


if __name__ == "__main__":
    main()
