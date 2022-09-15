from typing import List, Tuple, Union

from pydantic import BaseSettings, validator, FilePath
from pylsl import StreamOutlet, StreamInfo


class ModelSettings(BaseSettings):
    name: str = 'SVM'
    model_path: FilePath = 'saved_model/svm_FzCz.joblib'

    # input
    channels: List[str] = ["Fz", "Cz", ]
    sfreq: int = 32
    t_min: float = -0.4
    t_max: float = 0.6
    l_freq: float = 4
    h_freq: float = 8
    shape: Tuple[Tuple[int, int], int] = ((1, 52), 26)

    # validator
    @validator('t_max')
    def t_validator(cls, t_max, values):
        if 't_min' in values and not values['t_min'] < t_max:
            raise ValueError('t_max must greater than t_min')
        return t_max

    @validator('h_freq')
    def freq_validator(cls, h_freq: float, values):
        if 'l_freq' in values and not values['l_freq'] < h_freq:
            raise ValueError('h_freq must greater than l_freq')
        return h_freq

    @validator('model_path')
    def path_validator(cls, model_path: FilePath):
        if model_path.suffix not in ('.joblib', '.pkl'):
            raise ValueError('Model must be a .joblib or .pkl file.')
        return model_path


class GeneralSettings(BaseSettings):
    RAW_SAMPLING_RATE: int = 128

    BUFFER_TIME = 4  # seconds
    BUFFER_SIZE = BUFFER_TIME * RAW_SAMPLING_RATE

    use_ica: bool = False

    PREDICT_COUNT: int = 3


class Outlet(object):
    __name = 'ERN'
    __n_channels = 1
    # channel_format: int cf_float32
    __data_type = 'Markers'
    __sfreq = 4
    __source_id = 'ERN_API'
    __outlet: StreamOutlet
    __channel_names = ['Predict']

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        info = StreamInfo(name=self.__name, type=self.__data_type, channel_count=self.__n_channels,
                          # channel_format= ,
                          nominal_srate=self.__sfreq, source_id=self.__source_id)

        chns = info.desc().append_child("channels")
        for label in self.__channel_names:
            ch = chns.append_child("channel")
            ch.append_child_value("label", label)

        self.outlet = StreamOutlet(info)

    def send_sample(self, timestamp: Union[float, None], predict: int = 1):
        if timestamp is None:
            self.outlet.push_sample([predict])
        else:
            self.outlet.push_sample([predict], timestamp=timestamp)
        # timestamp = timestamp + 1
        # sleep(0.1)

    def channel_names(self):
        return self.__channel_names
