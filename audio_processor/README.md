# Audio Processor

This directory contains various scripts to process audio data using Kafka.

## Librosa Pitch Shift

The `pitch_shift.py` script reads raw audio data from a Kafka topic (default: `raw_audio`), performs pitch shifting using the `librosa` library, and sends the processed audio data to another Kafka topic (default: `librosa_audio`).

### Usage

```bash
python3 pitch_shift.py
```

Back to [main readme](../README.md).

