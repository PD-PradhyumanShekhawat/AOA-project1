# Divide-and-Conquer Component: Bearing Vibration FFT

Implements a radix-2 Cooley–Tukey Fast Fourier Transform (FFT) for spectrum computation on sampled vibration signals. This component does not classify or diagnose bearing faults.

## Run
Python 3.10+; implementation, tests, and benchmark use the standard library. Matplotlib is optional for plots.

```bash
python -m unittest discover -s tests -v
python scripts/benchmark_fft.py --out results
python scripts/demo_signal.py
```

## Mathematical model
For n=2^k, the DFT is X[m] = sum(j=0..n-1) x[j] exp(-2*pi*i*j*m/n).
Split even and odd samples, recursively compute E and O, then combine:
X[m] = E[m] + W_n^m O[m]; X[m+n/2] = E[m] - W_n^m O[m],
where W_n^m = exp(-2*pi*i*m/n), 0 <= m < n/2.
Recurrence T(n)=2T(n/2)+Theta(n), so time is Theta(n log n); this recursive implementation uses Theta(n) auxiliary space.

## Application and limitations
Bearing vibration measurements are sampled in time; FFT transforms them into frequency-domain coefficients that help identify prominent frequency components for further engineering analysis. FFT alone does not establish whether a bearing is faulty or identify a fault type. A real-domain example dataset is the [Case Western Reserve University Bearing Data Center](https://engineering.case.edu/bearingdatacenter).

## References
- J. W. Cooley and J. W. Tukey, “An Algorithm for the Machine Calculation of Complex Fourier Series,” Mathematics of Computation, 19(90), 297–301, 1965. DOI: https://doi.org/10.1090/S0025-5718-1965-0178586-1
- Case Western Reserve University, “Bearing Data Center.” https://engineering.case.edu/bearingdatacenter
