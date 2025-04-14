'''
Find which events are happening at the Forest Hills Stadium this year
'''
!pip install pdfplumber requests

import pdfplumber, requests, pandas as pd, urllib.parse, logging
from datetime import datetime

logging.getLogger("pdfminer").setLevel(logging.ERROR)

# Download the PDF
url = "https://www.livenation.com/api/calendar/KovZpZA777nA/forest-hills-stadium-upcoming-events.pdf"
pdf_path = "forest_hills.pdf"
with open(pdf_path, "wb") as f:
    f.write(requests.get(url).content)

# Extract data from PDF
data = []
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        table = page.extract_table()
        if not table: continue
        for row in table[1:]:
            name = row[0].strip() if row[0] else ""
            time = row[1].strip() if len(row) > 1 and row[1] else ""

            # Get performer name before any colon or dash
            for sep in [":", "–", "-"]:
                if sep in name:
                    performer = name.split(sep)[0].strip()
                    break
            else:
                performer = name

            # Split Start Time into Date and Time
            try:
                dt = datetime.strptime(time, "%a, %b %d, %Y, %I:%M %p")
                event_date = dt.strftime("%Y-%m-%d")
                event_time = dt.strftime("%I:%M %p")
            except:
                event_date = ""
                event_time = time

            data.append(["Forest Hills Stadium", name, performer, event_date, event_time])

# Create DataFrame with renamed columns
df = pd.DataFrame(data, columns=["Venue", "Event Name", "Performer", "Event Date", "Event Time"])

# Get Wikipedia summaries
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

# Print DataFrame
print(df)

# Optional: Save as CSV
# df.to_csv("forest_hills_events_cleaned.csv", index=False)
