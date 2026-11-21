import subprocess
import os
import re
import csv
import statistics

N = 512
THREADS = 4
REPEATS = 5

schedules = [
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

os.makedirs("results/raw", exist_ok=True)

output = "results/raw/scheduling_comparison.csv"

results = []

def run_test(schedule):

    env = os.environ.copy()
    env["OMP_SCHEDULE"] = schedule

    result = subprocess.run(
        ["./openmp", str(N), str(THREADS)],
        capture_output=True,
        text=True,
        env=env,
        check=True
    )

    if "Verification: PASSED" not in result.stdout:
        raise RuntimeError("Verification failed")

    match = re.search(
        r"Execution Time:\s*([\d.]+)",
        result.stdout
    )

    if not match:
        raise RuntimeError(result.stdout)

    return float(match.group(1))


for schedule in schedules:

    print("\nTesting:", schedule)

    # Warm-up
    run_test(schedule)

    times = []

    for run in range(1, REPEATS + 1):

        elapsed = run_test(schedule)
        times.append(elapsed)

        print(f"Run {run}: {elapsed:.6f} seconds")

    average = statistics.mean(times)
    deviation = statistics.stdev(times)

    results.append({
        "schedule": schedule,
        "threads": THREADS,
        "matrix_size": N,
        "average_seconds": average,
        "std_deviation": deviation
    })

    print(f"Average: {average:.6f} seconds")
    print(f"Std deviation: {deviation:.6f} seconds")


with open(output, "w", newline="") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=results[0].keys()
    )

    writer.writeheader()
    writer.writerows(results)


print("\nScheduling experiment completed!")
print("Saved:", output)
