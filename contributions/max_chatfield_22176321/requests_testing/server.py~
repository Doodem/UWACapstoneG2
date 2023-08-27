from typing import Union
from fastapi import FastAPI
import time

app = FastAPI()

last_epoch = 0

@app.get("/{ref_num}")
def req(ref_num: int):
	global last_epoch
	diff = time.time() - last_epoch
	print(f"Difference from last req: {diff}")
	last_epoch = time.time()
