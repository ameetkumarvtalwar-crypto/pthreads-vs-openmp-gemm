import csv

baseline_file = "results/raw/team1_baseline.csv"
pthreads_file = "results/raw/pthreads_official.csv"
output_file = "results/raw/pthreads_speedup.csv"

baseline = {}

with open(baseline_file, newline="") as f:
    for row in csv.DictReader(f):
        baseline[int(row["matrix_size"])] = float(row["average_seconds"])

results = []

with open(pthreads_file, newline="") as f:
    for row in csv.DictReader(f):
        size = int(row["matrix_size"])
        threads = int(row["threads"])
        parallel_time = float(row["average_seconds"])

        sequential_time = baseline[size]
        speedup = sequential_time / parallel_time
        efficiency = (speedup / threads) * 100

        results.append({
            "matrix_size": size,
            "threads": threads,
            "sequential_seconds": sequential_time,
            "parallel_seconds": parallel_time,
            "speedup": speedup,
            "efficiency_percent": efficiency
        })

with open(output_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("Speedup and efficiency calculated successfully!")
print("Saved to:", output_file)

for row in results:
    print(
        f"N={row['matrix_size']}, "
        f"Threads={row['threads']}, "
        f"Speedup={row['speedup']:.3f}, "
        f"Efficiency={row['efficiency_percent']:.2f}%"
    )
