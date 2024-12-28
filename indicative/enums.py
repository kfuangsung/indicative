import enum

from talib._ta_lib import MA_Type as talib_ma_type

__all__ = ["MA_Type"]


class MA_Type(enum.Enum):
    SMA = talib_ma_type.SMA
    EMA = talib_ma_type.EMA
    WMA = talib_ma_type.WMA
    DEMA = talib_ma_type.DEMA
    TEMA = talib_ma_type.TEMA
    TRIMA = talib_ma_type.TRIMA
    KAMA = talib_ma_type.KAMA
    MAMA = talib_ma_type.MAMA
    T3 = talib_ma_type.T3
