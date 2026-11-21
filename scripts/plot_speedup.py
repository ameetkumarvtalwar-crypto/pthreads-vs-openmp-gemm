import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results/raw/pthreads_speedup.csv")

plt.figure(figsize=(9, 6))

for size in sorted(df["matrix_size"].unique()):
    data = df[df["matrix_size"] == size]
    plt.plot(data["threads"], data["speedup"], marker="o",
             label=f"N={size}")

plt.xlabel("Number of Threads")
plt.ylabel("Speedup")
plt.title("Pthreads Speedup vs Number of Threads")
plt.xticks([1, 2, 4, 6, 8, 12])
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("results/plots/pthreads_speedup.png", dpi=300)
plt.show()
