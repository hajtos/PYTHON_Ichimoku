from candle import Candle
from types import MethodType


def to_float(s):
    return float(s.replace(",", "."))


class Graph:
    def __init__(self):
        self.linie = {}
        self.ask_candles = []
        self.bid_candles = []
        self.dates = []
        self.currency = ""
        self.timeframe = 1
        self.wskazniki = []

    @staticmethod
    def candles_from_file(filename):
        with open(filename) as plik:
            linie = plik.read().split("\n")[1:-1]
            values = [l.split(";") for l in linie]
            dates = [v[0] for v in values]
            candles = [Candle([to_float(s) for s in v[1:5]]) for v in values]
        return dates, candles

    def load_from_file(self, filename_ask, filename_bid):
        self.dates, self.ask_candles = self.candles_from_file(filename_ask)
        self.date = MethodType(lambda self, i: self.dates[i], self)
        for attr_name in ["high", "low", "open", "close"]:
            setattr(self, "ask_"+attr_name, MethodType(lambda self, i: getattr(self.ask_candles[i], attr_name), self))
        _, self.bid_candles = self.candles_from_file(filename_bid)
        for attr_name in ["high", "low", "open", "close"]:
            setattr(self, attr_name, MethodType(lambda self, i: getattr(self.bid_candles[i], attr_name), self))

    def get_my_index_for(self, index, base_interval):
        return base_interval * index // self.timeframe

    def make_graph_with_timeframe(self, interval):
        relative = interval / self.timeframe
        assert int(relative) == relative
        relative = int(relative)
        new_graph = Graph()
        new_graph.timeframe = interval
        new_graph.currency = self.currency
        for index in range(0, len(self.ask_candles) + 1 - relative, relative):
            new_graph.ask_candles.append(Candle.merge_candles(self.ask_candles[index:index+relative]))
            new_graph.bid_candles.append(Candle.merge_candles(self.bid_candles[index:index+relative]))
            new_graph.dates.append(self.dates[index])
        return new_graph

    def register_indicator(self, func, name, *params):
        self.wskazniki.append((name, func(*params)))
        setattr(self, name, MethodType(lambda self, i: self.linie.get((name, i)), self))

    def calculate_all_indicators(self):
        self.linie = {}
        for name, wsk in self.wskazniki:
            for index in range(len(self.ask_candles)):
                self.linie[(name, index)] = wsk(self, index)

    def save_to_file(self, filename):
        with open(filename, "w") as plik:
            first_line = "Time (UTC);Open;High;Low;Close"
            if self.wskazniki:
                first_line += ";" + ";".join(wsk[0] for wsk in self.wskazniki)
            plik.write(first_line + "\n")
            for i, candle in enumerate(self.bid_candles):
                line = "{};{};{};{};{}".format(self.dates[i], candle.open, candle.high, candle.low, candle.close)
                if self.wskazniki:
                    line += ";" + ";".join(str(self.linie.get((wsk[0], i), "")) for wsk in self.wskazniki)
                plik.write(line+"\n")
