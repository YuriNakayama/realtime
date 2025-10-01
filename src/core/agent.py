import numpy as np
import numpy.typing as npt

class TestAgent:
    def __init__(self):
        pass

    def __call__(self, audio: npt.NDArray[np.int16]) -> npt.NDArray[np.int16]:
        return audio * 2  # 例: 音量を2倍にする