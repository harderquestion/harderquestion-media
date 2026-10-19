"""Synthesize the Harder Questions ambient pad: a quiet A-major drone, low-passed, with slow tremolo and fades.
Usage: python3 pad.py OUT.m4a [seconds] [seed]
Royalty-free by construction (generated here, no samples). Level: about -27 dB mean, -16 dB peak.
"""
import subprocess, sys
out = sys.argv[1]
secs = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 7
fo = secs - 2.5
subprocess.run([
    "ffmpeg", "-y", "-loglevel", "error",
    "-f", "lavfi", "-i", f"sine=frequency=110:duration={secs}:sample_rate=44100",
    "-f", "lavfi", "-i", f"sine=frequency=164.81:duration={secs}:sample_rate=44100",
    "-f", "lavfi", "-i", f"sine=frequency=220.5:duration={secs}:sample_rate=44100",
    "-f", "lavfi", "-i", f"sine=frequency=277.18:duration={secs}:sample_rate=44100",
    "-f", "lavfi", "-i", f"sine=frequency=329.63:duration={secs}:sample_rate=44100",
    "-f", "lavfi", "-i", f"anoisesrc=color=brown:amplitude=0.015:duration={secs}:sample_rate=44100:seed={seed}",
    "-filter_complex",
    "[0]volume=0.5[a0];[1]volume=0.35[a1];[2]volume=0.3,tremolo=f=0.15:d=0.4[a2];"
    "[3]volume=0.22,tremolo=f=0.12:d=0.5[a3];[4]volume=0.12,tremolo=f=0.1:d=0.6[a4];[5]lowpass=f=200[n];"
    "[a0][a1][a2][a3][a4][n]amix=inputs=6:normalize=0,lowpass=f=900,aecho=0.6:0.3:600:0.25,"
    f"volume=0.16,volume=18dB,alimiter=limit=0.3,afade=t=in:d=2.5,afade=t=out:st={fo}:d=2.5[a]",
    "-map", "[a]", "-c:a", "aac", "-b:a", "128k", out], check=True)
