import csv
import glob

baseline_file = "results/raw/team1_baseline.csv"
output_file = "results/raw/openmp_speedup.csv"

baseline = {}

with open(baseline_file, newline="") as f:
    for row in csv.DictReader(f):
        baseline[int(row["matrix_size"])] = float(row["average_seconds"])

all_results = []

for filename in glob.glob("results/raw/openmp_scheduling_*.csv"):
    with open(filename, newline="") as f:
        all_results.extend(list(csv.DictReader(f)))

best_results = {}

for row in all_results:
    size = int(row["matrix_size"])
    threads = int(row["threads"])
    elapsed = float(row["average_seconds"])
    key = (size, threads)

    if key not in best_results or elapsed < best_results[key]["time"]:
        best_results[key] = {
            "time": elapsed,
            "schedule": row["schedule"]
        }

results = []

for (size, threads), item in sorted(best_results.items()):
    speedup = baseline[size] / item["time"]
    efficiency = speedup / threads * 100

    results.append({
        "matrix_size": size,
        "threads": threads,
        "schedule": item["schedule"],
        "parallel_seconds": item["time"],
        "speedup": speedup,
        "efficiency_percent": efficiency
    })

with open(output_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("OpenMP speedup calculation completed!")
print("Saved:", output_file)

for row in results:
    print(
        f"N={row['matrix_size']}, "
        f"Threads={row['threads']}, "
        f"Schedule={row['schedule']}, "
        f"Speedup={row['speedup']:.3f}, "
        f"Efficiency={row['efficiency_percent']:.2f}%"
    )
