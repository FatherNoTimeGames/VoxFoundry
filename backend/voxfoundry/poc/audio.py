"""Tiny deterministic signal generator. Deliberately NOT text-to-speech."""

import hashlib
import io
import math
import struct
import wave

from voxfoundry.domain.errors import DomainError

SAMPLE_RATE = 16000
FRAMES = SAMPLE_RATE * 2


def test_tone(text_digest: str) -> bytes:
    frequency = 330 + int(text_digest[:4], 16) % 330
    stream = io.BytesIO()
    with wave.open(stream, "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        output.writeframes(
            b"".join(
                struct.pack("<h", int(4000 * math.sin(2 * math.pi * frequency * i / SAMPLE_RATE)))
                for i in range(FRAMES)
            )
        )
    return stream.getvalue()


def verify_audio(content: bytes) -> str:
    try:
        with wave.open(io.BytesIO(content), "rb") as stream:
            if (
                stream.getnchannels(),
                stream.getsampwidth(),
                stream.getframerate(),
                stream.getnframes(),
                stream.getcomptype(),
            ) != (1, 2, SAMPLE_RATE, FRAMES, "NONE"):
                raise ValueError("Unexpected test-audio format")
            if len(stream.readframes(FRAMES)) != FRAMES * 2:
                raise ValueError("Truncated audio")
    except (wave.Error, EOFError, ValueError) as exc:
        raise DomainError("Expected a complete 2-second mono 16 kHz PCM test WAV", 400) from exc
    return hashlib.sha256(content).hexdigest()
