import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

# =============
# === Model ===
# =============


class Channel(BaseModel):
    name: str
    data: list[float]


class EEGSignal(BaseModel):
    # timestamp: int = 0
    sample_rate: int = 128
    length: int = 128
    eeg_signal: list[Channel]

    #
    # @validator("eeg_signal")
    # def parse_values(cls, value):
    #     return np.array(value, dtype=float)

    # class Config:
    #     arbitrary_types_allowed = True

# ================
# === Function ===
# ================


def create_data(eeg: EEGSignal):
    """
    Create EEG data from input
    :param eeg:
    :return: eeg data
    """
    data = np.ndarray()
    # TODO
    pass
    return data


def processing(data: np.ndarray):
    """
    Processing eeg data

    - filter
    - remove noise
    - smooth
    - downsample
    -



    :param data: eeg data
    :return:
    """
    pass


def predict(eeg_signal):
    """
    Predict eeg data have ERN or non ERN

    :param eeg_signal:
    :return: ERN or not ERN (bool)
    """
    pass


app = FastAPI()

# ==============
# === router ===
# ==============


@app.get("/")
async def base():
    return "Home"


@app.put("/")
async def check_ern(eeg: EEGSignal):
    hasERN = False
    data = create_data(eeg)
    processing(data)
    if predict(data):
        hasERN = True

    return {"Has ERN": f"{hasERN}"}
