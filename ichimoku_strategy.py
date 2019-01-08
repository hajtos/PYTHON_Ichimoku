from strategy import Strategy


class IchimokuStrategy(Strategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_close = -1
    
    def manage_transaction(self, index, direction, multiplier=1.0):
        i = index
        sl = self.sl
        tran_open = self.tran_open
        times = 1
        while True:
            candle = self.graph.bid_candles[i]
            if candle.low < sl:
                self.last_close = i
                return sl - tran_open
            if candle.close > tran_open + times*(tran_open - self.sl):
                if times == 1:
                    sl = tran_open
                elif times == 4:
                    self.last_close = i
                    return times*(tran_open - self.sl)
                else:
                    sl = self.graph.kijun_sen(i)
                times += 1
            i += 1

    def get_signal(self, index, direction):
        # signal 1 kijun-tenkan cross, kumo adjusting required
        signal1_present = (self.graph.tenkan_sen(index) - self.graph.kijun_sen(index)) * direction > 0 \
            and (self.graph.tenkan_sen(index) - self.graph.senkou_span_A(index - 26)) * direction > 0 \
            and (self.graph.tenkan_sen(index) - self.graph.senkou_span_B(index - 26)) * direction > 0
        signal1_age = 1
        while (self.graph.tenkan_sen(index - signal1_age) - self.graph.kijun_sen(index - signal1_age)) * direction > 0:
            signal1_age += 1
        # signal 2 kumo cross
        signal2_present = (self.graph.senkou_span_A(index) - self.graph.senkou_span_B(index)) * direction > 0
        signal2_age = 1
        while (self.graph.senkou_span_A(index - signal2_age) - self.graph.senkou_span_B(index - signal2_age)) * direction > 0:
            signal2_age += 1
        # signal 3 graph crossing kumo
        signal3_present = (self.graph.close(index) - self.graph.senkou_span_A(index)) * direction > 0 \
            and (self.graph.close(index) - self.graph.senkou_span_B(index)) * direction > 0
        signal3_age = 1
        while (self.graph.close(index - signal3_age) - self.graph.senkou_span_A(index - signal3_age)) * direction > 0 \
                and (self.graph.close(index - signal3_age) - self.graph.senkou_span_B(index - signal3_age)) * direction > 0:
            signal3_age += 1
        signals = [(t, age) for t, pres, age in [(1, signal1_present, signal1_age), (2, signal2_present, signal2_age),
                                                 (3, signal3_present, signal3_age)] if pres]
        if signals:
            return min(signals, key=lambda x: x[1])
        return (0, 0)

    def stoploss(self, index, signal, signal_type):
        if signal_type == 1 and signal == 1:
            return self.graph.kijun_sen(index)
        return None

    def takeprofit(self, index, signal, signal_type):
        week_graph = self.graphs[1]
        week_index = week_graph.get_my_index_for(index, self.graph.timeframe)
        if signal == 1:
            return week_graph.najblizszy_opor(week_index)
        return None

    def check_for_entry(self, index):
        if index <= self.last_close:
            return False
        direction = 1 if self.graph.tenkan_sen(index) > self.graph.tenkan_sen(index - 1) else -1
        if direction * (self.graph.close(index) - self.graph.close(index - 26)) < 0:
            return False
        signal_type, age = self.get_signal(index, direction)
        anti_signal, _ = self.get_signal(index, -direction)
        if not signal_type or anti_signal:
            return False
        stoploss = self.stoploss(index, direction, signal_type)
        takeprofit = self.takeprofit(index, direction, signal_type)
        current = self.graph.ask_close(index)
        ratio = (takeprofit - current)/(current - stoploss)
        if signal_type and ratio > 2.:
            self.sl = stoploss
            self.tran_open = current
            return True
