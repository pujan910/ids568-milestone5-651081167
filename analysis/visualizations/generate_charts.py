import json
import matplotlib.pyplot as plt
import numpy as np
import os

os.makedirs("analysis/visualizations", exist_ok=True)

with open("benchmarks/results/cold_vs_warm.json") as f:
    cvw = json.load(f)

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(["Cold Cache", "Warm Cache"], [cvw["cold_ms"], cvw["warm_ms"]], color=["#e74c3c", "#2ecc71"], width=0.4)
ax.set_ylabel("Latency (ms)")
ax.set_title("Cold vs Warm Cache Latency")
for bar, val in zip(bars, [cvw["cold_ms"], cvw["warm_ms"]]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, f"{val:.1f}ms", ha="center", fontweight="bold")
ax.set_ylim(0, cvw["cold_ms"] * 1.3)
plt.tight_layout()
plt.savefig("analysis/visualizations/cold_vs_warm.png", dpi=150)
plt.close()

with open("benchmarks/results/batching.json") as f:
    bat = json.load(f)

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(range(1, len(bat["individual"])+1), bat["individual"], color="#3498db")
ax.axhline(bat["avg_latency_ms"], color="red", linestyle="--", label=f"Avg: {bat['avg_latency_ms']:.1f}ms")
ax.set_xlabel("Request #")
ax.set_ylabel("Latency (ms)")
ax.set_title("Latency of 10 Concurrent Batched Requests")
ax.legend()
plt.tight_layout()
plt.savefig("analysis/visualizations/batching_latency.png", dpi=150)
plt.close()

with open("benchmarks/results/hit_rate.json") as f:
    hr = json.load(f)

cumulative_hits = []
total = 0
hits = 0
for r in hr:
    total += 1
    if r["cached"]:
        hits += 1
    cumulative_hits.append(hits / total * 100)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(range(1, len(cumulative_hits)+1), cumulative_hits, color="#9b59b6", linewidth=2)
ax.set_xlabel("Request Number")
ax.set_ylabel("Cumulative Hit Rate (%)")
ax.set_title("Cache Hit Rate Over Time")
ax.set_ylim(0, 100)
ax.axhline(72.5, color="gray", linestyle="--", label="Final hit rate: 72.5%")
ax.legend()
plt.tight_layout()
plt.savefig("analysis/visualizations/hit_rate_over_time.png", dpi=150)
plt.close()

levels = ["Low (5 concurrent)", "Medium (20 concurrent)", "High (50 concurrent)"]
latencies = [755.7, 2.8, 6.7]
hit_rates = [65, 100, 100]

fig, ax1 = plt.subplots(figsize=(9, 5))
x = np.arange(len(levels))
ax1.bar(x - 0.2, latencies, 0.4, label="Avg Latency (ms)", color="#e67e22")
ax1.set_ylabel("Avg Latency (ms)", color="#e67e22")
ax1.set_xticks(x)
ax1.set_xticklabels(levels)
ax2 = ax1.twinx()
ax2.bar(x + 0.2, hit_rates, 0.4, label="Cache Hit Rate (%)", color="#1abc9c")
ax2.set_ylabel("Cache Hit Rate (%)", color="#1abc9c")
ax2.set_ylim(0, 120)
ax1.set_title("Performance Under Different Load Levels")
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
plt.tight_layout()
plt.savefig("analysis/visualizations/load_comparison.png", dpi=150)
plt.close()
print("All 4 charts generated!")
