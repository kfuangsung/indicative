from __future__ import annotations

import enum
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Self

import pandas as pd
from pydantic import Field, PositiveInt
from pydantic.dataclasses import dataclass

from .datas import PriceDataArray, PriceDataPoint
from .history import History, Record
from .protocols import NamedTupleProtocol

if TYPE_CHECKING:
    from .types import Timestamp


class TimeUnit(enum.StrEnum):
    """
    TimeUnit is an enumeration of time units.
    """

    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"


def calc_timedelta(unit: TimeUnit, n: PositiveInt) -> pd.Timedelta:
    """
    Calculate a pandas Timedelta object.

    Args:
        unit (TimeUnit): The unit of time for the timedelta.
        n (PositiveInt): The number of units for the timedelta.

    Returns:
        pd.Timedelta: A pandas Timedelta object representing the specified duration.
    """
    return pd.Timedelta(n, unit=unit.value)


def calc_next_timestamp(timestamp: Timestamp, timedelta: pd.Timedelta) -> pd.Timestamp:
    """
    Calculate the next timestamp given a starting timestamp and a timedelta.

    Args:
        timestamp (Timestamp): The starting timestamp.
        timedelta (pd.Timedelta): The timedelta to add to the timestamp.

    Returns:
        pd.Timestamp: The resulting timestamp after adding the timedelta.
    """
    return pd.Timestamp(timestamp) + timedelta


def append_latest(history: History, input_: PriceDataPoint) -> None:
    """
    Append the latest PriceDataPoint to the history.

    Args:
        history (History): The history object to which the input data point will be registered.
        input_ (PriceDataPoint): The data point to be appended to the history.

    Returns:
        None
    """
    history.register(input_)


def pop_latest(history: History, input_: PriceDataPoint) -> None:
    """
    Pop the latest data point from the history if it already exists.

    Args:
        history (History): The history object from which the latest data point will be popped.
        input_ (PriceDataPoint): The data point to be compared with the history for uniqueness.

    Returns:
        None
    """
    hist_fields = history.fields
    for field in input_.fields:
        if field in hist_fields and len(history[field]) > 0:
            history[field].pop_latest()


def replace_latest(
    history: History,
    input_: PriceDataPoint,
    next_timestamp: pd.Timestamp,
    timestamp_field: str,
) -> None:
    """
    Replace the latest data point in the history if it's older than the given next timestamp.

    Args:
        history (History): The history object from which the latest data point will be popped and appended.
        input_ (PriceDataPoint): The data point to be compared with the history for uniqueness.
        next_timestamp (pd.Timestamp): The timestamp of the next sample point to be compared with the history.
        timestamp_field (str): The field name of the timestamp in the history object.

    Returns:
        None
    """
    last_hist_time = pd.Timestamp(history[timestamp_field].back())
    while last_hist_time >= input_.timestamp:
        pop_latest(history, input_)
        if len(history[timestamp_field]) == 0:
            break
        last_hist_time = pd.Timestamp(history[timestamp_field].back())

    input_.timestamp = next_timestamp
    return append_latest(history, input_)


@dataclass
class Resampler:
    """
    A resampler to resample a stream of PriceDataPoint into a fixed interval.

    Attributes:
        n (PositiveInt): The number of units for the timedelta.
        unit (TimeUnit): The unit of time for the timedelta.
        timestamp_field (str): The field name of the timestamp in the history object.
    """

    n: PositiveInt = Field(default=1)
    unit: TimeUnit = Field(default=TimeUnit.DAY)
    timestamp_field: str = Field(default="timestamp")

    def resample(self, input_: PriceDataPoint, history: History) -> None:
        """
        Resample a stream of PriceDataPoint into a fixed interval.

        Args:
            input_ (PriceDataPoint): The data point to be resampled.
            history (History): The history object to which the resampled data point will be registered.

        Returns:
            None
        """
        self.check_history(history)

        if self.is_empty_timestamp(history):
            append_latest(history, input_)
            return

        latest_timestamp = history[self.timestamp_field].back()

        next_timestamp = latest_timestamp
        while next_timestamp < input_.timestamp:
            next_timestamp = calc_next_timestamp(
                next_timestamp, calc_timedelta(self.unit, self.n)
            )

        if input_.timestamp > latest_timestamp:
            input_.timestamp = next_timestamp
            append_latest(history, input_)
        else:
            replace_latest(history, input_, next_timestamp, self.timestamp_field)

    def check_history(self, history: History) -> None:
        """
        Check if the history object has the timestamp field. If not, register it.

        Args:
            history (History): The history object to be checked.

        Returns:
            None
        """
        if self.timestamp_field not in history.fields:
            history.register(self.timestamp_field)

    def is_empty_timestamp(self, history: History) -> bool:
        """
        Check if the timestamp field of the history object is empty.

        Args:
            history (History): The history object to be checked.

        Returns:
            bool: True if the timestamp field is empty, False otherwise.
        """
        return len(history[self.timestamp_field]) == 0


@dataclass
class HistoryWithResampler:
    """Combines a History object with a Resampler for managing and resampling data points.

    Attributes:
        history (History): The history object for storing and managing records.
        resampler (Resampler): The resampler object used to resample data points.

    Properties:
        records (list[Record[object]]): The list of records in the history.
        fields (list[str]): The list of field names in the history.
    """

    history: History = Field(default_factory=History)
    resampler: Resampler = Field(default_factory=Resampler)

    @property
    def records(self) -> list[Record[object]]:
        """Gets the records from the history.

        Returns:
            list[Record[object]]: The records in the history.
        """
        return self.history.records

    @property
    def fields(self) -> list[str]:
        """Gets the field names from the history.

        Returns:
            list[str]: The field names in the history.
        """
        return self.history.fields

    def __getitem__(self, name: str) -> Record[object]:
        """Accesses a record by its name.

        Args:
            name (str): The name of the record.

        Returns:
            Record[object]: The record associated with the given name.
        """
        return self.__dict__[name]

    def __or__(self, other: Callable):
        """Allows using the `|` operator for applying a callable to the history.

        Args:
            other (Callable): The callable to be applied.

        Returns:
            Any: The result of applying the callable to the history.
        """
        return other(self.history)

    def __ror__(
        self,
        other: PriceDataPoint | PriceDataArray | NamedTupleProtocol | Iterable,
    ) -> Self:
        """Allows using the `|` operator to add or resample data points into the history.

        Args:
            other (PriceDataPoint | PriceDataArray | NamedTupleProtocol | Iterable): The data to be processed.

        Raises:
            ValueError: If the type of `other` is unsupported.
        """
        if isinstance(other, PriceDataPoint):
            self.resampler.resample(other, self.history)
        elif isinstance(other, PriceDataArray | NamedTupleProtocol | Iterable):
            self.history.register(other)
        else:
            raise ValueError(f"unsupported type {type(other)}")
        return self
