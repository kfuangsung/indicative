import numpy as np
import pandas as pd
from typing import Self
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict, PositiveInt
from .types import (
    Timestamp,
    PositiveRealNumber,
    ArrayDatetime64,
    ArrayFloat64,
    ArrayInt64,
    DataframeColumnNameMapping,
)
from .constants import DEFAULT_DATAFRAME_COLUMN_NAME_MAPPING


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class PriceDataPoint:
    timestamp: Timestamp
    open: PositiveRealNumber
    high: PositiveRealNumber
    low: PositiveRealNumber
    close: PositiveRealNumber
    volume: PositiveInt


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class PriceDataArray:
    timestamp: ArrayDatetime64
    open: ArrayFloat64
    high: ArrayFloat64
    low: ArrayFloat64
    close: ArrayFloat64
    volume: ArrayInt64

    @classmethod
    def from_dataframe(
        self,
        df: pd.DataFrame,
        column_names: DataframeColumnNameMapping
        | None = DEFAULT_DATAFRAME_COLUMN_NAME_MAPPING,
    ) -> Self:
        # pandas.Series to numpy.Array
        # type is int64 if 'volume' else float64
        input_ = {
            k: df.loc[:, v].to_numpy(dtype=np.int64 if k == "volume" else np.float64)
            for k, v in column_names.items()
        }
        input_["timestamp"] = pd.to_datetime(df.index).to_numpy(dtype=np.datetime64)
        return self(**input_)
