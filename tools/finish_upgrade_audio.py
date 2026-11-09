#!/usr/bin/env python3
"""Place the dry render in a small synthetic room. Adds reverberation only, never a noise floor. Usage: finish_upgrade_audio.py in.wav out.wav"""
import sys

import numpy as np
import scipy.signal as sig
import soundfile as sf

WET, DECAY_S, PREDELAY_S, DARK_HZ, SEED = .03, .3, .018, 3500, 7


def main():
    y, sr = sf.read(sys.argv[1], dtype="float64")
    n = int(5 * DECAY_S * sr)
    tail = np.random.default_rng(SEED).normal(0, 1, n) * np.exp(-np.arange(n) / (DECAY_S * sr / 3))
    tail = sig.sosfilt(sig.butter(2, DARK_HZ / (sr / 2), "lowpass", output="sos"), tail)
    tail /= np.sqrt((tail ** 2).sum())
    wet = sig.fftconvolve(y, np.r_[np.zeros(int(PREDELAY_S * sr)), tail])
    out = np.r_[y, np.zeros(len(wet) - len(y))] + WET * wet
    out = out[:len(y) + int(.3 * sr)]
    sf.write(sys.argv[2], out / np.abs(out).max() * .8, sr, subtype="PCM_16")


if __name__ == "__main__":
    main()
