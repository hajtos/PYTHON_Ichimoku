from graph import Graph
from indicators import *
import ichimoku_strategy

wykres = Graph()
wykres.load_from_file("ASK.csv", "BID.csv")

wykres_4h = wykres.make_graph_with_timeframe(240)
wykres_4h.register_indicator(ichimoku_kijun_tenkan, "kijun_sen", 28)
wykres_4h.register_indicator(ichimoku_kijun_tenkan, "tenkan_sen", 7)
wykres_4h.register_indicator(ichimoku_senkou_span_A, "senkou_span_A", 28, 56)
wykres_4h.register_indicator(ichimoku_senkou_span_A, "senkou_span_B", 28, 56)
wykres_4h.calculate_all_indicators()
#wykres_4h.save_to_file("test.csv")

wykres_24h = wykres_4h.make_graph_with_timeframe(1440)
wykres_24h.register_indicator(ichimoku_kijun_tenkan, "kijun_sen", 9)
wykres_24h.calculate_all_indicators()

wykres_week = wykres_4h.make_graph_with_timeframe(10080)
wykres_week.register_indicator(najblizszy_opor, "najblizszy_opor", 100, 2)
wykres_week.register_indicator(najblizsze_wsparcie, "najblizsze_wsparcie", 100, 2)
wykres_week.calculate_all_indicators()

ichimoku = ichimoku_strategy.IchimokuStrategy(wykres_4h, wykres_24h, wykres_week)
ichimoku.traverse_graph(0, 2000)

print(ichimoku.results, ichimoku.entry_points, [wykres_4h.dates[i] for i, direct in ichimoku.entry_points])
out = open("costam.csv", "w")
random_index = 1111
out.write("{};{};{}\n".format(wykres_4h.dates[random_index], wykres_4h.linie[("kijun_sen", random_index)],\
          wykres_4h.linie[("tenkan_sen", random_index)]))
out.write("\n".join("{};{};{}".format(res, entry, date) for res, entry, date in \
                    zip(ichimoku.results, ichimoku.entry_points, [wykres_4h.dates[i] for i, direct in ichimoku.entry_points])))
out.close()
