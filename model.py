import os
from pydantic import BaseModel

from joblib import load


class EEGSignal(BaseModel):
    sample: list[float]


class Frame(BaseModel):
    timestamp: int
    eeg: list[float]
    # is_clicked: bool = 0


class EegChunk(BaseModel):
    eeg_data: list[list[float]]
    timestamp: list[float]

    # sample_rate: int = 128
    # length: int = 128
    # eeg_signal: list[float]


class ET(BaseModel):
    timestamp: int = 0
    is_clicked: bool = 0


class SVM(object):
    _defaults = {
        "model_path": 'saved_model/svm.joblib',
        "f1_score": 0.77,
        "channels": ["Cz", "Fz", "F7", "F3", "C3", "C4", "F4", "F8"],
        "sample_rate": 128,
        "times": (-0.4, 0.6),
        "freq": (0.16, 0.30),
        "shape_input": (1, 1032)
    }

    def __init__(self, **kwargs):
        self.svm_model = None
        # self.model_path = self._defaults['model_path']
        self.__dict__.update(self._defaults)
        self.__dict__.update(kwargs)

    def __getattr__(self, item):
        return self.__dict__[item]

    def load_model(self):
        model_path = os.path.expanduser(self.model_path)
        assert model_path.endswith(('.joblib', '.pkl')), 'model  must be a .joblib or .pkl file.'
        try:
            self.svm_model = load(model_path)
        except FileNotFoundError:
            print("Not found saved model")

    def detect_ern(self, eeg):
        if self.svm_model is None:
            return 0
        else:
            return self.svm_model.predict(eeg)


# if __name__ == '__main__':
#     svm = SVM()
#     svm.load_model()
#     print(svm.freq[0])
#     print("done")
