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

SMATuple = namedtuple("sma", ["sma"])
type SMAOutput = list[SMATuple]


@dataclass
class SMA(IndicatorProtocol, IndicatorMixin):
    period: PositiveInt = Field(default=20)

    @multimethod
    def compute(self, close: ArrayFloat64) -> SMAOutput:
        v = ti.sma(close, self.period)
        return list(map(SMATuple._make, zip(v)))

    @compute.register
    def _(self, close: Iterable) -> SMAOutput:
        return self.compute(np.asarray(close, np.float64))

    @compute.register
    def _(self, history: History, field: str | None = "close") -> SMAOutput:
        return self.compute(history[field].data)

    @compute.register
    def _(self, price_data_arr: PriceDataArray) -> SMAOutput:
        return self.compute(price_data_arr.close)
