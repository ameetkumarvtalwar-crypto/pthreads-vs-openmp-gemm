import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Hardware measurements and estimates
peak_gflops = 281.6
bandwidth_gbps = 18.628
ridge_point = peak_gflops / bandwidth_gbps

# Idealized arithmetic intensity for GEMM
sizes = [512, 1024, 2048]
intensities = [n / 6 for n in sizes]

# Load sequential baseline
baseline = pd.read_csv("results/raw/team1_baseline.csv")

# Load Pthreads measurements
pthreads = pd.read_csv("results/raw/pthreads_official.csv")

plt.figure(figsize=(10, 7))

# Roofline limits
ai = np.logspace(0, 3, 300)
performance_limit = np.minimum(
    bandwidth_gbps * ai,
    peak_gflops
)

plt.loglog(
    ai,
    performance_limit,
    label="Estimated Roofline"
)

# Sequential performance
for _, row in baseline.iterrows():
    n = int(row["matrix_size"])
    time = float(row["average_seconds"])
    gflops = (2 * n**3) / (time * 1e9)

    plt.scatter(
        n / 6,
        gflops,
        marker="o",
        label=f"Sequential N={n}"
    )

# Best Pthreads performance for each size
for n in sizes:
    data = pthreads[pthreads["matrix_size"] == n]
    best = data.loc[data["average_seconds"].idxmin()]

    gflops = (2 * n**3) / (
        float(best["average_seconds"]) * 1e9
    )

    plt.scatter(
        n / 6,
        gflops,
        marker="^",
        label=f"Pthreads N={n}"
    )

plt.axvline(
    ridge_point,
    linestyle="--",
    label=f"Ridge point = {ridge_point:.2f} FLOP/byte"
)

plt.xlabel("Arithmetic Intensity (FLOP/byte)")
plt.ylabel("Performance (GFLOP/s)")
plt.title("GEMM Roofline Model")
plt.grid(True, which="both")
plt.legend(fontsize=8)
plt.tight_layout()

os.makedirs("results/plots", exist_ok=True)
plt.savefig("results/plots/roofline.png", dpi=300)
plt.show()

print("Roofline graph saved successfully.")
