import pandas as pd
import matplotlib.pyplot as plt
import os

sizes = [512, 1024, 2048]

os.makedirs("results/plots", exist_ok=True)

for size in sizes:

    file = f"results/raw/benchmark_{size}.csv"

    df = pd.read_csv(file)

    summary = df.groupby(
        ["implementation", "threads_or_ranks"]
    )["total_ms"].agg(["mean", "std"]).reset_index()

    seq_time = summary[
        summary["implementation"] == "Sequential"
    ]["mean"].iloc[0]

    pthreads = summary[
        summary["implementation"] == "Pthreads"
    ]

    openmp = summary[
        summary["implementation"] == "OpenMP-static"
    ]

    # GRAPH 1: Execution time vs threads

    plt.figure(figsize=(9, 5))

    plt.errorbar(
        pthreads["threads_or_ranks"],
        pthreads["mean"] / 1000,
        yerr=pthreads["std"] / 1000,
        marker="o",
        capsize=4,
        label="Pthreads"
    )

    plt.errorbar(
        openmp["threads_or_ranks"],
        openmp["mean"] / 1000,
        yerr=openmp["std"] / 1000,
        marker="s",
        capsize=4,
        label="OpenMP"
    )

    plt.axhline(
        seq_time / 1000,
        linestyle="--",
        label="Sequential"
    )

    plt.xlabel("Number of Threads")
    plt.ylabel("Execution Time (seconds)")
    plt.title(f"Execution Time vs Threads - {size}x{size}")
    plt.legend()
    plt.grid(True)

    plt.savefig(
        f"results/plots/time_vs_threads_{size}.png",
        dpi=300
    )

    plt.close()

    # GRAPH 2: Speedup

    plt.figure(figsize=(9, 5))

    for name, data in [
        ("Pthreads", pthreads),
        ("OpenMP", openmp)
    ]:

        speedup = seq_time / data["mean"]

        plt.plot(
            data["threads_or_ranks"],
            speedup,
            marker="o",
            label=name
        )

    plt.plot(
        [1, 2, 4, 6, 8, 12],
        [1, 2, 4, 6, 8, 12],
        linestyle="--",
        label="Ideal speedup"
    )

    plt.xlabel("Number of Threads")
    plt.ylabel("Speedup")
    plt.title(f"Speedup vs Threads - {size}x{size}")
    plt.legend()
    plt.grid(True)

    plt.savefig(
        f"results/plots/speedup_{size}.png",
        dpi=300
    )

    plt.close()

    # GRAPH 3: Parallel efficiency

    plt.figure(figsize=(9, 5))

    for name, data in [
        ("Pthreads", pthreads),
        ("OpenMP", openmp)
    ]:

        speedup = seq_time / data["mean"]

        efficiency = speedup / data["threads_or_ranks"]

        plt.plot(
            data["threads_or_ranks"],
            efficiency * 100,
            marker="o",
            label=name
        )

    plt.xlabel("Number of Threads")
    plt.ylabel("Parallel Efficiency (%)")
    plt.title(f"Parallel Efficiency - {size}x{size}")
    plt.legend()
    plt.grid(True)

    plt.savefig(
        f"results/plots/efficiency_{size}.png",
        dpi=300
    )

    plt.close()

    print(f"Graphs generated for matrix size {size}")

print("\nAll graphs generated successfully!")
