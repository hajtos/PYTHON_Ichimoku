from strategy import Strategy

class IchimokuStrategy(Strategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_close = -1
    
    def manage_transaction(self, index, multiplier=1.0):
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
                    sl = self.graph.linie[("kijun_sen", i)]
                times += 1
            i+=1

    def get_signal(self, index):
        graph4h = self.graph
        graph24h = self.graphs[0]
        index_24h = graph24h.get_my_index_for(index, graph4h.timeframe)
        if graph4h.linie[("tenkan_sen", index)] > graph4h.linie[("kijun_sen", index)]:
            if graph4h.bid_candles[index].close > graph4h.bid_candles[index - 26].close \
                and graph24h.linie[("kijun_sen", index_24h)] < graph24h.bid_candles[index_24h].close:
                return (1, 1, 0)
        return (0, 0, 0)

    def stoploss(self, index, signal, signal_type):
        if signal_type == 1 and signal == 1:
            return self.graph.linie[("kijun_sen", index)]
        return None

    def takeprofit(self, index, signal, signal_type):
        week_graph = self.graphs[1]
        week_index = week_graph.get_my_index_for(index, self.graph.timeframe)
        if signal == 1:
            return week_graph.linie[("najblizszy_opor", week_index)]
        return None

    def check_for_entry(self, index):
        if index <= self.last_close:
            return False
        signal, signal_type, age = self.get_signal(index)
        if not signal:
            return False
        stoploss = self.stoploss(index, signal, signal_type)
        takeprofit = self.takeprofit(index, signal, signal_type)
        current = self.graph.ask_candles[index].close
        ratio = (takeprofit - current)/(current - stoploss)
        if signal and ratio > 2.:
            self.sl = stoploss
            self.tran_open = current
            return True
