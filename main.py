import csv
import threading
import time
from typing import Union

import numpy as np
from joblib import load

from fastapi import FastAPI

from mne import Info, create_info, pick_channels
from mne.baseline import rescale
from mne.io import RawArray
from mne.preprocessing import ICA
from mne_icalabel import label_components
from mne.filter import filter_data, resample
from pydantic import BaseModel


from config import ModelSettings, Outlet, GeneralSettings
from model import EegChunk, ET

# =================
# === Parameter ===
# =================

DOWN_SAMPLE: int   # RAW_SAMPLING_RATE/MODEL_SAMPLING_RATE

PICK_IDX = []

info_raw: Info

# ET
PREDICT_COUNT: int = 0
CLICKED: bool = False
timestamp_clicked: int = 0

# EEG
buffer: EegChunk = EegChunk()

# setting
setting = GeneralSettings()


# predict model
model_setting: ModelSettings = ModelSettings()
model = load(model_setting.model_path)

# ================
# === Function ===
# ================


def reset_buffer():

    buffer.eeg_data = []
    buffer.timestamp = []


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
    # global eeg_buffer, timestamp_buffer

    buffer.eeg_data.extend(chunk.eeg_data)
    buffer.timestamp.extend(chunk.timestamp)

    while len(buffer.eeg_data) > setting.BUFFER_SIZE:
        buffer.eeg_data.pop(0)
        buffer.timestamp.pop(0)

    return


def processing():
    """
    Processing eeg data


    Parameters
    ----------

    Returns
    -------
    segment: np.ndarray
        EEG segment for detect ERN.
    """
    # global eeg_buffer, timestamp_buffer
    global PICK_IDX
    eeg = np.array(buffer.eeg_data).T

    if setting.use_ica:
        raw = RawArray(data=eeg, info=info_raw)

        raw.filter(model_setting.l_freq, model_setting.h_freq)

        ica = ICA(
            n_components=.99,
            max_iter="auto",
            method="infomax",
            # random_state=97,
            fit_params=dict(extended=True),
        )
        ica.fit(raw)

        labels = label_components(raw, ica, method="iclabel")["labels"]

        exclude_idx = [idx for idx, label in enumerate(labels) if label not in ["brain", "other"]]
        ica.apply(raw, exclude=exclude_idx)
        raw.pick_channels(model_setting.channels)

        resampled = raw.resample(model_setting.sfreq).get_data()
    else:
        # pick channel
        picked = eeg[PICK_IDX]

        # filter
        filtered = filter_data(picked,
                               sfreq=setting.RAW_SAMPLING_RATE,
                               l_freq=model_setting.l_freq, h_freq=model_setting.h_freq,
                               # method='iir',
                               verbose=0)

        # downsample
        resampled = resample(filtered,
                             down=DOWN_SAMPLE,
                             verbose=0)
    # mne.filter.s
    # segmented = resampled[:, -1024:]

    # Split segmented
    segmented = resampled[:, -model_setting.shape[2]:]

    # Norm
    rescaled = rescale(data=segmented,
                       times=np.array(buffer.timestamp[-model_setting.shape[1]:]) - buffer.timestamp[-model_setting.shape[1]],
                       baseline=(0, -model_setting.t_min), mode='mean')

    # flatten
    trans = rescaled.reshape(1, -1)

    return trans


def is_correct(eeg_signal):
    return model.predict(eeg_signal)


class BackgroundTasks(threading.Thread):
    def run(self):
        outlet = Outlet()
        # global PREDICT_COUNT, CLICKED, timestamp_clicked

        while True:
            global PREDICT_COUNT, CLICKED, timestamp_clicked
            if CLICKED and len(buffer.eeg_data) > setting.BUFFER_SIZE:
                segment_data = processing()
                if is_correct(segment_data):
                    PREDICT_COUNT = PREDICT_COUNT - 1
                    if PREDICT_COUNT == 0:
                        CLICKED = False
                    outlet.send_sample(timestamp_clicked, 1)  # action correct
                else:
                    PREDICT_COUNT = 0
                    CLICKED = False
                    outlet.send_sample(timestamp_clicked, 0)  # action error
            # else:
            #     outlet.send_sample(timestamp_clicked, 1)

            time.sleep(0.1)


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    global PICK_IDX, CLICKED
    global DOWN_SAMPLE
    global info_raw

    # down sample rate
    DOWN_SAMPLE = int(setting.RAW_SAMPLING_RATE/model_setting.sfreq)

    # set channel eeg for model
    f = open('channels.csv')
    file = csv.reader(f, delimiter=',')
    channels = []
    for row in file:
        channels.append(row[1])

    info_raw = create_info(ch_names=channels, sfreq=setting.RAW_SAMPLING_RATE, ch_types='eeg')
    PICK_IDX = pick_channels(ch_names=channels, include=model_setting.channels, ordered=True)

    # set action status
    CLICKED = False

    # start predict outlet
    Predict = BackgroundTasks()
    Predict.start()


# ==============
# === router ===
# ==============


@app.get("/")
async def base():
    return "Home"


@app.put("/update_eeg")
async def update_eeg(chunk: EegChunk):
    # , et: Union[ET, None] = None
    update_buffer(chunk)

    return {'eeg_updated': 'ok'}


@app.put('/update_et')
async def clicked(et: ET):
    global PREDICT_COUNT, timestamp_clicked, CLICKED
    if et.is_clicked:
        CLICKED = True
        timestamp_clicked = et.timestamp
        PREDICT_COUNT = setting.PREDICT_COUNT

    return {'status': 'ok'}
