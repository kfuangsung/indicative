import enum

from talib._ta_lib import MA_Type as talib_ma_type

__all__ = ["MA_Type"]


class MA_Type(enum.Enum):
    """Moving average types.

    The moving average types supported by the TALib library.

    Attributes:
        SMA (MA_Type): The simple moving average.
        EMA (MA_Type): The exponential moving average.
        WMA (MA_Type): The weighted moving average.
        DEMA (MA_Type): The double exponential moving average.
        TEMA (MA_Type): The triple exponential moving average.
        TRIMA (MA_Type): The triangular moving average.
        KAMA (MA_Type): The Kaufman adaptive moving average.
        MAMA (MA_Type): The MESA adaptive moving average.
        T3 (MA_Type): The triple exponential moving average.
    """

    SMA = talib_ma_type.SMA
    EMA = talib_ma_type.EMA
    WMA = talib_ma_type.WMA
    DEMA = talib_ma_type.DEMA
    TEMA = talib_ma_type.TEMA
    TRIMA = talib_ma_type.TRIMA
    KAMA = talib_ma_type.KAMA
    MAMA = talib_ma_type.MAMA
    T3 = talib_ma_type.T3
