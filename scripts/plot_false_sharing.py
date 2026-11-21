import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results/raw/false_sharing_official.csv")

plt.figure(figsize=(9, 6))

plt.plot(
    df["Threads"],
    df["Packed_Average"],
    marker="o",
    label="Packed counters"
)

plt.plot(
    df["Threads"],
    df["Padded_Average"],
    marker="o",
    label="Padded counters"
)

plt.xlabel("Number of Threads")
plt.ylabel("Average Execution Time (seconds)")
plt.title("False Sharing: Packed vs Padded Counters")
plt.xticks([1, 2, 4, 6, 8, 12])
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig("results/plots/false_sharing.png", dpi=300)
plt.show()
