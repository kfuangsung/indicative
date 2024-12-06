from collections import namedtuple
from typing import Iterable

import numpy as np
import tulipy as ti
from multimethod import multimethod
from pydantic import Field, PositiveInt
from pydantic.dataclasses import dataclass

from ..datas import PriceDataArray
from ..history import History
from ..mixins import IndicatorMixin
from ..protocols import IndicatorProtocol
from ..types import ArrayFloat64

STOCHTuple = namedtuple("stoch", ["stoch_k", "stoch_d"])
type STOCHOutput = list[STOCHTuple]


@dataclass
class STOCH(IndicatorProtocol, IndicatorMixin):
    pct_k_period: PositiveInt = Field(default=5)
    pct_k_slowing_period: PositiveInt = Field(default=3)
    pct_d_period: PositiveInt = Field(default=3)

    def __ror__(self, other: Iterable):
        return self(other)

    @multimethod
    def compute(
        self, high: ArrayFloat64, low: ArrayFloat64, close: ArrayFloat64
    ) -> STOCHOutput:
        k, d = ti.stoch(
            high,
            low,
            close,
            self.pct_k_period,
            self.pct_k_slowing_period,
            self.pct_d_period,
        )
        return list(map(STOCHTuple._make, zip(k, d)))

    @compute.register
    def _(self, high: Iterable, low: Iterable, close: Iterable) -> STOCHOutput:
        return self.compute(
            np.asarray(high, np.float64),
            np.asarray(low, np.float64),
            np.asarray(close, np.float64),
        )

    @compute.register
    def _(
        self, history: History, fields: list[str] | None = ["high", "low", "close"]
    ) -> STOCHOutput:
        return self.compute(
            history[fields[0]].data, history[fields[1]].data, history[fields[2]].data
        )

    @compute.register
    def _(self, price_data_arr: PriceDataArray) -> STOCHOutput:
        return self.compute(
            price_data_arr.high, price_data_arr.low, price_data_arr.close
        )
