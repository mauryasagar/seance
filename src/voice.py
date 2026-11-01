import io
import os
import wave
import numpy as np
import requests
from dotenv import load_dotenv

load_dotenv()
VOICE_ID = "N2lVS1w4EtoT3dr4eOWO"  # Callum, built-in voice
RATE = 22050

def haunt(pcm):
    x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    rate = int(RATE * 0.9)  # one voice, slightly deeper and slower
    n = len(x)
    rng = np.random.default_rng(1)
    m = int(1.6 * rate)
    ir = rng.standard_normal(m) * np.exp(-np.arange(m) / (0.4 * rate))
    size = 1 << int(np.ceil(np.log2(n + m)))
    wet = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: n + m]
    wet /= np.abs(wet).max() + 1e-9
    dry = np.pad(x, (0, m))
    dry /= np.abs(dry).max() + 1e-9
    out = 0.75 * dry + 0.4 * wet
    t = np.arange(len(out)) / rate
    drone = (np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 82.5 * t)) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.15 * t))
    out = out + 0.05 * drone
    out = out / np.abs(out).max() * 0.9
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes((out * 32767).astype(np.int16).tobytes())
    return buf.getvalue()

def speak(text):
    key = os.getenv("ELEVEN_API_KEY")
    if not key:
        return None, "No ELEVEN_API_KEY found in .env"
    try:
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format=pcm_22050",
            headers={"xi-api-key": key, "Content-Type": "application/json"},
            json={"text": "[whispers] " + text.replace(". ", "... [sighs] "),
                  "model_id": "eleven_v3",
                  "voice_settings": {"stability": 0.0}},
            timeout=60)
        if r.status_code != 200:
            return None, f"ElevenLabs error {r.status_code}: {r.text[:150]}"
        return haunt(r.content), None
    except Exception as e:
        return None, f"Voice problem: {e}"