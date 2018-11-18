
class Candle:
    def __init__(self, values):
        self.open = values[0]
        self.high = values[1]
        self.low = values[2]
        self.close = values[3]

    @staticmethod
    def merge_candles(candles):
        val_open = candles[0].open
        val_close = candles[-1].close
        val_high = max(c.high for c in candles)
        val_low = min(c.low for c in candles)
        return Candle([val_open, val_high, val_low, val_close])
