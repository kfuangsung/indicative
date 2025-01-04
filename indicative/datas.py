from typing import Self

import numpy as np
import pandas as pd
from pydantic import ConfigDict, PositiveInt
from pydantic.dataclasses import dataclass

from .constants import DEFAULT_DATAFRAME_COLUMN_NAME_MAPPING
from .types import (
    ArrayDatetime64,
    ArrayFloat64,
    ArrayInt64,
    DataframeColumnNameMapping,
    PositiveRealNumber,
    Timestamp,
)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class PriceDataPoint:
    """A data point representing a trade in a market.

    Attributes:
        timestamp: The timestamp of the trade.
        open: The opening price of the trade.
        high: The highest price of the trade.
        low: The lowest price of the trade.
        close: The closing price of the trade.
        volume: The volume of the trade.
    """

    timestamp: Timestamp
    open: PositiveRealNumber
    high: PositiveRealNumber
    low: PositiveRealNumber
    close: PositiveRealNumber
    volume: PositiveInt

    @property
    def fields(self) -> list[str]:
        """Returns a list of the field names of the data point."""
        return list(self.__dict__.keys())


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class PriceDataArray:
    """A data structure representing a market price dataset.

    Attributes:
        timestamp: The timestamps of the trades.
        open: The opening prices of the trades.
        high: The highest prices of the trades.
        low: The lowest prices of the trades.
        close: The closing prices of the trades.
        volume: The volumes of the trades.
    """

    timestamp: ArrayDatetime64
    open: ArrayFloat64
    high: ArrayFloat64
    low: ArrayFloat64
    close: ArrayFloat64
    volume: ArrayInt64

    @property
    def fields(self) -> list[str]:
        """Returns a list of the field names of the data array."""
        return list(self.__dict__.keys())

    @classmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame,
        column_names: DataframeColumnNameMapping = DEFAULT_DATAFRAME_COLUMN_NAME_MAPPING,
    ) -> Self:
        """Creates a PriceDataArray from a pandas.DataFrame.

        Args:
            df: The pandas.DataFrame containing the data.
            column_names: The column names of the fields in the DataFrame,
                defaults to DEFAULT_DATAFRAME_COLUMN_NAME_MAPPING.

        Returns:
            A PriceDataArray object.
        """
        # pandas.Series to numpy.Array
        # type is int64 if 'volume' else float64
        input_ = {
            k: df.loc[:, v].to_numpy(dtype=np.int64 if k == "volume" else np.float64)
            for k, v in column_names.items()
        }
        input_["timestamp"] = pd.to_datetime(df.index).to_numpy(dtype=np.datetime64)
        return cls(**input_)
