import subprocess
import re
import csv
import statistics
import os

SIZES = [2048]
THREADS = [1, 2, 4, 6, 8, 12]

SCHEDULES = [
    "static",
    "static,1",
    "static,8",
    "static,16",
    "dynamic,1",
    "dynamic,8",
    "dynamic,16",
    "guided,1",
    "guided,4",
    "guided,8"
]

REPEATS = 5
results = []

def run_program(size, threads, schedule):
    env = os.environ.copy()
    env["OMP_SCHEDULE"] = schedule

    result = subprocess.run(
        ["./openmp", str(size), str(threads)],
        capture_output=True,
        text=True,
        check=True,
        env=env
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
        for schedule in SCHEDULES:

            print(
                f"\nMatrix: {size}, Threads: {threads}, "
                f"Schedule: {schedule}"
            )

            run_program(size, threads, schedule)

            times = []

            for run in range(1, REPEATS + 1):
                elapsed = run_program(size, threads, schedule)
                times.append(elapsed)
                print(f"Run {run}: {elapsed:.6f} seconds")

            average = statistics.mean(times)
            deviation = statistics.stdev(times)

            print(f"Average: {average:.6f} seconds")
            print(f"Std deviation: {deviation:.6f} seconds")

            results.append({
                "implementation": "OpenMP",
                "matrix_size": size,
                "threads": threads,
                "schedule": schedule,
                "average_seconds": average,
                "std_deviation": deviation
            })

os.makedirs("results/raw", exist_ok=True)

with open(
    "results/raw/openmp_scheduling.csv",
    "w",
    newline=""
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=results[0].keys()
    )

    writer.writeheader()
    writer.writerows(results)

print("\nOpenMP benchmarking completed!")
print("Saved: results/raw/openmp_scheduling.csv")

