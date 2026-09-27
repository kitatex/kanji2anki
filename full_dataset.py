import pandas as pd

# 1. Load the base RTK dataset (this dictates all rows in the deck)
df = pd.read_csv("data/rtk/heisig-kanjis.csv", usecols=["kanji", "id_5th_ed"])

# Rename, sort, and zero-pad the RTK index
df = df.rename(columns={"id_5th_ed": "rtk_index"})
df = df.sort_values(by="rtk_index")
df["rtk_index"] = df["rtk_index"].fillna(9999).astype(int).astype(str).str.zfill(4)

# 2. Add the meanings from KANJIDIC2
df_csv_meanings = pd.read_csv("data/kanji_meanings.csv")
df = df.merge(df_csv_meanings, on="kanji", how="left")

# 3. Extract Keyword (Falls back to the first dictionary meaning)
df["keyword"] = df["meanings"].apply(
    lambda x: str(x).split(",")[0].strip() if pd.notna(x) else ""
)

# 4. Set placeholder story for all new cards
df["story"] = "not yet written"

# 5. Load and merge the frequency data
df_freq = pd.read_csv(
    "data/2242KANJIFREQUENCYLISTVER.1.1.csv", usecols=["FORM", "Google"]
)
df_freq = df_freq.rename(columns={"FORM": "kanji"})
df = df.merge(df_freq, on="kanji", how="left")

# Format frequency ranks
df = df.rename(columns={"Google": "frequency_rank"})
df["frequency_rank"] = df["frequency_rank"].fillna(9999).astype(int)

# 6. Create Anki tagging for rare kanji
df["anki_tag"] = df["frequency_rank"].apply(
    lambda x: "suspend_rare" if x > 1800 else ""
)

# 7. Add SVG image tags
df["stroke_svg"] = df["kanji"].apply(
    lambda x: f'<img src="{hex(ord(x))[2:].zfill(5)}.svg">'
)

# 8. Reorder and export to text file
df = df[
    [
        "kanji",
        "keyword",
        "meanings",
        "story",
        "frequency_rank",
        "rtk_index",
        "stroke_svg",
        "anki_tag",
    ]
]

print(df.head(5))

df.to_csv("anki_import_ready_full.txt", index=False, sep="\t", encoding="utf-8-sig")
