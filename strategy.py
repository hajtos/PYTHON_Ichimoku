
class Strategy:
    def __init__(self, graph, *graphs):
        self.graph = graph
        self.graphs = graphs
        self.entry_points = []
        self.results = []
        self.active_transactions = 0
    
    def manage_transaction(self, index, multiplier=1.0):
        raise NotImplementedError

    def check_for_entry(self, index):
        raise NotImplementedError

    def reset_entries(self):
        self.entry_points = []
        self.results = []

    def traverse_graph(self, start_index=0, end_index=None):
        self.reset_entries()
        end_index = end_index or len(self.graph.ask_candles)
        for index in range(start_index, end_index):
            if self.check_for_entry(index):
                self.entry_points.append(index)
                self.results.append(self.manage_transaction(index))
