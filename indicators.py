

def ichimoku_kijun_tenkan(parameter):
    def indicator(graph, index):
        if index < parameter:
            return 0.
        index += 1
        candles = graph.bid_candles[index - parameter:index]
        local_max = max(c.high for c in candles)
        local_min = min(c.low for c in candles)
        return (local_max + local_min) / 2
    return indicator


def ichimoku_senkou_span_A(parameter1, parameter2):
    kijun = ichimoku_kijun_tenkan(parameter1)
    tenkan = ichimoku_kijun_tenkan(parameter2)
    def indicator(graph, index):
        if index < parameter2 + max([parameter1, parameter2]):
            return 0.
        val_kijun = kijun(graph, index - parameter2)
        val_tenkan = tenkan(graph, index - parameter2)
        return (val_kijun + val_tenkan) / 2
    return indicator


def ichimoku_senkou_span_B(parameter1, parameter2):
    unshifted = ichimoku_kijun_tenkan(parameter2)
    def indicator(graph, index):
        return unshifted(graph, index-parameter1)
    return indicator


def ichimoku_chikou_span(parameter):
    def indicator(graph, index):
        if index < parameter:
            return 0.
        return graph.bid_candles[index - parameter].close
    return indicator


def najblizszy_opor(history_length, window_size):
    def indicator(graph, index):
        opor = 999999
        for i in range(index - history_length, index - window_size):
            if i < window_size:
                continue
            candles = graph.bid_candles[i-window_size: i+window_size+1]
            if max(c.close for c in candles) == graph.bid_candles[i].close and\
                graph.bid_candles[i].close < opor and graph.close(i) > graph.close(index):
                    opor = graph.bid_candles[i].close
        return opor if opor < 999999 else None
    return indicator


def najblizsze_wsparcie(history_length, window_size):
    def indicator(graph, index):
        wsparcie = 0
        for i in range(index - history_length, index - window_size):
            if i < window_size:
                continue
            candles = graph.bid_candles[i-window_size: i+window_size+1]
            if min(c.close for c in candles) == graph.bid_candles[i].close and\
                graph.bid_candles[i].close > wsparcie and graph.close(i) < graph.close(index):
                    wsparcie = graph.bid_candles[i].close
        return wsparcie if wsparcie > 0 else None
    return indicator
