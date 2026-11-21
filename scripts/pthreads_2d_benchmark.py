
import subprocess
import csv
import statistics
import os

SIZES = [512, 1024, 2048]
THREADS = [1, 2, 4, 6, 8, 12]
REPEATS = 5

OUTPUT = "results/raw/pthreads_2d_comparison.csv"

os.makedirs("results/raw", exist_ok=True)

results = []

for n in SIZES:
    for threads in THREADS:

        print(f"\nMatrix: {n}, Threads: {threads}")

        # Warm-up
        subprocess.run(
            ["./pthreads_2d", str(n), str(threads)],
            stdout=subprocess.DEVNULL,
            check=True
        )

        times = []

        for run in range(REPEATS):
            output = subprocess.check_output(
                ["./pthreads_2d", str(n), str(threads)],
                text=True
            )

            execution_time = None

            for line in output.splitlines():
                if "Execution Time:" in line:
                    execution_time = float(
                        line.split(":")[1].strip().split()[0]
                    )

                if "Verification: FAILED" in line:
                    raise RuntimeError("Verification failed!")

            if execution_time is None:
                raise RuntimeError("Execution time not found!")

            times.append(execution_time)
            print(f"Run {run + 1}: {execution_time:.6f} seconds")

        avg = statistics.mean(times)
        std = statistics.stdev(times)

        print(f"Average: {avg:.6f} seconds")
        print(f"Std deviation: {std:.6f} seconds")

        results.append([n, threads, avg, std])

with open(OUTPUT, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Matrix_Size",
        "Threads",
        "Average_Time",
        "Std_Deviation"
    ])
    writer.writerows(results)

print("\nPthreads 2D benchmark completed!")
print(f"Saved: {OUTPUT}")

