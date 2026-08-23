import pandas as pd

# 1. Fetch the 2,136 Jouyou Kanji
joyo_url = (
    "https://raw.githubusercontent.com/sph-mn/nihongo/master/data/jouyou-kanji.csv"
)
# The CSV has no headers, so we assign them
df_joyo = pd.read_csv(joyo_url, header=None, names=["kanji", "meaning", "readings"])

# 2. Fetch Kanji Frequencies
# (Swap 'wikipedia.json' with 'aozora.json' for literature/fiction frequencies)
freq_url = "https://raw.githubusercontent.com/scriptin/kanji-frequency/master/data/wikipedia.json"
df_freq = pd.read_json(freq_url)
df_freq.columns = ["kanji", "frequency_count"]

# 3. Merge datasets (Inner join keeps only Jouyou Kanji that appear in the frequency data)
df_merged = pd.merge(df_joyo, df_freq, on="kanji", how="inner")

# 4. Sort by frequency in descending order and reset the index
df_merged = df_merged.sort_values(by="frequency_count", ascending=False).reset_index(
    drop=True
)

# 5. Add ranking and cumulative percentage to help you find your cutoff
df_merged["joyo_rank"] = df_merged.index + 1
total_joyo_occurrences = df_merged["frequency_count"].sum()
df_merged["cumulative_percentage"] = (
    df_merged["frequency_count"].cumsum() / total_joyo_occurrences
) * 100

print(
    df_merged[["joyo_rank", "kanji", "frequency_count", "cumulative_percentage"]].head(
        10
    )
)

# --- Exploring the Cutoff ---
# If you want slightly more than half of the 2,136 Jouyou kanji in your high-frequency set:
cutoff_rank = 1200

high_freq_set = df_merged[df_merged["joyo_rank"] <= cutoff_rank]
low_freq_set = df_merged[df_merged["joyo_rank"] > cutoff_rank]

print(
    f"\nThe top {cutoff_rank} kanji account for {high_freq_set['cumulative_percentage'].iloc[-1]:.2f}% of all Jouyou kanji usage."
)
