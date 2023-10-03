from TendersWA.Preprocessing.Tender import Tender

path_to_pickles = r"/home/ucc/maxichat/Capstone/data/tender_raw/"

extended_tenders = []
import os
os.chdir(path_to_pickles)
for file in os.listdir(path_to_pickles):
    if file.endswith(".pickle"):
        tender = Tender.load(file)
        if tender != None:
            if len(tender.file_map.keys()) > 2:
                extended_tenders.append(file)

import pickle
with open('extended_pickles', 'wb') as f:
    pickle.dump(extended_tenders, f)