from TendersWA.Models.summarisation_model import Summariser

from TendersWA.Preprocessing.Tender import Tender
import os

import re
def clean(content):
    if content != None:
        content = re.sub("[^a-zA-Z.,]", " ", content)
        content = re.sub("_", " ", content)
        content = re.sub("\s+", " ", content)
        return content

def clean_tender(tender):
    for key in tender.file_map.keys():
        tender.file_map[key] = clean(tender.file_map[key])


summariser = Summariser(max_length = 75, min_length = 25)
import pickle

path_to_pickles = r"/home/ucc/maxichat/Capstone/data/tender_raw/"
save_dir = r"/home/ucc/maxichat/Capstone/UWACapstoneG2/data/extended_summaries/"
extended_pickles = pickle.load(open("extended_pickles", "rb"))
def process_tenders(pickle_files):
    os.chdir(path_to_pickles)
    for file in pickle_files:
        tender = Tender.load(file)
        # only process extended tenders and that a .sum file has not been generated
        # a few didnt have descriptions, ignore them
        sum_file = os.path.join(save_dir, f"{tender.reference}.sum")
        if tender != None and "DESCRIPTION" in tender.file_map and len(tender.file_map.keys()) > 2 and not os.path.exists(sum_file):
            clean_tender(tender)
            summary, relevant, short_desc = summariser.summarise_tender(tender)
            if summary != "": # empty summary means something went wrong. Dont record
                summary_result = {"summary": summary, "relevant": relevant, "short_desc": short_desc}
                with open(sum_file, "wb") as f:
                    pickle.dump(summary_result, f)
            else:
                return
        
process_tenders(extended_pickles)
