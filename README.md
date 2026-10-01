# callquality

Score one sample call. A SIP text trace becomes a call ladder. An RTP CSV becomes loss, jitter, and a lab MOS estimate. Nothing is captured from a live network.

The sample trace drops sequence 4 and delivers packet 3 five milliseconds late.

## Run

```bash
cd callquality
PYTHONPATH=src python3 -m callquality fixtures/rtp.csv fixtures/sip.txt
```

RTP columns are `seq,timestamp_ms,bytes`. The packet period is 20 ms. Jitter is the average gap, beyond that 20 ms, between packets whose sequence numbers are consecutive. The MOS figure is an E-model style estimate for the demo, not a certified score.

SIP lines look like:

```
10:00:00.000 Caller -> PBX INVITE sip:alice@pbx.lab
```

## Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```
