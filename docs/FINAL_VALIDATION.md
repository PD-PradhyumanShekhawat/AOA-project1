# Final Validation Record

Validation was rerun before packaging the Python version of the project.

## Environment

- Python: 3.13.5
- Runtime measurements are environment-dependent; they are evidence from this run, not universal constants.

## Correctness checks

- Greedy/scheduling tests: 13 passed.
- FFT tests: 7 passed.
- Greedy versus dynamic-programming cross-check: 1,000 generated instances matched.
- Real-data FFT cross-check: the project's radix-2 FFT was compared with `numpy.fft.fft` on the first 4,096 mean-centered samples from `divide_conquer_fft/data/105.mat` (`X105_DE_time`). The maximum absolute coefficient error was approximately `1.03456583947e-13`; comparison passed with `rtol=1e-9`, `atol=1e-9`.
- LaTeX report: compiled successfully with `latexmk -pdf -interaction=nonstopmode main.tex` from `aoa_report_starter/report/`.

## Runtime benchmark reproduction

Both benchmark scripts were rerun with seven repetitions per input size. The refreshed CSV files and plots are stored with the project and the report's runtime tables use the median values from this run.

Greedy benchmark command (from repository root):

```bash
python greedy_dsn/scripts/benchmark_greedy_runtime.py --out greedy_dsn/results/runtime --repeats 7
```

FFT benchmark command (from `divide_conquer_fft/`):

```bash
python scripts/benchmark_fft.py --out results --min-power 8 --max-power 15 --repeats 7 --warmups 1
```

The greedy benchmark uses deterministic synthetic interval sets with a fixed seed; the FFT benchmark uses deterministic synthetic signals. A high maximum time for one greedy input size indicates timing variability under system load, so medians are reported and no claim is made that the plot proves asymptotic complexity.

## Scope of conclusions

- The greedy algorithm maximizes the number of non-overlapping intervals in a fixed candidate set for one antenna. It is not a solution to full multi-resource DSN scheduling and does not maximize total communication duration.
- The FFT computes frequency-domain coefficients. Spectrum peaks alone do not diagnose or classify bearing faults.
