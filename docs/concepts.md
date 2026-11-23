# Concepts

**Classic PCAP** stores capture metadata and a record for each captured packet. The record contains a timestamp and the bytes included by the capture. A file named `.pcap` still needs a valid header.

**Protocol layers** describe different jobs. Ethernet frames can carry ARP directly or carry IP, which can in turn carry TCP, UDP or ICMP. Counting one category per frame avoids counting the same packet again as both IP and TCP.

**Packet share** divides the number of packets in one category by all counted packets. A high share describes frequency in the supplied capture. It gives limited information about data volume, traffic quality or malicious intent.
