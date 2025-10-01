import json
import matplotlib.pyplot as plt
import numpy as np

def plot_pain_history_fixed(log_file="user_pain_log.json", save_png=False, png_path="pain_plot.png"):
    """
    Plot the pain level evolution from a JSON file.
    
    Parameters:
        log_file (str): Path to the JSON pain log file.
        save_png (bool): Whether to save the plot as PNG.
        png_path (str): File path to save PNG if save_png=True.
    """
    # --- Load file safely ---
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("No pain log file found:", log_file)
        return
    except json.JSONDecodeError:
        print("Pain log file is empty or corrupted.")
        return

    if not data:
        print("No data to plot.")
        return

    # --- Extract x labels and pain values ---
    raw_queries = []
    raw_pains = []
    for i, entry in enumerate(data):
        q = entry.get("user_query") or entry.get("query") or f"entry_{i}"
        p = entry.get("pain_status")

        # convert p to float robustly
        try:
            if isinstance(p, str):
                p_str = p.strip()
                if p_str.endswith("%"):
                    p = float(p_str.rstrip("%")) / 100.0
                else:
                    p = float(p_str)
            else:
                p = float(p)
        except Exception as e:
            print(f"Warning: could not parse pain_status for entry {i} ('{p}'): {e}. Using 0.0")
            p = 0.0

        # clamp to [-1, 1]
        p = max(-1.0, min(1.0, p))
        raw_queries.append(q)
        raw_pains.append(round(p, 2))  # round to 2 decimal points

    # --- Prepare x-axis ---
    x = list(range(len(raw_pains)))
    short_labels = [
        (s[:25] + '...') if isinstance(s, str) and len(s) > 25 else s
        for s in raw_queries
    ]

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(x, raw_pains, marker="o", linestyle="-", linewidth=2, label="Pain Level")

    # Fixed Y-axis and ticks
    ax.set_ylim(-1.0, 1.0)
    ax.set_autoscaley_on(False)
    ax.set_yticks(np.linspace(-1.0, 1.0, 9))

    # X ticks
    ax.set_xticks(x)
    ax.set_xticklabels(short_labels, rotation=45, ha="right")

    # Zero baseline and grid
    ax.axhline(0, color="gray", linestyle="--", linewidth=1)
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)

    ax.set_xlabel("User Query (shortened)")
    ax.set_ylabel("Pain Level (clipped to [-1,1])")
    ax.set_title("Pain Level Evolution (fixed Y-axis -1 to 1)")
    ax.legend()

    plt.tight_layout()

    # Save plot if requested
    if save_png:
        plt.savefig(png_path, dpi=150)
        print("Saved plot to", png_path)

    plt.show()
    plt.close(fig)  # free memory


# --- Example usage ---
if __name__ == "__main__":
    LOG_FILE = "user_pain_log.json"
    plot_pain_history_fixed(log_file=LOG_FILE, save_png=True)



import json
import os

def log_pain_status(user_query: str, pain_status: float, file_path="user_pain_log.json"):
    """
    Log the user query and calculated pain status into a JSON file.
    Each entry will look like:
    {
        "user_query": "...",
        "pain_status": ...
    }
    """
    # Step 1: Load existing log if file exists
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Step 2: Append new record
    data.append({
        "user_query": user_query,
        "pain_status": round(pain_status, 3)
    })

    # Step 3: Save updated log back to file
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
