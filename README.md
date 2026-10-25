# COT5405 — Analysis of Algorithms, Project 1

This repository studies two algorithmic techniques through separate application problems:

1. **Greedy:** maximum-cardinality selection of non-overlapping candidate antenna-communication intervals.
2. **Divide and conquer:** radix-2 Cooley–Tukey FFT for frequency analysis of sampled vibration data.

The greedy experiment uses the supplied SatNet request and maintenance files to construct a fixed candidate set for antenna DSS-34. The candidate set is a restricted benchmark model, not a claim to reproduce an operational NASA schedule or solve the full multi-resource DSN problem. The FFT experiment uses a Case Western Reserve University bearing-vibration recording and does not diagnose or classify faults.

## Repository structure

- `aoa_report_starter/report/main.tex` — IEEE conference-style LaTeX report source.
- `aoa_report_starter/report/main.pdf` — compiled report.
- `greedy_dsn/data/` — supplied SatNet request and maintenance inputs.
- `greedy_dsn/src/greedy_satnet.py` — earliest-finish-time scheduler.
- `greedy_dsn/scripts/` — audit, validation, objective comparison, and runtime benchmark scripts.
- `greedy_dsn/tests/` — greedy tests and randomized comparison against dynamic programming.
- `greedy_dsn/results/audit_v2/` — fixed candidate set and audit outputs.
- `greedy_dsn/results/schedule/` — selected schedule and summaries.
- `greedy_dsn/results/runtime/` — greedy benchmark CSV and plots.
- `greedy_dsn/results/objective_comparison/` — cardinality-greedy versus weighted-DP results.
- `divide_conquer_fft/src/radix2_fft.py` — radix-2 FFT implementation.
- `divide_conquer_fft/tests/` — FFT correctness tests.
- `divide_conquer_fft/scripts/` — benchmark and real-data demonstration.
- `divide_conquer_fft/data/105.mat` — CWRU bearing data used by the demonstration.
- `divide_conquer_fft/results/` — FFT runtime data/plot and real-data outputs.
- `docs/` — methodological notes and objective-comparison discussion.

## Requirements

- Python 3.10 or later.
- Matplotlib to regenerate plots.
- SciPy to load the MATLAB `.mat` real-data file.
- LaTeX with the `IEEEtran` class and the packages used by `main.tex` to rebuild the report.

Use a virtual environment and install the dependencies needed for plots and MATLAB data loading:

```bash
python -m pip install matplotlib scipy
```

## Reproduce tests

Run from the repository root:

```bash
python -m unittest discover -s greedy_dsn/tests -p 'test_*.py' -v
python -m unittest discover -s divide_conquer_fft/tests -p 'test_*.py' -v
python greedy_dsn/tests/verify_greedy_optimality.py
```

The randomized verifier checks 1,000 generated instances against a dynamic-programming maximum-cardinality solution. It is an experimental cross-check, not a replacement for the proof in the report.

## Reproduce greedy data audit and schedule

From the repository root:

```bash
python greedy_dsn/scripts/audit_satnet_v2.py \
  --problems greedy_dsn/data/problems.json \
  --maintenance greedy_dsn/data/maintenance.csv \
  --antenna DSS-34 \
  --out greedy_dsn/results/audit_v2

python greedy_dsn/src/greedy_satnet.py \
  --input greedy_dsn/results/audit_v2/candidate_intervals.csv \
  --out greedy_dsn/results/schedule

python greedy_dsn/scripts/compare_objectives.py
python greedy_dsn/scripts/benchmark_greedy_runtime.py \
  --out greedy_dsn/results/runtime
```

The greedy objective is to maximize the number of compatible intervals for a fixed candidate set. It does not maximize total requested communication duration. The weighted interval-scheduling DP in `compare_objectives.py` solves that different objective on the same fixed candidate set only.

## Reproduce FFT experiments

Run from the `divide_conquer_fft` directory:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/benchmark_fft.py --out results --min-power 8 --max-power 15 --repeats 7
python scripts/demo_real_data.py \
  --file data/105.mat --sample-rate 12000 --channel auto \
  --samples 4096 --out results/real_data
python scripts/validate_real_fft.py
```

The independent real-data validation compares the project FFT against NumPy's FFT on the same 4,096-sample segment. It is a numerical cross-check, not a diagnosis.

The benchmark timings depend on machine and interpreter. The FFT's \(\Theta(n\log n)\) bound is established by the recurrence and correctness argument, not by the plot alone.

## Rebuild the report

From the report directory (so all relative figure and source-code paths resolve):

```bash
cd aoa_report_starter/report
latexmk -pdf -interaction=nonstopmode main.tex
```

The report includes source listings for both runtime benchmark scripts. Before submission, the AI-use appendix must be completed with the exact prompt/output history required by the course; the project ZIP did not contain a complete export of prior AI conversations, so that history cannot be honestly reconstructed from this repository alone.

## Limitations and data provenance

The SatNet input files are included with the supplied project data, but their exact upstream provenance was not embedded in the archive. The report therefore treats them as supplied benchmark inputs and cites NASA DSN scheduling literature only for domain context. The FFT demonstration reports spectral peaks only; it does not infer a bearing fault.
