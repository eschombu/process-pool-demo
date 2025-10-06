# Parallelization with Process & Thread Pools

This repo is a lightweight set of utilities and demos showing: (1) the ergonomics of `concurrent.futures` (thread vs process pools), (2) why CPU‑bound work usually needs processes under a GIL build, (3) how a free‑threaded Python build changes that story, and (4) practical patterns for sharing large read‑only NumPy arrays efficiently with multiple workers.


## Dependencies
Minimal scientific stack: `numpy`, progress bars via `tqdm`, and Jupyter for the notebook variants. The `multiprocess` package is listed but the core demos rely on the standard library `multiprocessing` / `concurrent.futures`; `multiprocess` can be experimented with as a drop‑in for alternative serialization behavior.


## Installation

```bash
git clone XXXX  # TODO: replace with actual repo URL
cd process-pools
python3.13 -m venv .venv/py313  # Replace with python3.14t for free-threaded Python installation
source .venv/py313/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```


## Why parallelization strategies differ

- I/O‑bound tasks: Threads work well; time is mostly spent waiting (e.g. sleeping, network, disk). Multiple threads interleave without heavy CPU contention.
- CPU‑bound tasks under the GIL: Threads do not run truly in parallel; only one executes Python bytecode at a time. Use a `ProcessPoolExecutor` / `multiprocessing.Pool` to achieve parallel speedup.
- CPU‑bound tasks under a free‑threaded (nogil) build: Threads *can* run simultaneously, so the simplicity + shared memory advantages of threads become compelling again.
- Large shared read‑only data (e.g. big NumPy arrays): Processes normally copy (or pickle) data to each worker. Use shared memory (`multiprocessing.shared_memory`, or pass indices/metadata only) to avoid large copy overhead.


## Utilities (`utils.py` and `functions.py`)
These small helpers keep demo code concise; each function has its own docstring, so only high‑level purposes are summarized here.

- `timed` (decorator): Wraps a function so it returns `(result, elapsed_seconds)`. Used everywhere to compare per‑task time vs wall clock.
- `submit_get_results`: Submits `n` tasks with `executor.submit`, optionally harvesting results in completion order (`as_completed=True`) vs submission order. Shows difference between streaming early results and waiting for all tasks.
- `map_results`: Uses `executor.map` to apply a timed function across a simple integer range. Demonstrates the simpler API and ordered results guarantee.
- `display_results`: Convenience wrapper that runs one of the above, prints task results, individual runtimes (sum of per‑task time), and the actual elapsed wall time for the batch (demonstrating parallel speedup / lack thereof).
- `delayed_return` (in `functions.py`): Simulates an I/O‑bound (or latency‑bound) task by sleeping for a random or fixed duration then returning a value. Good for illustrating near‑ideal thread scaling when tasks mostly sleep.
- `long_factorize` (in `functions.py`): Intentionally inefficient integer factorization to create a clearly CPU‑bound workload for demonstrating: threads (with GIL) ≈ serial time, processes ≫ faster, threads (free‑threaded build) regain parallel speedup.


## Demos
The notebooks / scripts are grouped into two themes: (1) basic executor behavior and (2) sharing large data for graph computations.

The `*_freethreaded.ipynb` variants should be run with a python3.14t kernel.

### Demo 1 (notebook variants `demo_1*.ipynb`)
Focus: Comparing submission styles (`submit` vs `map`), result ordering (`as_completed`), and thread vs process behavior for I/O‑ vs CPU‑bound tasks.

Key ideas across variants:
- Sum of individual task runtimes (serial cost) vs actual wall time (parallel cost) clarifies effective speedup.
- Threads excel on `delayed_return` (I/O‑like) even with the GIL, because sleeping releases the GIL.
- Threads fail to speed up `long_factorize` under a GIL build; processes do.
- `as_completed` lets you act on fast‑finishing tasks early (helpful when durations are variable).

Variant highlights:
- `demo_1.ipynb`: Introduces timing utilities, runs both `delayed_return` and `long_factorize` with thread and process pools, compares `submit` vs `map`.
- `demo_1b.ipynb`: Emphasizes collecting results with `as_completed` and observing non‑deterministic completion ordering when task durations vary.
- `demo_1c.ipynb`: Focuses on CPU‑bound factorization to highlight lack of thread speedup under the GIL and clear process pool benefit as worker count increases.
- `demo_1d_freethreaded.ipynb`: Repeats CPU‑bound tests under a free‑threaded Python build showing that threads now scale similarly to processes while retaining simple shared memory (no pickling / copy of Python objects needed for communication). Demonstrates why free‑threaded builds reduce the motivation for process pools for pure Python CPU tasks.

Take‑aways from Demo 1:
- Pick a thread pool for latency / I/O bound tasks in standard CPython.
- Pick a process pool for CPU bound tasks on GIL builds.
- Free‑threaded Python narrows this distinction; threads can be both simpler (shared memory) and fast for CPU tasks.
- Use `as_completed` when you want to stream / pipeline partial results; use `map` or ordered `submit` collection when order matters more than latency.

### Demo 2 (graph path distances; notebooks `demo_2.ipynb`, `demo_2_freethreaded.ipynb`)
Focus: A toy workload computing short path (hop-limited) distances over a sparse adjacency matrix, exploring how to share large data efficiently across workers and how the approach differs between GIL and free‑threaded builds.

Core components (shown in `demo_2.ipynb`):
- Generate a sparse `M x M` NumPy adjacency matrix (`uint8`) with a configurable connection fraction.
- Compute distances for many (i, j) node pairs up to a max hop using repeated vector–matrix products.
- Baseline: naive process pool where the adjacency matrix would otherwise be pickled (highlighting overhead concerns).
- Optimization: place the adjacency matrix in shared memory (`SharedMemoryManager` + creating a single backing block) and have each worker attach; introduce a variant function (`path_distance_shm`) that reads from shared memory.

Free‑threaded variant (`demo_2_freethreaded.ipynb`):
- Runs the same conceptual workload using a `ThreadPoolExecutor` under a free‑threaded Python build.
- No explicit shared memory boilerplate required—threads naturally share the NumPy array.
- Code is shorter: the path distance function just receives the in‑memory array reference plus (i, j) pairs.
- Demonstrates improved speedups without inter‑process communication complexity.

Take‑aways from Demo 2:
- Large read‑only arrays: with processes, use shared memory to avoid repeated serialization; with threads (free‑threaded) you can skip this.
- `SharedMemoryManager` simplifies lifecycle management vs manual create/close/unlink logic.
- A free‑threaded build turns an IPC problem into a straightforward in‑memory parallel map.


## Summary
These demos illustrate practical patterns rather than micro‑optimized benchmarks. The key is matching the parallelization tool to your workload characteristics and runtime (GIL vs free‑threaded). Threads become much more attractive for CPU work once the GIL is gone, primarily because data sharing becomes trivial.
