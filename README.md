# Indicative: A Pipeline-Oriented Technical Analysis Library

![logo](https://raw.githubusercontent.com/kfuangsung/indicative/refs/heads/main/docs/_static/original.png)

## About the project

Indicative is a technical analysis library designed with a unique focus on pipeline-oriented programming. While the Python ecosystem already offers numerous technical analysis libraries—whether implemented in pure Python or built in other languages (like C) with Python bindings—Indicative takes a different approach. Drawing inspiration from pipeline-oriented programming paradigms, such as those in F#, it offers a fresh perspective that diverges from the conventional Pythonic style.

## Getting started 

### Prerequisites

Indicative requires [ta-lib-python](https://github.com/TA-Lib/ta-lib-python) version 0.6 or higher. This version supports TA-Lib 0.6.x and is compatible with NumPy 2.

### Installation

```bash
pip install indicative
```

### [Documentation](https://kfuangsung.github.io/indicative)

## Usages

This example download stock data using [yfinance](https://github.com/ranaroussi/yfinance).

### History and Indicator

```python
import pandas as pd
import yfinance as yf
from indicative.adapters import Attr, Back, Filter, Mean, Reverse, Select, Sort, Tail, Front, Head
from indicative.datas import PriceDataArray, PriceDataPoint
from indicative.history import History
from indicative.indicators import ADX, BBANDS, EMA, MACD, RSI, SMA, STOCH
from indicative.resampler import HistoryWithResampler

# download price data 
price = yf.download("aapl", period="1y", group_by="tickers")

# transform to PriceDataArray
data = PriceDataArray.from_dataframe(price["AAPL"])

# history and indicators
input_hist = History()
output_hist = History()
sma = SMA()
adx = ADX()
ema = EMA()
bbands = BBANDS()
rsi = RSI()
stoch = STOCH()
macd = MACD()

# pass data to be stored in input history
# sma calculated from input history 
# output history stored output from sma
data | input_hist | sma | output_hist

# see records in input history 
input_hist.records
# Out:
# [Record(name='timestamp', data=deque([np.datetime64('2024-01-04T00:00:00.000000000'),...
#  Record(name='open', data=deque([np.float64(181.261998363711), np.float64(181.10277101042314),...
#  Record(name='high', data=deque([np.float64(182.19741821935423), np.float64(181.8690061871609),...
#  Record(name='low', data=deque([np.float64(179.99820064627082), np.float64(179.29163655398915),...
#  Record(name='close', data=deque([np.float64(181.02317810058594), np.float64(180.2967071533203),...
#  Record(name='volume', data=deque([np.int64(71983600), np.int64(62303300),...

# see records in output history
# size=1000 is maximum size of Record object
# when maximum size is exceeded the oldest record will be automatically removed.
output_hist.records
# Out:
# [Record(name='sma', data=deque([np.float64(nan),...np.float64(244.5163324991862), np.float64(245.018999226888)]), size=1000)]


# more indicators
# input history already contains all the data 
input_hist | adx | output_hist
input_hist | ema | output_hist
input_hist | bbands | output_hist
input_hist | rsi | output_hist
input_hist | stoch | output_hist
input_hist | macd | output_hist

# output history now contains outputs from all indicators
output_hist.records
# Out:
# [Record(name='sma', data=deque([np.float64(nan),..., np.float64(245.018999226888)]), size=1000),
#  Record(name='adx', data=deque([np.float64(nan),..., np.float64(36.75008298359567)]), size=1000),
#  Record(name='ema', data=deque([np.float64(nan),..., np.float64(245.4047478591999)]), size=1000),
#  Record(name='upperband', data=deque([np.float64(nan),..., np.float64(258.6330803249832)]), size=1000),
#  Record(name='middleband', data=deque([np.float64(nan),..., np.float64(249.08399963378906)]), size=1000),
#  Record(name='lowerband', data=deque([np.float64(nan),..., np.float64(239.5349189425949)]), size=1000),
#  Record(name='rsi', data=deque([np.float64(nan),..., np.float64(45.363794664276504)]), size=1000),
#  Record(name='stoch_k', data=deque([np.float64(nan),..., np.float64(9.83553251451694)]), size=1000),
#  Record(name='stoch_d', data=deque([np.float64(nan),..., np.float64(17.654065843227453)]), size=1000),
#  Record(name='macd', data=deque([np.float64(nan),..., np.float64(3.1771851374329287)]), size=1000),
#  Record(name='macdsignal', data=deque([np.float64(nan),..., np.float64(4.852283278799896)]), size=1000),
#  Record(name='macdhist', data=deque([np.float64(nan),, np.float64(-1.6750981413669672)]), size=1000)]
```

### Adaptor

```python
# gettting last n value of sma from output history
# by default n=10
output_hist | Attr("sma") | Tail()
# Out:
# [np.float64(237.18199869791667),
#  np.float64(238.09066569010417),
#  np.float64(239.03433227539062),
#  np.float64(240.16666615804036),
#  np.float64(241.32633260091146),
#  np.float64(242.34199930826824),
#  np.float64(243.1413324991862),
#  np.float64(243.98866577148436),
#  np.float64(244.5163324991862),
#  np.float64(245.018999226888)]

# getting the last value of adx
output_hist | Attr("adx") | Back()
# Out:
# np.float64(36.75008298359567)

# specify ranges to retrieve values
output_hist | Attr("rsi") | Select(lambda x: x[-10:-5])
# Out:
# [np.float64(67.21181059966862),
#  np.float64(72.33415370070303),
#  np.float64(73.08562963063878),
#  np.float64(75.75026433795774),
#  np.float64(76.4528656758449)]

# find mean of the last 20 values 
output_hist | Attr("stoch_d") | Tail(20) | Mean()
# Out:
# np.float64(73.2506046486207)

# Filter positve value
output_hist | Attr("macdhist") | Tail(50) | Filter(lambda x: x > 0)
# Out:
# [np.float64(0.3394415881799535),
#  np.float64(0.044160937691766655),
#  np.float64(0.15406418593398896),
#  np.float64(0.29613413012799505),
#  np.float64(0.34353315120733835),
#  np.float64(0.44511202306928177),
#  np.float64(0.679610072679347),

# Reverse then select the first value
output_hist | Attr("sma") | Reverse() | Front()
# np.float64(245.018999226888)

# Sort then reverse then select the first 10 values
output_hist | Attr("ema") | Sort() | Reverse() | Head(10)
# [np.float64(245.6627137970819),
#  np.float64(245.54576491362602),
#  np.float64(245.40474786180187),
#  np.float64(245.334625219712),
#  np.float64(244.86115130739958),
#  np.float64(244.12123096046918),
#  np.float64(243.0937304050759),
#  np.float64(242.05191786701),
#  np.float64(241.14032570111684),
#  np.float64(240.2196581292515)]
```

### Supported indicators

- ADX
- BBANDS
- EMA 
- MACD 
- RSI
- SMA 
- STOCH

## License 

Distributed under the MIT License. See [`LICENSE`](https://github.com/kfuangsung/indicative/blob/main/LICENSE) for more information.

## Maintainers 

[indicative](https://github.com/kfuangsung/indicative) is currently maintained by [kfuangsung](https://github.com/kfuangsung) (kachain.f@outlook.com).

## Acknowledgments

[TA-Lib](https://github.com/TA-Lib/ta-lib-python): A widely used technical analysis library