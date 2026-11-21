import pandas as pd
import matplotlib.pyplot as plt

normal = pd.concat([
    pd.read_csv("results/raw/openmp_scheduling_1024.csv"),
    pd.read_csv("results/raw/openmp_scheduling_2048.csv")
])

# Use static scheduling for normal OpenMP
normal = normal[normal["schedule"] == "static"]

collapse = pd.read_csv(
    "results/raw/openmp_collapse_official.csv"
)

plt.figure(figsize=(10, 6))

for size in sorted(collapse["Matrix_Size"].unique()):
    normal_data = normal[
        (normal["matrix_size"] == size) &
        (normal["threads"] == 4)
    ]

    collapse_data = collapse[
        (collapse["Matrix_Size"] == size) &
        (collapse["Threads"] == 4)
    ]

    if not normal_data.empty and not collapse_data.empty:
        plt.bar(
            [f"{size}\nNormal", f"{size}\nCollapse(2)"],
            [
                normal_data.iloc[0]["average_seconds"],
                collapse_data.iloc[0]["Average_Time"]
            ],
            label=f"N={size}"
        )

plt.ylabel("Average Execution Time (seconds)")
plt.title("Normal OpenMP vs OpenMP collapse(2) – 4 Threads")
plt.grid(axis="y")
plt.tight_layout()

plt.savefig(
    "results/plots/openmp_collapse_comparison.png",
    dpi=300
)

plt.show()
