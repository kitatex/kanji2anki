import pandas as pd

# 1. Load ONLY the kanji and the reading columns
# Replace 'on_yomi' and 'kun_yomi' with the actual column headers in your CSV
df = pd.read_csv(
    "data/rtk/heisig-kanjis.csv", usecols=["kanji", "on_reading", "kun_reading"]
)

# 2. Fill missing values with empty strings so Anki doesn't print "NaN" on blank cards
df = df.fillna("")

# 3. Export this minimalist dataset
df.to_csv("anki_readings_update.txt", index=False, sep="\t", encoding="utf-8-sig")
print("Update file ready!")
