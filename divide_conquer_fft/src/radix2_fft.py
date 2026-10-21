"""Recursive radix-2 Cooley–Tukey FFT, standard library only."""
import cmath
import math
from typing import Iterable


def _is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0


def fft(signal: Iterable[complex | float | int]) -> list[complex]:
    """Return the unnormalised forward DFT; input length must be a power of two."""
    x = [complex(value) for value in signal]
    n = len(x)
    if not _is_power_of_two(n):
        raise ValueError("FFT input length must be a positive power of two")
    if n == 1:
        return x
    even = fft(x[0::2])
    odd = fft(x[1::2])
    result = [0j] * n
    half = n // 2
    for k in range(half):
        twiddle = cmath.exp(-2j * math.pi * k / n) * odd[k]
        result[k] = even[k] + twiddle
        result[k + half] = even[k] - twiddle
    return result
