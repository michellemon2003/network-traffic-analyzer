# Development notes

- `summarize()` opens the capture in binary mode and iterates over records using dpkt. It keeps counts and a byte total in memory while reading one frame at a time.
- `classify()` starts at Ethernet. ARP is identified directly. For IPv4 and IPv6, the decoded payload determines the TCP, UDP, or ICMP category. Unsupported or unparsed frames go into Other.
- `write_chart()` reuses the counts from the terminal summary. It creates a PNG with Matplotlib's `Figure` API and runs without a display server.
- The first implementation used Scapy. Its import attempted network interface discovery in the development environment, so the offline implementation switched to dpkt.
- `make_sample.py` writes six labeled synthetic records through dpkt. It needs no network interface. The fixed sequence keeps the expected counts easy to check by hand.
