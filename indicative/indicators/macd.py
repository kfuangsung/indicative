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

MACD_Output = namedtuple("macd", ["macd", "macdsignal", "macdhist"])
type MACD_Return = list[MACD_Output]


@dataclass
class MACD(IndicatorProtocol, IndicatorMixin):
    """Moving Average Convergence Divergence (MACD).

    The MACD is a widely used indicator that plots the difference between a
    short-term and long-term moving average of a security's price. The MACD is
    calculated by subtracting the long-term moving average from the short-term
    moving average.

    Args:
        fast_period (PositiveInt): The number of bars used to calculate the
            fast moving average. Defaults to 12.
        slow_period (PositiveInt): The number of bars used to calculate the
            slow moving average. Defaults to 26.
        signal_period (PositiveInt): The number of bars used to calculate the
            signal line. Defaults to 9.

    Returns:
        MACD_Return: A list of namedtuples containing the MACD, MACD signal and
            MACD histogram values.
    """

    fast_period: PositiveInt = Field(default=12)
    slow_period: PositiveInt = Field(default=26)
    signal_period: PositiveInt = Field(default=9)

    @multimethod
    def compute(self, close: Array) -> MACD_Return:  # type: ignore
        """Compute the MACD.

        Args:
            close (Array): A numpy array of close prices.

        Returns:
            MACD_Return: A list of namedtuples containing the MACD, MACD signal
                and MACD histogram values.
        """
        macd, macdsignal, macdhist = talib.MACD(
            close, self.fast_period, self.slow_period, self.signal_period
        )
        return list(map(MACD_Output._make, zip(macd, macdsignal, macdhist)))

    @compute.register  # type: ignore
    def _(self, rec: Record) -> MACD_Return:
        """Compute the MACD.

        Args:
            rec (Record): A Record object.

        Returns:
            MACD_Return: A list of namedtuples containing the MACD, MACD signal
                and MACD histogram values.
        """
        return self.compute(np.asarray(rec.data, np.float64))

    @compute.register  # type: ignore
    def _(self, history: History, field: str = "close") -> MACD_Return:
        """Compute the MACD.

        Args:
            history (History): A History object.
            field (str): The field to compute the MACD for. Defaults to "close".

        Returns:
            MACD_Return: A list of namedtuples containing the MACD, MACD signal
                and MACD histogram values.
        """
        return self.compute(history[field])

    @compute.register  # type: ignore
    def _(self, price_data_arr: PriceDataArray) -> MACD_Return:
        """Compute the MACD.

        Args:
            price_data_arr (PriceDataArray): A PriceDataArray object.

        Returns:
            MACD_Return: A list of namedtuples containing the MACD, MACD signal
                and MACD histogram values.
        """
        return self.compute(price_data_arr.close)
