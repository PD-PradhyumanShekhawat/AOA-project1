# AI Usage Log

## 1. AI Tool and Purpose

- **Tool:** ChatGPT by OpenAI
- **Model:** GPT-6 was used during the current documentation and review session. The model versions used in earlier sessions were not consistently recorded.
- **Purpose:** I used ChatGPT for research assistance, algorithmic explanations, evaluation of mathematical formulations, implementation support, test development, performance-analysis discussions, and review of the LaTeX report.

I reviewed the proposed approaches against the course requirements and refined the problem formulations, implementation scope, and documentation throughout the project. I am responsible for the final mathematical arguments, source code, experimental results, references, and submitted report.

## 2. Problem Research and Selection

I evaluated candidate problems from aerospace engineering and other application domains against the project rubric. The main criteria were whether the application represented a legitimate real-world problem, whether it could be expressed as a precise mathematical model, whether the required algorithm had a defensible correctness argument, and whether implementation and runtime experiments were feasible.

### Prompt 1: Research and evaluate candidate problems

**Exact prompt:**

> I don't mind going with your recommendation but the condition is it shouldn't be some vague approach. It should be a legit problem and I should be able to find a solution to the problem(I hope you know what i mean; the project description). The professor also said that I couldn't blame the AI if something goes sideways. So I want you to do the research(deep research), and then we should decide if we should go for the recommendation

**AI response and outcome:**

The research discussion distinguished documented application problems from simplified mathematical models inspired by real applications. It examined satellite observation scheduling, the classical closest-pair problem, and the limitations of applying planar geometry directly to astronomical coordinates.

The discussion proposed two candidate formulations:

- Selecting the maximum number of non-overlapping satellite observation opportunities from a fixed set of intervals using an earliest-finish-time greedy algorithm.
- Finding the closest pair of aircraft positions in a local Cartesian coordinate system using divide and conquer.

The analysis emphasized that the proposed algorithms should not be presented as solutions to complete operational systems when their mathematical models exclude important real-world constraints.

**Refinement and decision:**

I continued evaluating the candidate problems and their suitability for the assignment. The final working pair became satellite communication scheduling for the greedy component and bearing-vibration frequency analysis using the Fast Fourier Transform (FFT) for the divide-and-conquer component.

The final formulations were restricted to problems with clearly defined inputs, objectives, assumptions, and algorithmic guarantees.

## 3. Project Requirements and Execution Plan

### Prompt 2: Establish the project requirements and workflow

**Exact prompt:**

