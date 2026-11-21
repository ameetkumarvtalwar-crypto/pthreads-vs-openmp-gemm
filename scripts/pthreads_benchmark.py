import subprocess
import re
import csv
import statistics
import os

SIZES = [512, 1024, 2048]
THREADS = [1, 2, 4, 6, 8, 12]
REPEATS = 5

results = []

def run_program(size, threads):

    result = subprocess.run(
        ["./pthreads", str(size), str(threads)],
        capture_output=True,
        text=True,
        check=True
    )

    if "Verification: PASSED" not in result.stdout:
        raise RuntimeError(result.stdout)

    match = re.search(
        r"Execution Time:\s*([\d.]+)",
        result.stdout
    )

    if not match:
        raise RuntimeError(result.stdout)

    return float(match.group(1))


for size in SIZES:

    for threads in THREADS:

        print(f"\nMatrix: {size}, Threads: {threads}")

        run_program(size, threads)

        times = []

        for run in range(1, REPEATS + 1):

            elapsed = run_program(size, threads)

            times.append(elapsed)

            print(f"Run {run}: {elapsed:.6f} seconds")

        average = statistics.mean(times)
        deviation = statistics.stdev(times)

        print(f"Average: {average:.6f} seconds")
        print(f"Std deviation: {deviation:.6f} seconds")

        results.append({
            "implementation": "Pthreads-row",
            "matrix_size": size,
            "threads": threads,
            "average_seconds": average,
            "std_deviation": deviation
        })


os.makedirs("results/raw", exist_ok=True)

with open(
    "results/raw/pthreads_official.csv",
    "w",
    newline=""
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=results[0].keys()
    )

    writer.writeheader()
    writer.writerows(results)

print("\nPthreads benchmarking completed!")
print("Saved: results/raw/pthreads_official.csv")
