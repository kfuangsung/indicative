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

RSI_Output = namedtuple("rsi", ["rsi"])
type RSI_Return = list[RSI_Output]


@dataclass
class RSI(IndicatorProtocol, IndicatorMixin):
    """Computes the Relative Strength Index (RSI) for a given set of price data.

    The Relative Strength Index (RSI) is a technical indicator used to measure the
    strength of a trend. It is based on the ratio of the average gain of up days to the
    average loss of down days over a given period of time.

    Attributes:
        timeperiod (int): The number of periods to use for the calculation of the RSI.
    """

    timeperiod: PositiveInt = Field(default=14)

    @multimethod
    def compute(self, close: Array) -> RSI_Return:  # type: ignore
        """Computes the Relative Strength Index (RSI) for a given set of close prices.

        Args:
            close (Array): An array of close prices.

        Returns:
            RSI_Return: A list of namedtuples containing the computed RSI values.
        """
        v = talib.RSI(close, self.timeperiod)
        return list(map(RSI_Output._make, zip(v)))

    @compute.register  # type: ignore
    def _(self, rec: Record) -> RSI_Return:
        """Computes the Relative Strength Index (RSI) using a Record object.

        Args:
            rec (Record): A Record object containing close prices.

        Returns:
            RSI_Return: A list of namedtuples containing the computed RSI values.
        """
        return self.compute(np.asarray(rec.data, np.float64))

    @compute.register  # type: ignore
    def _(self, history: History, field: str = "close") -> RSI_Return:
        """Computes the Relative Strength Index (RSI) using a History object and a
        list of field names.

        Args:
            history (History): A History object containing price data.
            field (str): A field name to be used for computing the RSI.

        Returns:
            RSI_Return: A list of namedtuples containing the computed RSI values.
        """
        return self.compute(history[field])

    @compute.register  # type: ignore
    def _(self, price_data_arr: PriceDataArray) -> RSI_Return:
        """Computes the Relative Strength Index (RSI) using a PriceDataArray object.

        Args:
            price_data_arr (PriceDataArray): A PriceDataArray object containing close
                prices.

        Returns:
            RSI_Return: A list of namedtuples containing the computed RSI values.
        """
        return self.compute(price_data_arr.close)
