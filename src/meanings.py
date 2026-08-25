import urllib.request
import gzip
import xml.etree.ElementTree as ET
import pandas as pd

# 1. Download the official KANJIDIC2 database (GZipped XML)
url = "http://www.edrdg.org/kanjidic/kanjidic2.xml.gz"
filename = "kanjidic2.xml.gz"

print("Downloading KANJIDIC2...")
urllib.request.urlretrieve(url, filename)

# 2. Extract and parse the XML
print("Parsing XML...")
with gzip.open(filename, "rt", encoding="utf-8") as f:
    tree = ET.parse(f)
    root = tree.getroot()

# 3. Extract the literal kanji and their English meanings
kanji_data = []

for character in root.findall("character"):
    literal = character.find("literal").text

    meanings = []
    reading_meaning = character.find("reading_meaning")

    if reading_meaning is not None:
        rmgroup = reading_meaning.find("rmgroup")
        if rmgroup is not None:
            # We only extract English meanings (nodes without an 'm_lang' attribute)
            for meaning in rmgroup.findall("meaning"):
                if not meaning.attrib:
                    meanings.append(meaning.text)

    if meanings:
        kanji_data.append({"kanji": literal, "meanings": ", ".join(meanings)})

# 4. Create the Pandas DataFrame
df_meanings = pd.DataFrame(kanji_data)

# Test with your example
print(df_meanings[df_meanings["kanji"] == "詮"])

# Save the DataFrame to a CSV file
df_meanings.to_csv("kanji_meanings.csv", index=False, encoding="utf-8-sig")
