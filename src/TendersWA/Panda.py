from IPython.display import HTML

def pretty_print(df):
    display(HTML(df.to_html(index = False)))

from TendersWA.Preprocessing import Text
import pandas as pd

# loads a panda dataframe, taking care to load without any duplicates in the references
# cols - cols to load
# clean_desc - clean short descriptions of their html tags
def load_tender_uniques(path, cols = ["Reference Number", "Contract Title", "Description"], clean_desc = True):
    df = pd.read_excel(path).astype(str)
    df = df.dropna(subset = ["Reference Number"]).drop_duplicates(subset = ["Reference Number"])[cols]
    if clean_desc:
        for index, row in df.iterrows():
            desc = Text.remove_html_tags(row["Description"])
            df.at[index, "Description"] = desc

    return df