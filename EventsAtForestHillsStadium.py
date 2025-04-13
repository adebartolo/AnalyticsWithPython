'''
Find which events are happening at the Forest Hills Stadium this year
'''

import pdfplumber, requests, pandas as pd, urllib.parse, logging

logging.getLogger("pdfminer").setLevel(logging.ERROR)

url = "https://www.livenation.com/api/calendar/KovZpZA777nA/forest-hills-stadium-upcoming-events.pdf"
pdf_path = "forest_hills.pdf"
with open(pdf_path, "wb") as f:
    f.write(requests.get(url).content)

# Grab event data by extracting from PDF file
data = []
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        table = page.extract_table()
        if not table: continue
        for row in table[1:]:
            name = row[0].strip() if row[0] else ""
            time = row[1].strip() if len(row) > 1 and row[1] else ""
            # Get performer name, excluding event info after the colon or dash
            for sep in [":", "–", "-"]:
                if sep in name:
                    performer = name.split(sep)[0].strip()
                    break
            else:
                performer = name
            data.append([name, performer, time, "Forest Hills Stadium"])

df = pd.DataFrame(data, columns=["Event Name", "Performer", "Start Time", "Venue"])

# Use Wiki to get quick info on each performer
def get_wiki_summary(name):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(name)}"
    r = requests.get(url)
    if r.status_code != 200: return "Not found"
    j = r.json()
    if j.get("type") == "disambiguation":
        return "Multiple meanings. Search manually."
    return j.get("extract", "No summary.")

wiki_info = {p: get_wiki_summary(p) for p in df["Performer"].unique()}
df["Performer Info"] = df["Performer"].map(wiki_info)

print(df)

# Save as CSV
# df.to_csv("forest_hills_events_with_info.csv", index=False)
