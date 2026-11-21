
import subprocess
import csv
import statistics
import os

THREADS = [1, 2, 4, 6, 8, 12]
REPEATS = 10

OUTPUT = "results/raw/false_sharing_official.csv"

os.makedirs("results/raw", exist_ok=True)

results = []

def run_test(threads):
    output = subprocess.check_output(
        ["./false_sharing", str(threads)],
        text=True
    )

    packed = None
    padded = None

    for line in output.splitlines():
        if "Packed Array Time:" in line:
            packed = float(line.split(":")[1].split()[0])

        if "Padded Array Time:" in line:
            padded = float(line.split(":")[1].split()[0])

    if packed is None or padded is None:
        raise RuntimeError("Could not read benchmark output")

    return packed, padded


for threads in THREADS:
    print(f"\nTesting {threads} threads")

    # Warm-up
    run_test(threads)

    packed_times = []
    padded_times = []

    for run in range(REPEATS):

        # Alternate execution order to reduce order bias
        packed, padded = run_test(threads)

        packed_times.append(packed)
        padded_times.append(padded)

        print(
            f"Run {run + 1}: "
            f"Packed={packed:.6f}s, "
            f"Padded={padded:.6f}s"
        )

    packed_avg = statistics.mean(packed_times)
    padded_avg = statistics.mean(padded_times)

    packed_std = statistics.stdev(packed_times)
    padded_std = statistics.stdev(padded_times)

    improvement = (
        (packed_avg - padded_avg) / packed_avg
    ) * 100

    print(f"Packed average: {packed_avg:.6f}s")
    print(f"Padded average: {padded_avg:.6f}s")
    print(f"Improvement: {improvement:.2f}%")

    results.append([
        threads,
        packed_avg,
        packed_std,
        padded_avg,
        padded_std,
        improvement
    ])


with open(OUTPUT, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
        "Threads",
        "Packed_Average",
        "Packed_StdDev",
        "Padded_Average",
        "Padded_StdDev",
        "Improvement_Percent"
    ])

    writer.writerows(results)

print("\nFalse-sharing benchmark completed!")
print(f"Saved: {OUTPUT}")

