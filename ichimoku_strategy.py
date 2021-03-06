from strategy import Strategy


class ZigZag:
    def __init__(self, fraction, graph):
        self.peaks = [(0, graph.close(0))]
        i = 1
        while graph.close(i) == graph.close(0):
            i += 1
        direction = 1 if graph.close(i) >= graph.close(0) else -1
        curr_peak = graph.close(i)
        peak_index = i
        self.graph = graph
        for i in range(i, len(graph.ask_candles)):
            if (graph.close(i) - curr_peak) * direction > 0:
                curr_peak = graph.close(i)
                peak_index = i
            elif (graph.close(i) - curr_peak) / (self.peaks[-1][1] - curr_peak) > fraction:
                self.peaks.append((peak_index, curr_peak))
                direction *= -1
                curr_peak = graph.close(i)
                peak_index = i
        i = len(graph.ask_candles) - 1
        self.peaks.append((peak_index, curr_peak))
        self.peaks.append((i, graph.close(i)))

    def __call__(self, index, history_wall):
        assert index < history_wall
        peak_index = 0
        while self.peaks[peak_index][0] < index:
            peak_index += 1
        right_side = min([history_wall, self.peaks[peak_index][0]])
        left_side = self.peaks[peak_index - 1][0]
        return (index - left_side) * (self.graph.close(right_side) - self.graph.close(left_side)) \
               / (right_side - left_side)


class IchimokuStrategy(Strategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_needed = 26
        self.last_close = -1
        self.max_age = 5
        self.zigzag = ZigZag(0.09, self.graph)
    
    def manage_transaction(self, index, direction, multiplier=1.0):
        i = index
        sl = self.sl
        tran_open = self.tran_open
        #times = 1
        while True:
            candle = self.graph.bid_candles[i]
            to_sl = ((candle.low if direction == 1 else candle.high) - sl) * direction
            to_tp = ((candle.low if direction == -1 else candle.high) - self.tp) * direction
            """
            ########################################################################
            Przy wyjsciu z transakcji wypisuje:
                date wyjscia, na jakim poziomie sie skonczylo i wynik
            """
            if to_sl < 0:
                self.last_close = i
                print("Result: date-{}, end-{}, result-{}".format(self.graph.dates[i], sl, sl - tran_open))
                return sl - tran_open
            if to_tp > 0:
                self.last_close = i
                print("Result: date-{}, end-{}, result-{}".format(self.graph.dates[i], self.tp, self.tp - tran_open))
                return self.tp - tran_open
            """
            if candle.close > tran_open + times*(tran_open - self.sl):
                if times == 1:
                    sl = tran_open
                elif times == 4:
                    self.last_close = i
                    return times*(tran_open - self.sl)
                else:
                    sl = self.graph.kijun_sen(i)
                times += 1
            """
            i += 1

    def get_signal(self, index, direction):
        # signal 1 kijun-tenkan cross, kumo adjusting required
        signal1_present = (self.graph.tenkan_sen(index) - self.graph.kijun_sen(index)) * direction > 0 \
            and (self.graph.tenkan_sen(index) - self.graph.senkou_span_A(index - 26)) * direction > 0 \
            and (self.graph.tenkan_sen(index) - self.graph.senkou_span_B(index - 26)) * direction > 0
        wykres1D = self.graphs[0]
        index1D = wykres1D.get_my_index_for(self.graph.dates[index])
        signal1_present = signal1_present and (wykres1D.close(index1D) - wykres1D.kijun_sen(index1D)) * direction > 0
        signal1_age = 1
        while (self.graph.tenkan_sen(index - signal1_age) - self.graph.kijun_sen(index - signal1_age)) * direction > 0:
            signal1_age += 1
        # signal 2 kumo cross
        #signal2_present = (self.graph.senkou_span_A(index) - self.graph.senkou_span_B(index)) * direction > 0
        #signal2_age = 1
        #while (self.graph.senkou_span_A(index - signal2_age) - self.graph.senkou_span_B(index - signal2_age)) * direction > 0:
        #    signal2_age += 1
        # signal 3 graph crossing kumo
        signal3_present = (self.graph.close(index) - self.graph.senkou_span_A(index)) * direction > 0 \
            and (self.graph.close(index) - self.graph.senkou_span_B(index)) * direction > 0
        signal3_age = 1
        while (self.graph.close(index - signal3_age) - self.graph.senkou_span_A(index - signal3_age)) * direction > 0 \
            and (self.graph.close(index - signal3_age) - self.graph.senkou_span_B(index - signal3_age)) * direction > 0:
            signal3_age += 1
        signals = [(t, age) for t, pres, age in [(1, signal1_present, signal1_age),
                   (3, signal3_present, signal3_age)] if pres]
        if signals and min(s[1] for s in signals) <= self.max_age:
            return min(signals, key=lambda x: x[1])
        return (0, 0)

    def stoploss(self, index, signal, signal_type):
        if signal_type == 1:
            return self.graph.kijun_sen(index) - signal * 0.0002
        if signal_type == 3:
            linie = [self.graph.senkou_span_B(index), self.graph.senkou_span_A(index)]
            return min(linie) if signal == 1 else max(linie)
        return None

    def takeprofit(self, index, signal, signal_type):
        week_graph = self.graphs[1]
        week_index = week_graph.get_my_index_for(self.graph.dates[index])
        if signal == 1 or signal == 3:
            return week_graph.najblizszy_opor(week_index)
        elif signal == -1:
            return week_graph.najblizsze_wsparcie(week_index)
        return None

    def check_for_entry(self, index):
        if index <= self.last_close:
            return False
        direction = 1 if self.graph.tenkan_sen(index) > self.graph.tenkan_sen(index - 1) else -1
        #if direction * (self.graph.close(index) - self.graph.close(index - 26)) < 0:
        #    return False
        signal_type, age = self.get_signal(index, direction)
        anti_signal, _ = self.get_signal(index, -direction)
        if not signal_type or anti_signal:
            return False
        stoploss = self.stoploss(index, direction, signal_type)
        takeprofit = self.takeprofit(index, direction, signal_type)
        current = self.graph.ask_close(index)
        if takeprofit is None or stoploss is None:
            return False
        ratio = (takeprofit - current)/(current - stoploss)
        """
        ########################################################################
        Niezaleznie od stosunku takeprofit do stoploss wypisuje:
            index, date, kierunke(1, -1), takeprofit, stoploss, obecna cene i stosunek
        """
        print(index, self.graph.date(index), direction, takeprofit, stoploss, current, ratio)
        if signal_type and ratio > 2.:
            self.sl = stoploss
            self.tp = 3 * current - 2 * stoploss
            self.tran_open = current
            """#######################################################
            W momencie wejscia wypisuje:
                date, kierunek, takeprofit(faktyczny próbowany) i stoploss
            """
            print("Enter: date-{}, direction-{}, edge-{}, sl-{}".format(
                    self.graph.dates[index], direction, self.tp, stoploss))
            return direction
