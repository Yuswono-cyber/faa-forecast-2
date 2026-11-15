# polymarket-faa-attribution-02 entry — adaptive-volatility quantile forecaster

`main.py` (Python 3.13, standard library only) reads every `<id>.in` case in the
input directory and writes `<id>.out` forecasts: for each market, 240 rows of the
five quantiles (5%, 25%, 50%, 75%, 95%) of its Yes price over the next 240 minutes.

The house baseline keeps one fixed spread (sigma 0.0025 per root-minute) for every
market. This entry instead measures each market's own recent volatility — the mean
absolute 1-minute move over its last ~6 hours, converted to a normal-equivalent
sigma — shrinks it toward a fixed anchor (0.0015), clamps it to [0.0009, 0.0045],
and spreads the quantiles around the last price with the usual root-horizon growth.
The median stays at the last price (drift terms tested worse). Deterministic: the
output is a pure function of the case file.

Local check on the kit's six practice cases (five with real recorded futures):
pinball loss 0.322 vs the baseline's 0.393 (about 18% lower).
