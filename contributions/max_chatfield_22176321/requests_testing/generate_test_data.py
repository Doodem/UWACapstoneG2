import pandas as pd

# generate mock data set to test
ref_nums = [str(i) for i in range(100)]
links = ["http://localhost:8000/" + str(i) for i in ref_nums]
Tenders = pd.DataFrame({"Reference Number": ref_nums, "TenderLink": links})
Tenders.to_excel('test.xlsx')
