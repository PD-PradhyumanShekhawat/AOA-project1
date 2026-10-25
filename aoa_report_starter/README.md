# Report source and build

`report/main.tex` is the IEEE conference-style LaTeX report for Project 1.

## Build

Build from this directory so the relative paths to project plots and benchmark source files resolve:

```bash
latexmk -pdf -interaction=nonstopmode main.tex
```

The report references source files and figures under `../../greedy_dsn/` and `../../divide_conquer_fft/`.

## Submission checks

- The FFT runtime table is taken from `divide_conquer_fft/results/fft_runtime.csv`.
- The greedy runtime table is taken from `greedy_dsn/results/runtime/runtime_results.csv`.
- Runtime validation source code is included in the report appendix using `\\lstinputlisting`.
- The supplied SatNet inputs are described as project-provided benchmark files; no claim is made that they are raw operational NASA schedules.
- The report includes a transparent note that the ZIP did not contain the complete historical AI prompt/output export. The exact conversation log required by the course must be attached before submission; it must not be fabricated or reconstructed as if verbatim.
