import csv
from typing import Union

import mne.filter
import numpy as np
from fastapi import FastAPI
from mne.baseline import rescale
from mne.decoding import Vectorizer

from model import SVM, EegChunk, ET

# =============
# === Model ===
# =============

# =================
# === Parameter ===
# =================


SAMPLING_RATE = 128
L_FREQ = 0.16
H_FREQ = 30.

BUFFER_TIME = 4   # seconds
SEGMENT_TIME = 1  # seconds

BUFFER_SIZE = BUFFER_TIME * SAMPLING_RATE
SEGMENT_SIZE = SEGMENT_TIME * SAMPLING_RATE+1
# SEGMENT_SIZE = 0
PICK_IDX = []
DOWN_SAMPLE = 1


PREDICT_COUNT = 3

eeg_buffer = []
timestamp_buffer = []

# current_time_stamp = 0
svm_model = None


# times = 1

# ================
# === Function ===
# ================


def update_buffer(chunk):
    """
    Update EEG buffer

    Parameters
    ----------
    chunk: EegChunk
        chunk of eeg signal receive from emotiv

    Returns
    -------

    """
    global eeg_buffer
    global timestamp_buffer

    # sampling_length = len(eeg_buffer[0])
    eeg_buffer.extend(chunk.eeg_data)
    timestamp_buffer.extend(chunk.timestamp)

    while len(eeg_buffer) > BUFFER_SIZE:
        eeg_buffer.pop()

    return


def processing(raw_eeg):
    """
    Processing eeg data

    - reformat
    - filter
    - remove noise
    - smooth
    - downsample


    Parameters
    ----------
    raw_eeg : list
        EEG signal buffer.

    Returns
    -------
    segment: np.ndarray
        EEG segment for detect ERN.
    """
    global timestamp_buffer, PICK_IDX
    eeg = np.array(raw_eeg).T

    picked = eeg[PICK_IDX]

    filtered = mne.filter.filter_data(picked,
                                      sfreq=SAMPLING_RATE,
                                      l_freq=L_FREQ, h_freq=H_FREQ,
                                      method='iir',
                                      verbose=0)

    resampled = mne.filter.resample(filtered,
                                    down=DOWN_SAMPLE,
                                    verbose=0)
    # mne.filter.s
    # segmented = resampled[:, -1024:]

    segmented = resampled[:, -SEGMENT_SIZE:]

    rescaled = rescale(data=segmented, times=np.array(timestamp_buffer[-SEGMENT_SIZE:])-timestamp_buffer[-SEGMENT_SIZE],
                       baseline=(0, 0.4),  mode='mean')

    vect = Vectorizer()

    trans = vect.fit_transform([rescaled])

    return trans


def is_correct(eeg_signal):
    return svm_model.detect_ern(eeg_signal)


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    global svm_model, L_FREQ, H_FREQ, PICK_IDX

    svm_model = SVM()
    svm_model.load_model()

    L_FREQ = svm_model.freq[0]
    H_FREQ = svm_model.freq[1]

    f = open('channels.csv')
    file = csv.reader(f, delimiter=',')
    channels = []
    for row in file:
        channels.append(row[1])
    # PICKS = svm_model.channels
    PICK_IDX = mne.pick_channels(ch_names= channels, include=svm_model.channels)


# ==============
# === router ===
# ==============


@app.get("/")
async def base():
    return "Home"


@app.put("/test")
async def check_error_action(chunk: EegChunk, et: Union[ET, None] = None):
    update_buffer(chunk)
    if et is not None:
        if et.is_clicked:
            segment_data = processing(eeg_buffer)
            if not is_correct(segment_data):
                return {"error": 1}
        return {"error": 0}
    else:
        return {"error": 0}
