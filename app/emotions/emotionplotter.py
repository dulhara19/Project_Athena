import matplotlib.pyplot as plt
import datetime

def plot_user_emotions_and_pain(recent_memory, top_emotions=None):
    """
    Plots pain level and selected emotional states over time.

    Parameters:
    - recent_memory: list of dicts, each dict contains 'timestamp' and 'emotion' info
    - top_emotions: list of emotion names to plot (default is ['sadness', 'anger', 'joy'])
    """

    if top_emotions is None:
        top_emotions = ['sadness', 'anger', 'joy']  # default emotions to track

    # Extract timestamps
    timestamps = [datetime.datetime.fromisoformat(item['timestamp']) for item in recent_memory]

    # Extract pain levels
    pain_levels = [item.get('pain_level', 0) if 'pain_level' in item else 0 for item in recent_memory]

    # Plot pain level
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, pain_levels, label='Pain Level', marker='o', color='red')

    # Plot selected emotions
    for emotion in top_emotions:
        values = [item['emotion']['emotions'].get(emotion, 0) for item in recent_memory]
        plt.plot(timestamps, values, label=emotion.capitalize(), marker='x')

    plt.xlabel('Time')
    plt.ylabel('Intensity / Pain Level')
    plt.title('User Emotional State and Pain Level Over Time')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
