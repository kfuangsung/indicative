from collections import namedtuple

import numpy as np
from multimethod import multimethod
from pydantic import Field, PositiveInt
from pydantic.dataclasses import dataclass
import talib

from ..datas import PriceDataArray
from ..history import History, Record
from ..mixins import IndicatorMixin
from ..protocols import IndicatorProtocol
from ..types import Array

ADX_Output = namedtuple("adx", ["adx"])
type ADX_Return = list[ADX_Output]


@dataclass
class ADX(IndicatorProtocol, IndicatorMixin):
    """
    Computes the Average Directional Index (ADX).

    The Average Directional Index (ADX) is a technical indicator that measures the
    strength of a trend. It is based on the difference between the highest and lowest
    prices over a given period of time. The ADX is calculated as the absolute value of
    the difference between the highest and lowest prices divided by the sum of the
    absolute values of the differences between consecutive prices.

    Attributes:
        timeperiod (int): The number of periods to use for the calculation of the ADX.
    """

    timeperiod: PositiveInt = Field(default=14)

    @multimethod
    def compute(self, high: Array, low: Array, close: Array) -> ADX_Return:  # type: ignore
        """
        Computes the Average Directional Index (ADX) for a given set of high, low,
        and close price data.

        Args:
            high (Array): An array of high prices.
            low (Array): An array of low prices.
            close (Array): An array of close prices.

        Returns:
            STOCH_Return: A list of namedtuples containing the computed ADX values.
        """

        v = talib.ADX(high, low, close, self.timeperiod)
        return list(map(ADX_Output._make, zip(v)))

    @compute.register  # type: ignore
    def _(self, high: Record, low: Record, close: Record) -> ADX_Return:
        """
        Computes the Average Directional Index (ADX) using high, low, and close
        price data records.

        Args:
            high (Record): A record containing high prices.
            low (Record): A record containing low prices.
            close (Record): A record containing close prices.

        Returns:
            STOCH_Return: A list of namedtuples containing the computed ADX values.
        """

        return self.compute(
            np.asarray(high.data, np.float64),
            np.asarray(low.data, np.float64),
            np.asarray(close.data, np.float64),
        )

    @compute.register  # type: ignore
    def _(
        self, history: History, fields: list[str] = ["high", "low", "close"]
    ) -> ADX_Return:
        """
        Computes the Average Directional Index (ADX) using a History object and a
        list of field names.

        Args:
            history (History): A History object containing price data.
            fields (list[str]): A list of field names to be used for computing the ADX.

        Returns:
            STOCH_Return: A list of namedtuples containing the computed ADX values.
        """
        return self.compute(history[fields[0]], history[fields[1]], history[fields[2]])

    @compute.register  # type: ignore
    def _(self, price_data_arr: PriceDataArray) -> ADX_Return:
        """
        Computes the Average Directional Index (ADX) using a PriceDataArray object.

        Args:
            price_data_arr (PriceDataArray): A PriceDataArray object containing price data.

        Returns:
            STOCH_Return: A list of namedtuples containing the computed ADX values.
        """
        return self.compute(
            price_data_arr.high, price_data_arr.low, price_data_arr.close
        )
