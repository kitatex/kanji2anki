import pandas as pd

# Load the base RTK dataset (this dictates all rows in the deck)
df = pd.read_csv(
    "data/rtk/heisig-kanjis.csv",
    usecols=["kanji", "id_6th_ed", "keyword_6th_ed", "on_reading", "kun_reading"],
)

# Rename, sort, and zero-pad the RTK index
df = df.rename(columns={"id_6th_ed": "rtk_index"})
df = df.rename(columns={"keyword_6th_ed": "keyword"})
df = df.sort_values(by="rtk_index")
df["rtk_index"] = df["rtk_index"].fillna(9999).astype(int).astype(str).str.zfill(4)

# Add the meanings from KANJIDIC2
df_csv_meanings = pd.read_csv("data/kanji_meanings.csv")
df = df.merge(df_csv_meanings, on="kanji", how="left")

# Set placeholder story for all new cards
df["story"] = "STORY"

# Load and merge the frequency data
df_freq = pd.read_csv(
    "data/2242KANJIFREQUENCYLISTVER.1.1.csv", usecols=["FORM", "Google"]
)
df_freq = df_freq.rename(columns={"FORM": "kanji"})
df = df.merge(df_freq, on="kanji", how="left")

# Format frequency ranks
df = df.rename(columns={"Google": "frequency_rank"})
df["frequency_rank"] = df["frequency_rank"].fillna(9999).astype(int)

# Create Anki tagging for rare kanji
df["anki_tag"] = df["frequency_rank"].apply(
    lambda x: "suspend_rare" if x > 1800 else ""
)

# Add SVG image tags
df["stroke_svg"] = df["kanji"].apply(
    lambda x: f'<img src="{hex(ord(x))[2:].zfill(5)}.svg">'
)

# Reorder and export to text file
df = df[
    [
        "kanji",
        "keyword",
        "meanings",
        "story",
        "frequency_rank",
        "rtk_index",
        "stroke_svg",
        "on_reading",
        "kun_reading",
        "anki_tag",
    ]
]

print(df.head(5))

df.to_csv("anki_import_ready_full.txt", index=False, sep="\t", encoding="utf-8-sig")
