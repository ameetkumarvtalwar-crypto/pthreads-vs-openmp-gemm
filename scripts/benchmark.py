import subprocess
import re
import csv
import sys
import os
import statistics

MATRIX_SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 512

THREADS = [1, 2, 4, 6, 8, 12]
REPEATS = 5

OUTPUT = f"results/raw/benchmark_{MATRIX_SIZE}.csv"

columns = [
    "cluster", "problem", "platform", "implementation",
    "dataset", "size", "threads_or_ranks", "run_id",
    "total_ms", "kernel_ms", "transfer_ms",
    "throughput", "error", "power_w"
]

os.makedirs("results/raw", exist_ok=True)


def run_program(command, environment=None):

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=environment,
        check=True
    )

    match = re.search(
        r"Execution Time:\s*([\d.]+)",
        result.stdout
    )

    if not match:
        raise RuntimeError(result.stdout + result.stderr)

    if "Verification: PASSED" not in result.stdout:
        raise RuntimeError("Result verification failed")

    return float(match.group(1))


def benchmark(name, command, threads, environment=None):

    print(f"\nTesting {name}, threads={threads}")

    # Warm-up run (discarded)
    run_program(command, environment)

    times = []

    for run in range(1, REPEATS + 1):

        elapsed = run_program(command, environment)
        times.append(elapsed)

        print(f"Run {run}: {elapsed:.6f} seconds")

        throughput = (
            (2 * MATRIX_SIZE**3) / elapsed
        ) / 1e9

        with open(OUTPUT, "a", newline="") as file:

            writer = csv.DictWriter(file, fieldnames=columns)

            writer.writerow({
                "cluster": "A",
                "problem": "Pthreads_vs_OpenMP_GEMM",
                "platform": "WSL2 Ubuntu 24.04",
                "implementation": name,
                "dataset": "constant_A1_B2",
                "size": MATRIX_SIZE,
                "threads_or_ranks": threads,
                "run_id": run,
                "total_ms": elapsed * 1000,
                "kernel_ms": "",
                "transfer_ms": 0,
                "throughput": throughput,
                "error": 0,
                "power_w": ""
            })

    average = statistics.mean(times)
    deviation = statistics.stdev(times)

    print(f"Average: {average:.6f} seconds")
    print(f"Std deviation: {deviation:.6f} seconds")


# Create CSV header
with open(OUTPUT, "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()


# Sequential benchmark
benchmark(
    "Sequential",
    ["./sequential", str(MATRIX_SIZE)],
    1
)


# Pthreads benchmarks
for threads in THREADS:

    benchmark(
        "Pthreads",
        ["./pthreads", str(MATRIX_SIZE), str(threads)],
        threads
    )


# OpenMP static scheduling benchmarks
for threads in THREADS:

    env = os.environ.copy()
    env["OMP_SCHEDULE"] = "static"

    benchmark(
        "OpenMP-static",
        ["./openmp", str(MATRIX_SIZE), str(threads)],
        threads,
        env
    )


print("\nBenchmark completed!")
print("Results saved to:", OUTPUT)
