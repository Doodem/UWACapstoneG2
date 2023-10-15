from TendersWA.Preprocessing.Tender import Tender
import pandas as pd
from bs4 import BeautifulSoup

# saves in whatever directory the python script is called from

tenders_structured_path = r"~/Capstone/UWACapstoneG2/data/UpdatedAgainTenders.xlsx"

tenders_structured = pd.read_excel(tenders_structured_path)
tenders_structured = tenders_structured[["Reference Number", "Contract Title", "Description"]].dropna(subset=["Reference Number"]).drop_duplicates(subset=["Reference Number"])

def remove_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    cleaned = soup.get_text().replace('\xa0', ' ')
    cleaned = ' '.join(cleaned.split())
    return cleaned

for index, row in tenders_structured.iterrows():
    ref = str(row["Reference Number"])
    title = row["Contract Title"]
    desc = remove_html_tags(row["Description"])
    tender = Tender.load(ref)
    if tender == None:
        tender = Tender(ref)

    tender.add("TITLE", title)
    tender.add("DESCRIPTION", desc)
    tender.save()