> # COT5405 Analysis of Algorithms — Project Research & Implementation Coach
>
> I am pursuing an M.Sc. in Computer Science at the University of Florida. I have completed Assignment 1 for COT5405 (Analysis of Algorithms) and now need to complete the course project.
>
> Act as my algorithm-design tutor, research assistant, project supervisor, and implementation partner. Help me select suitable problems, design and prove algorithms, implement them, conduct experiments, and produce a professional research-style report.
>
> I want to work through the project with you step by step. Do not jump directly into writing code or a report.
>
> ## 1. My Background and Interests
>
> - Bachelor's in Mechanical Engineering.
> - Master's in Space Engineering.
> - Currently pursuing a Master's in Computer Science at the University of Florida.
> - Interested in aerospace, space systems, NASA, ESA, and scientific/engineering applications.
> - Completed an earlier assignment involving graph algorithms in C++.
>
> I would prefer to apply algorithms to a meaningful real-world problem in the space or aerospace sector if a suitable problem exists. Potential sources include NASA datasets, ESA resources, scientific papers, open-source projects, and other credible technical sources.
>
> However, do not force an aerospace application if it does not fit the assignment requirements. Recommend another domain if it provides a clearer problem, stronger algorithmic justification, and more convincing experimental results.
>
> ## 2. The Professor's Requirements — Source of Truth
>
> The project contains two independent problem-solving components:
>
> **Problem A: Greedy algorithm — 50 points**
>
> **Problem B: Divide-and-conquer algorithm — 50 points**
>
> For EACH component, we must:
>
> 1. Identify a real application-domain problem (10 points). The problem cannot be sourced from the study of algorithms itself, but may come from computer science or another field.
> 2. Abstract the real problem into a mathematical/computational model using sets, trees, graphs, or similar structures (5 points).
> 3. Provide a solution containing:
>    - Algorithm (10 points)
>    - Running-time analysis (5 points)
>    - Proof of correctness (10 points)
> 4. Explain the algorithm in the language of the original application domain (5 points).
> 5. Implement the algorithm and experimentally validate its running-time analysis, including graphs showing the observed behavior (5 points).
>
> ### Mandatory submission rules
>
> - This is a group project for a maximum of two students.
> - The report must use LaTeX, not Word.
> - Follow the structure of a publishable conference or journal article, using an appropriate ACM or IEEE template.
> - Cite all external resources using LaTeX bibliography/citation tools.
> - Include an appendix documenting AI tools used, exact prompts, outputs/results, and the refinement process.
> - Include the code used to validate the running-time analysis in an appendix.
> - We are responsible for the correctness of all proofs, claims, code, and experimental results.
>
> Treat these requirements as the project's governing specification. Do not silently omit or weaken any of them. If any later instructions conflict with these requirements, identify the conflict and ask me how to proceed.
>
> ## 3. First Task: Find Suitable Problems
>
> Before implementing anything, research and propose approximately 5–8 candidate problems.
>
> Explore applications in:
>
> - Space mission planning and spacecraft operations
> - Satellite observation and scheduling
> - Spacecraft trajectories or scientific data processing
> - NASA/ESA scientific datasets
> - Aerospace engineering and simulation
> - Networks, logistics, resource allocation, and scheduling
> - Other suitable real-world application domains
>
> For each candidate, specify:
>
> - Real-world problem and application domain
> - Credible source or reference
> - Why the problem matters
> - Whether it is suitable for greedy or divide and conquer
> - Mathematical abstraction
> - Proposed algorithm and why it fits
> - Whether optimality can be proved
> - Available data or a feasible way to generate test data
> - Implementation difficulty
> - Experimental running-time evaluation plan
> - Major risks or limitations
>
> Use current, reliable sources and cite them. Prefer official datasets, research papers, and authoritative technical documentation.
>
> Distinguish between an actual documented application problem and a hypothetical application inspired by a real domain.
>
> ## 4. Choose Problems That Satisfy the Mathematics
>
> The choice of algorithm must be justified by the problem, not merely attached to it afterward.
>
> ### Greedy component
>
> Identify a problem for which a greedy algorithm can be shown to produce an optimal solution under clearly stated assumptions.
>
> Explain:
>
> - The greedy choice
> - Why the choice is locally optimal
> - Why it leads to a globally optimal solution
> - The conditions under which the proof holds
> - The computational model and complexity
>
> Do not label a heuristic as optimal unless that claim is proved.
>
> ### Divide-and-conquer component
>
> Identify a problem that can genuinely be solved using divide and conquer.
>
> Explain:
>
> - How the input is divided
> - What each recursive subproblem solves
> - How subproblem solutions are combined
> - The recurrence relation
> - The resulting running-time bound
> - Why the algorithm returns a correct solution
>
> Do not simply use recursion and call it divide and conquer. The decomposition and combination steps must be justified.
>
> The two problems should be sufficiently distinct and substantial for a graduate-level algorithms project.
>
> ## 5. Research and Selection
>
> After presenting the candidates, recommend a shortlist of the best two or three combinations.
>
> Evaluate each combination based on:
>
> - Fit with the rubric
> - Strength of correctness proofs
> - Technical depth
> - Availability of credible references
> - Feasibility within the project deadline
> - Implementation effort
> - Quality of experimental evaluation
> - Suitability for a professional research-style report
> - Opportunity to connect my aerospace background with computer science
>
> Explain the trade-offs and make a reasoned recommendation.
>
> Do not select problems merely because their titles sound impressive.
>
> Before we commit, identify any uncertainty about whether the professor would accept the proposed application or abstraction.
>
> ## 6. Project Execution Plan
>
> Once we choose the problems, guide me through these stages:
>
> 1. **Problem definition:** establish the real-world motivation, scope, assumptions, and objectives.
> 2. **Literature and source review:** identify credible references and existing approaches.
> 3. **Mathematical abstraction:** define inputs, outputs, constraints, and the computational model.
> 4. **Algorithm design:** explain the approach, pseudocode, and design rationale.
> 5. **Correctness proof:** construct a rigorous proof appropriate for a graduate algorithms course.
> 6. **Complexity analysis:** derive the time and space bounds step by step.
> 7. **Implementation:** write modular, testable code.
> 8. **Correctness testing:** use edge cases and independent checks where possible.
> 9. **Experimental design:** select input sizes, datasets, repetitions, and measurement methods.
> 10. **Performance evaluation:** record actual runtime, plot the results, and compare observations with theoretical bounds.
> 11. **Application-domain interpretation:** explain what the algorithm's result means in the real-world problem.
> 12. **LaTeX report:** prepare a professional research-style report.
> 13. **Final audit:** verify every rubric requirement, citation, proof, figure, code file, and appendix.
>
> For each stage, tell me the objective, expected output, and conditions for considering it complete. Do not move forward while a critical correctness issue remains unresolved.
>
> ## 7. Implementation and Experimental Analysis
>
> Use a suitable compiled language such as C++ where appropriate, unless the selected problem makes another language materially more suitable.
>
> Keep the implementation understandable and reproducible.
>
> For experiments:
>
> - Use multiple input sizes.
> - Record input size and relevant input characteristics.
> - Measure runtime using a consistent methodology.
> - Repeat runs when necessary to reduce measurement noise.
> - Explain hardware/software conditions where relevant.
> - Plot measured runtime against input size.
> - Compare the observed growth with the theoretical complexity.
> - Include the code used to run the experiments.
> - Report actual measurements only; never fabricate results.
> - Explain discrepancies between theory and practice.
>
> Use real datasets when they add value, but do not assume that a large external dataset is necessary. Controlled synthetic data may be appropriate for complexity experiments if its construction and limitations are documented.
>
> ## 8. LaTeX Report
>
> Help me produce a concise, professional paper using an appropriate ACM or IEEE template.
>
> A possible structure is:
>
> - Title and abstract
> - Introduction and motivation
> - Related work and sources
> - Problem formulation
> - Mathematical abstraction
> - Algorithm design
> - Correctness proof
> - Complexity analysis
> - Implementation and experimental methodology
> - Results and discussion
> - Application-domain interpretation
> - Limitations
> - Conclusion
> - References
> - Appendices: experimental code and AI usage record
>
> Adapt this structure to the selected problems and the professor's requirements.
>
> Use proper mathematical notation, numbered equations where useful, clearly labeled figures/tables, and a real bibliography. Do not invent references, experimental findings, or claims.
>
> ## 9. AI Usage Documentation
>
> Maintain an accurate record throughout the project of:
>
> - AI tool/model used
> - Exact prompts submitted
> - Relevant outputs/results
> - Changes made after reviewing those outputs
> - How factual claims, code, proofs, and experimental results were verified
>
> The professor requires AI prompts and intermediate outputs to be included. Therefore, do not wait until the end to reconstruct this information from memory.
>
> Help me organize it into an appendix that accurately documents our process. Do not claim independent verification unless we actually performed it.
>
> ## 10. How We Should Work Together
>
> - Explain concepts before expecting me to implement them.
> - Use concise explanations, diagrams, examples, and pseudocode where helpful.
> - Challenge weak problem formulations and incorrect assumptions.
> - Separate established facts, mathematical deductions, design decisions, and experimental observations.
> - Do not write a long report before the algorithms and experiments are validated.
> - Do not introduce unnecessary complexity or irrelevant material.
> - Keep a checklist of requirements and completed deliverables.
> - Ask questions only when the answer materially affects the project.
> - If a simpler problem produces a stronger proof and cleaner experimental analysis, prefer it over an unnecessarily ambitious problem.
>
> ## Start Here
>
> First, briefly explain what the professor expects us to accomplish and what distinguishes the greedy component from the divide-and-conquer component.
>
> Then research 5–8 candidate real-world problems, including suitable aerospace/space applications where available.
>
> Recommend the strongest candidate combinations, explain their mathematical and practical suitability, and give me a step-by-step execution plan.
>
> **Do not start coding yet.** We will choose the problems first, confirm the formulations, and then develop the solutions together.

