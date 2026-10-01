"""Jitter, loss, and a simple MOS estimate for a sample call.

RTP rows are arrival timestamps in milliseconds for a 20 ms packet period.
Loss is missing sequence numbers between the first and last packet.
Jitter is the mean absolute deviation of inter-arrival time from 20 ms,
counted only across packets whose sequence numbers differ by 1.
"""

from __future__ import annotations

from dataclasses import dataclass

PACKET_MS = 20


@dataclass
class RtpReport:
    received: int
    expected: int
    loss_pct: float
    jitter_ms: float
    mos: float


@dataclass
class SipEvent:
    clock: str
    source: str
    destination: str
    message: str


def analyze_rtp(csv_text: str) -> RtpReport:
    rows = []
    for line in csv_text.splitlines():
        line = line.strip()
        if not line or line.lower().startswith("seq"):
            continue
        seq_raw, ts_raw, _size = line.split(",")
        rows.append((int(seq_raw), float(ts_raw)))
    if len(rows) < 2:
        raise ValueError("need at least two RTP rows")
    rows.sort()
    expected = rows[-1][0] - rows[0][0] + 1
    received = len({seq for seq, _ts in rows})
    lost = expected - received
    gaps = []
    by_seq = dict(rows)
    for seq, ts in rows:
        nxt = by_seq.get(seq + 1)
        if nxt is None:
            continue
        gaps.append(abs((nxt - ts) - PACKET_MS))
    jitter = sum(gaps) / len(gaps) if gaps else 0.0
    loss_pct = (lost / expected) * 100
    return RtpReport(
        received=received,
        expected=expected,
        loss_pct=round(loss_pct, 2),
        jitter_ms=round(jitter, 2),
        mos=estimate_mos(jitter, loss_pct),
    )


def estimate_mos(jitter_ms: float, loss_pct: float, delay_ms: float = 0.0) -> float:
    """A small E-model style estimate. It is a lab score, not a certified MOS."""
    latency = delay_ms + jitter_ms * 2 + 10
    if latency < 160:
        rating = 93.2 - (latency / 40)
    else:
        rating = 93.2 - (latency - 120) / 10
    rating -= loss_pct * 2.5
    rating = max(0.0, min(100.0, rating))
    score = 1 + 0.035 * rating + 0.000007 * rating * (rating - 60) * (100 - rating)
    return round(max(1.0, min(4.5, score)), 2)


def parse_sip(text: str) -> list[SipEvent]:
    events = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        clock, rest = line.split(" ", 1)
        source, arrow, destination, message = rest.split(" ", 3)
        if arrow != "->":
            raise ValueError(f"expected '->' in {line}")
        events.append(SipEvent(clock, source, destination, message))
    if not events:
        raise ValueError("SIP trace is empty")
    return events


def call_ladder(events: list[SipEvent]) -> str:
    names = []
    for event in events:
        for name in (event.source, event.destination):
            if name not in names:
                names.append(name)
    width = 16
    header = "".join(name.ljust(width) for name in names).rstrip()
    lines = [header, "-" * len(header)]
    columns = {name: index * width for index, name in enumerate(names)}
    for event in events:
        start = columns[event.source]
        end = columns[event.destination]
        left, right = sorted((start, end))
        arrow = ("-" * (right - left - 1)) + (">" if end > start else "<")
        row = [" "] * (max(columns.values()) + width)
        label = f"{event.clock} {event.message}"
        for index, char in enumerate(arrow):
            row[left + index] = char
        rendered = "".join(row).rstrip()
        lines.append(f"{rendered}  {label}")
    return "\n".join(lines)


def report(csv_text: str, sip_text: str) -> str:
    rtp = analyze_rtp(csv_text)
    events = parse_sip(sip_text)
    summary = (
        f"RTP packets: {rtp.received} received / {rtp.expected} expected\n"
        f"Loss: {rtp.loss_pct}%\n"
        f"Jitter: {rtp.jitter_ms} ms\n"
        f"MOS estimate: {rtp.mos}\n"
    )
    return summary + "\n" + call_ladder(events) + "\n"
