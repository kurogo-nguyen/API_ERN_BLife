import mne.filter
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
    timestamp: int = 0
    ET: bool = 0
    # sample_rate: int = 128
    # length: int = 128
    eeg_signal: list[float]

    #
    # @validator("eeg_signal")
    # def parse_values(cls, value):
    #     return np.array(value, dtype=float)

    # class Config:
    #     arbitrary_types_allowed = True


# =================
# === Parameter ===
# =================

SAMPLING_RATE = 128
L_FREQ = 0.16
H_FREQ = 30.

BUFFER_SIZE = 256
SEGMENT_TIME = 800  # milliseconds
PICKS = ['Fz', 'Cz']
DOWN_SAMPLE = 8

eeg_data = np.zeros((32, 1))
current_time_stamp = 0


# times = 1

# ================
# === Function ===
# ================


def update_data(eeg_signal, timestamp):
    """
    Update EEG buffer

    Parameters
    ----------
    eeg_signal : array_like
        Values of all sensor in a frame.
    timestamp : int
        Timestamp of frame.

    Returns
    -------
    None
    """
    global eeg_data
    global current_time_stamp

    sampling_length = len(eeg_data[0])
    eeg_data = np.insert(eeg_data, len(eeg_data[0]), np.array(eeg_signal[3:-2]), axis=1)
    current_time_stamp = timestamp

    if sampling_length > BUFFER_SIZE:
        eeg_data = np.delete(eeg_data, 0, axis=1)

    return


def processing(raw_eeg):
    """
    Processing eeg data

    - filter
    - remove noise
    - smooth
    - downsample


    Parameters
    ----------
    raw_eeg : np.ndarray
        EEG signal buffer.

    Returns
    -------
    segment: np.ndarray
        EEG segment for detect ERN.


    """
    filtered = mne.filter.filter_data(raw_eeg,
                                      sfreq=SAMPLING_RATE,
                                      l_freq=L_FREQ, h_freq=H_FREQ,)

    resampled = mne.filter.resample(filtered,
                                    down=DOWN_SAMPLE)

    segmented = resampled[:, -SEGMENT_TIME*SAMPLING_RATE/DOWN_SAMPLE:]

    return segmented


def predict(eeg_signal):
    """
    Predict eeg data have ERN or non ERN

    :param eeg_signal:
    :return: ERN or not ERN (bool)
    """

    return True


app = FastAPI()


# ==============
# === router ===
# ==============


@app.get("/")
async def base():
    return "Home"


@app.put("/")
async def check_ern(frame: EEGSignal):
    hasERN = False
    update_data(frame.eeg_signal, frame.timestamp)
    if frame.ET:
        segment_data = processing(eeg_data)
        if predict(segment_data):
            hasERN = True

        return {"Has ERN": f"{hasERN}"}
    else:
        return {"Has ERN": 0}