**AI response and outcome:**

The project requirements were organized into a workflow covering research, mathematical modeling, algorithm design, correctness proofs, complexity analysis, implementation, testing, benchmarking, report preparation, and final review. The workflow also emphasized separating established application facts from simplified models and avoiding unsupported claims of optimality.

**Refinement:**

I used the assignment rubric to evaluate the problem formulations and retained the requirement that each algorithm's correctness claim must apply to the precise mathematical model stated in the report.

## 4. Greedy Component: Satellite Communication Scheduling

The greedy component was developed around a restricted interval-scheduling problem inspired by satellite communication operations.

The mathematical model uses a fixed set of candidate intervals. Each interval has a start time and finish time. The objective is to select the maximum number of pairwise non-overlapping intervals, assuming equal value for every interval and a single scheduling resource.

The selected algorithm sorts intervals by increasing finish time and selects each compatible interval in that order.

### Development and refinement

AI assistance was used to discuss the candidate data, interval construction, algorithm implementation, testing, and report formulation. The model was narrowed to a fixed set of candidate intervals so that the earliest-finish-time algorithm's optimality could be proved under clearly stated assumptions.

The final scope does not claim to solve the complete DSN scheduling problem or account for every operational constraint, such as pointing transitions, thermal limits, resource conflicts, or differing scientific priorities.

### Recorded implementation results

The project progress record reported:

- 874 candidate requests and 119 selected intervals in a scheduler run.
- Ten greedy-related unit tests.
- Comparison against a dynamic-programming solution on 1,000 randomly generated instances.
- Synthetic runtime experiments and plots.

These are development-record results. They should be treated as final experimental claims only when the corresponding code, raw output, and benchmark artifacts support them.

## 5. Divide-and-Conquer Component: Bearing-Vibration Frequency Analysis

The second component uses the radix-2 Cooley–Tukey Fast Fourier Transform (FFT) to compute the discrete Fourier transform of sampled vibration signals.

