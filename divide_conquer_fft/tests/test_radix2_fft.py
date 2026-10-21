import cmath
import math
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from radix2_fft import fft


def direct_dft(signal):
    n = len(signal)
    return [sum(complex(signal[j]) * cmath.exp(-2j * math.pi * j * k / n)
                for j in range(n)) for k in range(n)]


class TestRadix2FFT(unittest.TestCase):
    def assertComplexListsAlmostEqual(self, actual, expected, places=8):
        self.assertEqual(len(actual), len(expected))
        for a, e in zip(actual, expected):
            self.assertAlmostEqual(a.real, e.real, places=places)
            self.assertAlmostEqual(a.imag, e.imag, places=places)

    def test_single_sample(self):
        self.assertComplexListsAlmostEqual(fft([7]), [7 + 0j])

    def test_constant_signal(self):
        self.assertComplexListsAlmostEqual(fft([3, 3, 3, 3]), [12, 0, 0, 0])

    def test_impulse_signal(self):
        self.assertComplexListsAlmostEqual(fft([1, 0, 0, 0]), [1, 1, 1, 1])

    def test_known_bin_sinusoid(self):
        n, target = 16, 3
        signal = [math.cos(2 * math.pi * target * i / n) for i in range(n)]
        spectrum = fft(signal)
        self.assertAlmostEqual(abs(spectrum[target]), n / 2, places=8)
        self.assertAlmostEqual(abs(spectrum[n-target]), n / 2, places=8)
        for k, value in enumerate(spectrum):
            if k not in (target, n-target):
                self.assertAlmostEqual(abs(value), 0.0, places=8)

    def test_matches_direct_dft_on_random_inputs(self):
        rng = random.Random(5405)
        for n in (2, 4, 8, 16, 32):
            signal = [complex(rng.uniform(-1, 1), rng.uniform(-1, 1)) for _ in range(n)]
            self.assertComplexListsAlmostEqual(fft(signal), direct_dft(signal))

    def test_rejects_empty_input(self):
        with self.assertRaises(ValueError):
            fft([])

    def test_rejects_non_power_of_two(self):
        for signal in ([1, 2, 3], [1, 2, 3, 4, 5, 6]):
            with self.subTest(signal=signal):
                with self.assertRaises(ValueError):
                    fft(signal)


if __name__ == "__main__":
    unittest.main()
