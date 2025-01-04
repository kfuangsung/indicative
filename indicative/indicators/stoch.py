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
from ..enums import MA_Type

STOCH_Output = namedtuple("stoch", ["stoch_k", "stoch_d"])
type STOCH_Return = list[STOCH_Output]


@dataclass
class STOCH(IndicatorProtocol, IndicatorMixin):
    """Stochastic Oscillator (STOCH)

    The Stochastic Oscillator is a momentum indicator that compares the
    closing price of a security to its price range over a given period of time.
    The indicator is used to identify overbought and oversold conditions in the
    market.

    Attributes:
        fastk_period (int): The number of periods used for the fast k line.
        slowk_period (int): The number of periods used for the slow k line.
        slowd_period (int): The number of periods used for the slow d line.
        slowk_matype (MA_Type): The type of moving average used for the slow k line.
        slowd_matype (MA_Type): The type of moving average used for the slow d line.
    """

    fastk_period: PositiveInt = Field(default=5)
    slowk_period: PositiveInt = Field(default=3)
    slowd_period: PositiveInt = Field(default=3)
    slowk_matype: MA_Type = Field(default=MA_Type.SMA)
    slowd_matype: MA_Type = Field(default=MA_Type.SMA)

    @multimethod
    def compute(self, high: Array, low: Array, close: Array) -> STOCH_Return:  # type: ignore
        """Compute the Stochastic Oscillator.

        Args:
            high (Array): An array of high prices.
            low (Array): An array of low prices.
            close (Array): An array of close prices.

        Returns:
            STOCH_Return: A list of namedtuples containing the computed STOCH values.
        """
        k, d = talib.STOCH(
            high,
            low,
            close,
            self.fastk_period,
            self.slowk_period,
            self.slowk_matype.value,
            self.slowd_period,
            self.slowd_matype.value,
        )
        return list(map(STOCH_Output._make, zip(k, d)))

    @compute.register  # type: ignore
    def _(self, high: Record, low: Record, close: Record) -> STOCH_Return:
        """Compute the Stochastic Oscillator using Records.

        Args:
            high (Record): A Record containing high prices.
            low (Record): A Record containing low prices.
            close (Record): A Record containing close prices.

        Returns:
            STOCH_Return: A list of namedtuples containing the computed STOCH values.
        """
        return self.compute(
            np.asarray(high.data, np.float64),
            np.asarray(low.data, np.float64),
            np.asarray(close.data, np.float64),
        )

    @compute.register  # type: ignore
    def _(
        self, history: History, fields: list[str] = ["high", "low", "close"]
    ) -> STOCH_Return:
        """Compute the Stochastic Oscillator using a History object.

        Args:
            history (History): A History object containing price data.
            fields (list[str]): A list of field names to be used for computing the
                Stochastic Oscillator.

        Returns:
            STOCH_Return: A list of namedtuples containing the computed STOCH values.
        """
        return self.compute(history[fields[0]], history[fields[1]], history[fields[2]])

    @compute.register  # type: ignore
    def _(self, price_data_arr: PriceDataArray) -> STOCH_Return:
        """Compute the Stochastic Oscillator using a PriceDataArray object.

        Args:
            price_data_arr (PriceDataArray): A PriceDataArray object containing price
                data.

        Returns:
            STOCH_Return: A list of namedtuples containing the computed STOCH values.
        """
        return self.compute(
            price_data_arr.high, price_data_arr.low, price_data_arr.close
        )
