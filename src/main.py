import pandas as pd

# 1. Load your local dataset
# Replace with your actual filename
filename = "data/2242KANJIFREQUENCYLISTVER.1.1.csv"
df = pd.read_csv(filename)

# 2. Setup your experiment parameters
# The column you want to use for your ranking (e.g., 'AVG FREQ', 'FREQ BIG 5', or '文化庁')
rank_column = "AVG FREQ"

# Your handpicked kanji that you feel represent the "cutoff" boundary.
# (Replace these with your actual borderline kanji from Heisig/Kanji Study)
borderline_kanji = ["靴", "傘", "濯", "誰", "仁", "盾"]

# 3. Analyze your handpicked kanji
# Filter the dataframe to find where your handpicked kanji land
boundary_df = df[df["FORM"].isin(borderline_kanji)][["FORM", rank_column]].copy()

# Sort them so you can see the spread of your intuition
boundary_df = boundary_df.sort_values(by=rank_column)

print("--- Your Boundary Kanji Ranks ---")
print(boundary_df.to_string(index=False))

# 4. Determine a suggested cutoff
# You can use the median or max of your borderline kanji as a starting point
suggested_cutoff = int(boundary_df[rank_column].median())

print(f"\nBased on your picks, a suggested cutoff rank is: {suggested_cutoff}")

# 5. Validate the Cutoff
# Sort the entire dataset by your chosen ranking column
df_sorted = df.sort_values(by=rank_column).reset_index(drop=True)

# Find the index where this cutoff happens
# (Because ranks might skip numbers or have duplicates, finding the closest row is safer)
cutoff_idx = df_sorted[df_sorted[rank_column] >= suggested_cutoff].index[0]

# Display a window of kanji exactly around your cutoff to see if the difficulty feels right
window_size = 5
validation_window = df_sorted.iloc[
    cutoff_idx - window_size : cutoff_idx + window_size + 1
]

print("\n--- Kanji Around the Suggested Cutoff ---")
print(validation_window[["FORM", rank_column]].to_string(index=False))

# 6. Final Split Calculation
high_freq_count = len(df_sorted.iloc[:cutoff_idx])
total_kanji = len(df_sorted)

print(f"\nIf you use {suggested_cutoff} as your cutoff:")
print(f"High Frequency Set: {high_freq_count} kanji")
print(f"Low Frequency Set: {total_kanji - high_freq_count} kanji")
