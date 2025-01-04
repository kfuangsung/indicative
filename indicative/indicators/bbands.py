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
from ..enums import MA_Type

BBANDS_Output = namedtuple("bbands", ["upperband", "middleband", "lowerband"])
type BBANDS_Return = list[BBANDS_Output]


@dataclass
class BBANDS(IndicatorProtocol, IndicatorMixin):
    """
    Bollinger Bands (BBANDS) indicator.

    Attributes:
        timeperiod (PositiveInt): The number of periods for the moving average.
        nbdevup (PositiveInt): The number of standard deviations above the moving average.
        nbdevdn (PositiveInt): The number of standard deviations below the moving average.
        matype (MA_Type): The type of moving average to use.
    """

    timeperiod: PositiveInt = Field(default=5)
    nbdevup: PositiveInt = Field(default=2)
    nbdevdn: PositiveInt = Field(default=2)
    matype: MA_Type = Field(default=MA_Type.SMA)

    @multimethod
    def compute(self, close: Array) -> BBANDS_Return:  # type: ignore
        """
        Computes the Bollinger Bands for a given array of closing prices.

        Args:
            close (Array): An array of closing prices.

        Returns:
            BBANDS_Return: A list of namedtuples containing the upper, middle, and lower bands.
        """
        upperband, middleband, lowerband = talib.BBANDS(
            close, self.timeperiod, self.nbdevup, self.nbdevdn, self.matype.value
        )
        return list(map(BBANDS_Output._make, zip(upperband, middleband, lowerband)))

    @compute.register  # type: ignore
    def _(self, rec: Record) -> BBANDS_Return:
        """
        Computes the Bollinger Bands for a given record.

        Args:
            rec (Record): A record containing data.

        Returns:
            BBANDS_Return: A list of namedtuples containing the upper, middle, and lower bands.
        """
        return self.compute(np.asarray(rec.data, np.float64))

    @compute.register  # type: ignore
    def _(self, history: History, field: str = "close") -> BBANDS_Return:
        """
        Computes the Bollinger Bands using a History object and a specified field.

        Args:
            history (History): A History object containing price data.
            field (str): The field name to be used for computing the Bollinger Bands.

        Returns:
            BBANDS_Return: A list of namedtuples containing the upper, middle, and lower bands.
        """
        return self.compute(history[field])

    @compute.register  # type: ignore
    def _(self, price_data_arr: PriceDataArray) -> BBANDS_Return:
        """
        Computes the Bollinger Bands using a PriceDataArray.

        Args:
            price_data_arr (PriceDataArray): An array containing price data.

        Returns:
            BBANDS_Return: A list of namedtuples containing the upper, middle, and lower bands.
        """
        return self.compute(price_data_arr.close)
