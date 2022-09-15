from typing import List

from pydantic import BaseModel

from config import Outlet


class Frame(BaseModel):
    timestamp: int
    eeg: List[float]
    # is_clicked: bool = 0


class EegChunk(BaseModel):
    eeg_data: List[List[float]] = []
    timestamp: List[float] = []


class ET(BaseModel):
    timestamp: int
    is_clicked: bool


# class SVM(object):
#     _defaults1 = {
#         "model_path": 'saved_model/svm.joblib',
#         "f1_score": 0.77,
#         "channels": ["Cz", "Fz", "F7", "F3", "C3", "C4", "F4", "F8"],
#         "sample_rate": 128,
#         "times": (-0.4, 0.6),
#         "freq": (0.16, 0.30),
#         "shape_input": (1, 1032)
#     }
#     _defaults2 = {
#         "model_path": 'saved_model/svm_FzCz.joblib',
#         "f1_score": 0.73,
#         "channels": ["Fz", "Cz", ],
#         "sample_rate": 32,
#         "times": (-0.2, 0.6),
#         "freq": (4, 8),
#         "shape_input": (1, 52)
#     }
#
#     def __init__(self, mode: int = 2, **kwargs):
#         self.svm_model = None
#         # self.model_path = self._defaults['model_path']
#         if mode == 1:
#             self.__dict__.update(self._defaults1)
#         else:
#             self.__dict__.update(self._defaults2)
#         # self.__dict__.update(kwargs)
#
#     def __getattr__(self, item):
#         return self.__dict__[item]
#
#     def load_model(self):
#         model_path = os.path.expanduser(self.model_path)
#         assert model_path.endswith(('.joblib', '.pkl')), 'model  must be a .joblib or .pkl file.'
#         try:
#             self.svm_model = load(model_path)
#         except FileNotFoundError:
#             print("Not found saved model")
#
#     def detect_ern(self, eeg):
#         if self.svm_model is None:
#             return 0
#         else:
#             return self.svm_model.predict(eeg)


# class Buffer(object):


if __name__ == '__main__':
    __outlet = Outlet(name='new')
    print(__outlet.outlet.get_info().as_xml())


