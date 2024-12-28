from collections import namedtuple

import numpy as np
import talib
from multimethod import multimethod
from pydantic import Field, PositiveInt
from pydantic.dataclasses import dataclass

from ..datas import PriceDataArray
from ..history import History, Record
from ..mixins import IndicatorMixin
from ..protocols import IndicatorProtocol
from ..types import Array

SMA_Output = namedtuple("sma", ["sma"])
type SMA_Return = list[SMA_Output]


@dataclass
class SMA(IndicatorProtocol, IndicatorMixin):
    """Simple Moving Average (SMA) indicator.

    Attributes:
        timeperiod (PositiveInt): The number of periods for the moving average.
            Defaults to 30.
    """

    timeperiod: PositiveInt = Field(default=30)

    @multimethod
    def compute(self, close: Array) -> SMA_Return:  # type: ignore
        """Computes the SMA indicator for a given array of closing prices.

        Args:
            close (Array): An array of closing prices.

        Returns:
            SMA_Return: A list of namedtuples containing the computed SMA values.
        """
        v = talib.SMA(close, self.timeperiod)
        return list(map(SMA_Output._make, zip(v)))

    @compute.register  # type: ignore
    def _(self, rec: Record) -> SMA_Return:
        """Computes the SMA indicator for a given record.

        Args:
            rec (Record): A record containing data.

        Returns:
            SMA_Return: A list of namedtuples containing the computed SMA values.
        """
        return self.compute(np.asarray(rec.data, np.float64))

    @compute.register  # type: ignore
    def _(self, history: History, field: str = "close") -> SMA_Return:
        """Computes the SMA indicator using a History object and a specified field.

        Args:
            history (History): A History object containing price data.
            field (str): The field name to be used for computing the SMA.
                Defaults to "close".

        Returns:
            SMA_Return: A list of namedtuples containing the computed SMA values.
        """
        return self.compute(history[field])

    @compute.register  # type: ignore
    def _(self, price_data_arr: PriceDataArray) -> SMA_Return:
        """Computes the SMA indicator using a PriceDataArray.

        Args:
            price_data_arr (PriceDataArray): An array containing price data.

        Returns:
            SMA_Return: A list of namedtuples containing the computed SMA values.
        """
        return self.compute(price_data_arr.close)
