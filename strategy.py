
class Strategy:
    def __init__(self, graph, *graphs):
        self.graph = graph
        self.graphs = list(graphs)
        self.entry_points = []
        self.results = []
        self.start_needed = None
        self.active_transactions = 0
    
    def manage_transaction(self, index, direction, multiplier=1.0):
        raise NotImplementedError

    def check_for_entry(self, index):
        raise NotImplementedError

    def reset_entries(self):
        self.entry_points = []
        self.results = []

    def traverse_graph(self, start_index=0, end_index=None):
        self.reset_entries()
        end_index = end_index or len(self.graph.ask_candles)
        end_index = min(end_index, len(self.graph.ask_candles))
        start_index = start_index
        while start_index < end_index:
            breaking = True
            ref_index = start_index - self.start_needed
            for graph in [self.graph] + self.graphs:
                for name, wsk in graph.wskazniki:
                    if (name, ref_index) not in graph.linie or graph.linie[(name, ref_index)] is None:
                        breaking = False
                        break
                if not breaking:
                    break
            if breaking:
                break
            start_index += 1
        print(start_index)
        for index in range(start_index, end_index):
            direction = self.check_for_entry(index)
            if direction:
                self.entry_points.append((index, direction))
                self.results.append(self.manage_transaction(index, direction))
