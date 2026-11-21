import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

files = glob.glob("results/raw/openmp_scheduling_*.csv")
df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

# Compare scheduling methods using 4 threads
df = df[df["threads"] == 4]

# Remove duplicate rows if files overlap
df = df.drop_duplicates(
    subset=["matrix_size", "threads", "schedule"]
)

plt.figure(figsize=(12, 6))

for size in sorted(df["matrix_size"].unique()):
    data = df[df["matrix_size"] == size].copy()
    data = data.sort_values("schedule")

    plt.plot(
        data["schedule"],
        data["average_seconds"],
        marker="o",
        label=f"N={size}"
    )

plt.xlabel("OpenMP Scheduling Method")
plt.ylabel("Average Execution Time (seconds)")
plt.title("OpenMP Scheduling Performance (4 Threads)")
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()
plt.tight_layout()

os.makedirs("results/plots", exist_ok=True)
plt.savefig("results/plots/openmp_scheduling.png", dpi=300)
plt.show()
