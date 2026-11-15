# polymarket-faa-attribution-02 entry: per-market adaptive-volatility quantile forecaster.
# Reads every <id>.in in the input dir, writes <id>.out to the output dir:
# {"forecasts":[{"id","q"}]} with horizon rows of the five quantiles around the last price.
# The spread is set market by market from the recent robust volatility of its own price
# path (mean absolute 1-minute move, last ~6 hours), shrunk toward a fixed anchor and
# clamped, instead of one fixed spread for every market. Deterministic; stdlib only.
import json
import math
import os
from statistics import NormalDist

INPUT_DIR = os.environ.get('MAKEFUN_INPUT_DIR', '/input')
OUTPUT_DIR = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
ANCHOR = 0.0015
W_DATA = 0.60
SIG_MIN, SIG_MAX = 0.0009, 0.0045
WINDOW = 361  # last ~6 hours of minutes


def price6(x):
    return round(min(1.0, max(0.0, x)) * 1e6) / 1e6 + 0.0


def sigma_for(prices):
    if len(prices) < 2:
        return ANCHOR
    tail = prices[-WINDOW:]
    diffs = [abs(tail[i] - tail[i - 1]) for i in range(1, len(tail))]
    mad = sum(diffs) / len(diffs) * 1.2533  # mean abs move -> normal-equivalent sigma
    s = W_DATA * mad + (1 - W_DATA) * ANCHOR
    return min(SIG_MAX, max(SIG_MIN, s))


def forecast_market(prices, horizon, zs):
    if not prices:
        return [[0.5] * len(zs) for _ in range(horizon)]
    x = prices[-1]
    sig = sigma_for(prices)
    rows = []
    for h in range(1, horizon + 1):
        s = sig * math.sqrt(h)
        rows.append([price6(x + z * s) for z in zs])
    return rows


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    nd = NormalDist()
    for name in sorted(os.listdir(INPUT_DIR)):
        if not name.endswith('.in'):
            continue
        with open(os.path.join(INPUT_DIR, name)) as f:
            case = json.load(f)
        zs = [round(nd.inv_cdf(t), 6) for t in case['quantiles']]
        forecasts = [
            {'id': m['id'], 'q': forecast_market(m['prices'], case['horizon_minutes'], zs)}
            for m in case['markets']
        ]
        out = os.path.join(OUTPUT_DIR, name[:-3] + '.out')
        with open(out, 'w') as f:
            f.write(json.dumps({'forecasts': forecasts}) + '\n')


if __name__ == '__main__':
    main()
