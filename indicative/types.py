from datetime import datetime

import numpy as np
import numpy.typing as npt
from pandas import Timestamp as pdts
from pydantic import PositiveFloat, PositiveInt

type PositiveRealNumber = PositiveInt | PositiveFloat
type Array = np.ndarray
type ArrayFloat64 = npt.NDArray[np.float64]
type ArrayInt64 = npt.NDArray[np.int64]
type ArrayDatetime64 = npt.NDArray[np.datetime64]
type DataframeColumnNameMapping = dict[str, str]
type Timestamp = datetime | pdts | np.datetime64
type ListFloat = list[float]
