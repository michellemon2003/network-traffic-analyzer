"""Summarize an existing capture and render an offline protocol chart."""

import argparse
from collections import Counter
from pathlib import Path

from matplotlib.figure import Figure
import dpkt

PROTOCOLS = ("TCP", "UDP", "ICMP", "ARP", "Other")


def classify(packet) -> str:
    """Assign one category based on the first network and transport headers."""
    network = dpkt.ethernet.Ethernet(packet).data
    if isinstance(network, dpkt.arp.ARP):
        return "ARP"
    if isinstance(network, (dpkt.ip.IP, dpkt.ip6.IP6)):
        transport = network.data
        for header, label in (
            (dpkt.tcp.TCP, "TCP"),
            (dpkt.udp.UDP, "UDP"),
            ((dpkt.icmp.ICMP, dpkt.icmp6.ICMP6), "ICMP"),
        ):
            if isinstance(transport, header):
                return label
    return "Other"

def summarize(path: Path) -> tuple[Counter, int]:
    counts = Counter(dict.fromkeys(PROTOCOLS, 0))
    captured_bytes = 0
    with path.open("rb") as source:
        capture = dpkt.pcap.Reader(source)
        if capture.datalink() != dpkt.pcap.DLT_EN10MB:
            raise ValueError("Export the capture as classic PCAP with Ethernet link type.")
        for _, packet in capture:
            try:
                category = classify(packet)
            except dpkt.UnpackError:
                category = "Other"
            counts[category] += 1
            captured_bytes += len(packet)
    return counts, captured_bytes


def write_chart(counts: Counter, output: Path) -> None:
    figure = Figure(figsize=(7, 4), layout="constrained")
    axes = figure.subplots()
    bars = axes.bar(PROTOCOLS, [counts[name] for name in PROTOCOLS], color="#235786")
    axes.bar_label(bars)
    axes.set_ylim(0, max(1, max(counts.values()) * 1.25))
    axes.set(ylabel="Packet count", title="Protocol distribution")
    axes.yaxis.get_major_locator().set_params(integer=True)
    figure.savefig(output, format="png")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path, help="Authorized PCAP file")
    parser.add_argument("--chart", type=Path, default=Path("protocols.png"))
    args = parser.parse_args()
    if args.chart.suffix.lower() != ".png":
        parser.error("--chart must end in .png")
    if args.chart.exists():
        parser.error("--chart already exists. Choose another path or remove the old chart.")
    try:
        counts, captured_bytes = summarize(args.capture)
        write_chart(counts, args.chart)
    except (OSError, dpkt.UnpackError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")

    total = sum(counts.values())
    print(f"Packets: {total} | Captured bytes: {captured_bytes}")
    if total:
        print(f"Mean captured packet size: {captured_bytes / total:.1f} bytes")
    for name in PROTOCOLS:
        percent = 100 * counts[name] / total if total else 0
        print(f"{name:5} {counts[name]:5} ({percent:5.1f}%)")
    print(f"Chart: {args.chart}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
