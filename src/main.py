import pandas as pd
import re


# 1. Helper function to safely read the text files
def parse_kanjistudy_export(filepath, column_name):
    data = []
    # Using utf-8 is crucial here to avoid character mapping errors
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # The kanji is the first character.
            # Everything after the first space is the story/meaning.
            kanji = line[0]
            content = line[1:].strip()

            data.append({"kanji": kanji, column_name: content})

    return pd.DataFrame(data)


# 2. Load the datasets
# Replace these strings with your actual file paths
df_stories = parse_kanjistudy_export(
    "data/kanji_study/KanjiStudy-Kanji-Notes-20260823132418.txt", "story"
)
df_custom_meanings = parse_kanjistudy_export(
    "data/kanji_study/KanjiStudy-Kanji-Meanings-20260823132555.txt", "custom_meanings"
)

# Load the CSV we generated previously
df_csv_meanings = pd.read_csv("data/kanji_meanings.csv")

# 3. Merge the DataFrames
# Left join ensures we keep all 619 kanji from your stories
df = df_stories.merge(df_custom_meanings, on="kanji", how="left")
df = df.merge(df_csv_meanings, on="kanji", how="left")

# 4. Consolidate the 'meanings' column
# This uses the custom meaning if it exists, otherwise it falls back to the CSV meaning
df["meanings"] = df["custom_meanings"].fillna(df["meanings"])

# Drop the temporary columns to keep the DataFrame clean
df = df.drop(columns=["custom_meanings"])


# 5. Extract the Keyword
def extract_keyword(row):
    # Search for anything captured between two asterisks
    match = re.search(r"\*(.*?)\*", str(row["story"]))

    if match:
        return match.group(1)  # Return the word inside the asterisks

    # Fallback: Take the first element of the meanings list
    if pd.notna(row["meanings"]):
        # Assuming meanings are separated by commas (like in KANJIDIC2)
        return str(row["meanings"]).split(",")[0].strip()

    return ""  # Absolute fallback if nothing is found


# Apply the function row by row
df["keyword"] = df.apply(extract_keyword, axis=1)

# 6. Reorder columns for a clean final dataset
df = df[["kanji", "keyword", "meanings", "story"]]

# 7. Load and merge the frequency data
df_freq = pd.read_csv(
    "data/2242KANJIFREQUENCYLISTVER.1.1.csv", usecols=["FORM", "Google"]
)

# Rename 'FORM' to 'kanji' so pandas knows how to join them
df_freq = df_freq.rename(columns={"FORM": "kanji"})

# Merge into your main DataFrame (Left join keeps your 619 story kanji intact)
df = df.merge(df_freq, on="kanji", how="left")
df = df.rename(columns={"Google": "frequency_rank"})

# Fill missing kanji with a high rank (9999) so they are treated as rare,
# then convert the entire column to integers.
df["frequency_rank"] = df["frequency_rank"].fillna(9999).astype(int)

# 8. Create a column specifically for Anki tagging.
# It outputs the tag "suspend_rare" if the value is > 1800, and leaves it blank otherwise.
df["anki_tag"] = df["frequency_rank"].apply(
    lambda x: "suspend_rare" if x > 1800 else ""
)

# 9. Update order based on heisig dataset
df_rtk = pd.read_csv("data/rtk/heisig-kanjis.csv", usecols=["kanji", "id_5th_ed"])
df = df.merge(df_rtk, on="kanji", how="left")
df = df.sort_values(by="id_5th_ed")
df = df.rename(columns={"id_5th_ed": "rtk_index"})
df["rtk_index"] = df["rtk_index"].fillna(9999).astype(int).astype(str).str.zfill(4)
df = df[
    [
        "kanji",
        "keyword",
        "meanings",
        "story",
        "frequency_rank",
        "rtk_index",
        "anki_tag",
    ]
]

print(df.head(5))

# Finally, export your perfectly ordered Anki file
df.to_csv("anki_import_ready.txt", index=False, sep="\t", encoding="utf-8-sig")