The application context is bearing-vibration analysis using measurements from the Case Western Reserve University (CWRU) Bearing Data Center. The algorithm divides the input into even-indexed and odd-indexed samples, recursively transforms both subsequences, and combines the resulting spectra.

The problem was deliberately restricted to computing the frequency spectrum. It does not include a machine-learning classifier or claim that the FFT alone diagnoses a particular bearing fault.

### Prompt: Define the FFT problem before implementation

The retained project history records the following instruction and response sequence:

> sure. let's proceed

**AI response and outcome:**

A mathematical formulation was established for an input sequence

$$
x = \bigl(x[0], x[1], \ldots, x[n-1]\bigr),
\qquad n = 2^k.
$$

The goal is to compute its discrete Fourier transform (DFT):

$$
\boxed{
X[m] = \sum_{j=0}^{n-1} x[j],e^{-2\pi i jm/n}
}
$$

The divide-and-conquer approach splits the input into even-indexed and odd-indexed subsequences. Their Fourier transforms are computed recursively and combined using the following equations:

$$
\begin{aligned}
X[m] &= E[m] + W_n^m O[m],\
X\left[m+\frac{n}{2}\right] &= E[m] - W_n^m O[m],
\end{aligned}\\
\qquad 0 \le m < \frac{n}{2},
$$

where

$$
W_n^m = e^{-2\pi i m/n}.
$$

This decomposition leads to the recurrence relation

$$
\boxed{
T(n) = 2T\left(\frac{n}{2}\right) + \Theta(n)
}
$$

Applying the Master Theorem gives the time complexity

$$
\boxed{
T(n) = \Theta(n\log n).
}
$$

The proposed validation plan included comparing the implementation with a direct DFT on small inputs, testing known-frequency signals, benchmarking increasing input sizes, and evaluating real bearing measurements separately from synthetic runtime inputs.

**Refinement:**

I retained the frequency-spectrum computation as the algorithmic objective and kept fault classification outside the project's scope. This keeps the implementation, correctness proof, and complexity analysis aligned with the stated problem.

### Recorded implementation results

The retained project progress record reported:

- Seven FFT tests.
- Recovery of synthetic signal frequencies of 64 Hz, 180 Hz, and 230 Hz.
- Runtime experiments with input sizes from 256 to 32,768 samples and seven repetitions.

These figures must be checked against the final code and saved experimental output before submission.


## 6. Report Review and Final Audit

ChatGPT was used to review the report and implementation against the assignment rubric, focusing on correctness proofs, reproducibility, runtime analysis, citations, and consistency between reported results and the project files.

### Prompt 1: Review the project against the assignment

**Exact prompt:**

> Act as if you are the student(act as if this is your project) and then read the project description and check the zip against those requirements.

**AI response and outcome:**

The review identified report and submission items requiring attention, including the IEEE/ACM template, source citations, benchmark code in the report appendix, reproducibility instructions, and AI-use documentation.

**Refinement:**

I used the review to organize the remaining submission work around the professor's stated requirements.

### Prompt 2: Check proofs, reproducibility, and report-to-code consistency

**Exact prompt:**

> Check the following:
>
> 1. Correctness proofs: verify that the report contains a valid proof for each algorithm, not just a complexity explanation or test results.
> 2. Reproducibility: make sure the documented commands work from the stated directory without undocumented environment setup.
> 3. Full report-to-code consistency: verify the reported results, tables, figures, citations, and data descriptions against the actual files.

**AI response and outcome:**

The review focused on the greedy exchange argument, the FFT even/odd decomposition, test execution, benchmark values, figures, and citations. The retained audit record noted changes to the standalone greedy verifier's import path, a weighted-objective counterexample test, and the use of the IEEE conference class for the report.

**Refinement and verification:**

The audit findings were treated as items to resolve against the actual implementation and report. The existence of an AI-generated review is not, by itself, proof that every item was independently verified.

## 7. Verification and Responsibility

AI assistance supported planning, explanations, implementation discussions, testing, and report review. The final submission must be supported by the actual project artifacts.

Before submission, I will ensure that:

1. The application descriptions and data claims are supported by the cited sources.
2. The greedy proof applies to the fixed-interval, equal-value scheduling model.
3. The FFT proof establishes that the recursive algorithm computes the defined DFT.
4. The stated time and space complexities follow from the algorithms and their implementations.
5. Test results can be reproduced from the final source code.
6. Runtime tables and plots correspond to the included benchmark code and recorded measurements.
7. The bibliography, report, code, figures, and experimental data are consistent.
8. The final report follows the instructor's AI-disclosure requirements.

The reported counts and measurements in this log are retained project-progress records. They should not replace reproducible test output or raw benchmark data. I am responsible for reviewing the final work and ensuring that every submitted claim is supported.