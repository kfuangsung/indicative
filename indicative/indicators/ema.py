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

EMA_Output = namedtuple("ema", ["ema"])
type EMA_Return = list[EMA_Output]


@dataclass
class EMA(IndicatorProtocol, IndicatorMixin):
    """Exponential Moving Average (EMA).

    The Exponential Moving Average (EMA) is a type of moving average that gives more
    weight to more recent prices. It is calculated by taking the average price of a
    security over a specified period of time, with more recent prices given more
    weight.

    Args:
        timeperiod (int): The number of bars to use in the calculation of the EMA.
            Defaults to 30.
    """

    timeperiod: PositiveInt = Field(default=30)

    @multimethod
    def compute(self, close: Array) -> EMA_Return:  # type: ignore
        """Compute the EMA.

        Args:
            close (Array): The array of closing prices.

        Returns:
            EMA_Return: A list of namedtuples containing the computed EMA values.
        """
        v = talib.EMA(close, self.timeperiod)
        return list(map(EMA_Output._make, zip(v)))

    @compute.register  # type: ignore
    def _(self, rec: Record) -> EMA_Return:
        """Compute the EMA using a Record object.

        Args:
            rec (Record): A Record object containing the data.

        Returns:
            EMA_Return: A list of namedtuples containing the computed EMA values.
        """
        return self.compute(np.asarray(rec.data, np.float64))

    @compute.register  # type: ignore
    def _(self, history: History, field: str = "close") -> EMA_Return:
        """Compute the EMA using a History object and a field name.

        Args:
            history (History): A History object containing the data.
            field (str): The name of the field to use for computing the EMA.
                Defaults to "close".

        Returns:
            EMA_Return: A list of namedtuples containing the computed EMA values.
        """
        return self.compute(history[field])

    @compute.register  # type: ignore
    def _(self, price_data_arr: PriceDataArray) -> EMA_Return:
        """Compute the EMA using a PriceDataArray object.

        Args:
            price_data_arr (PriceDataArray): A PriceDataArray object containing the
                data.

        Returns:
            EMA_Return: A list of namedtuples containing the computed EMA values.
        """
        return self.compute(price_data_arr.close)
