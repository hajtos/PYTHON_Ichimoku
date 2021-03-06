from graph import Graph
from indicators import *
import ichimoku_strategy

#wykres = Graph()
#wykres.load_from_file("ASK.csv", "BID.csv")

katalog = "EURAUD"
wykres_4h = Graph()
wykres_4h.load_from_file(katalog+"/Ask_4_Hours.csv", katalog+"/BID_4_Hours.csv")
wykres_4h.register_indicator(ichimoku_kijun_tenkan, "kijun_sen", 26)
wykres_4h.register_indicator(ichimoku_kijun_tenkan, "tenkan_sen", 9)
wykres_4h.register_indicator(ichimoku_senkou_span_A, "senkou_span_A", 9, 26)
wykres_4h.register_indicator(ichimoku_senkou_span_B, "senkou_span_B", 26, 52)
wykres_4h.calculate_all_indicators()
wykres_4h.save_to_file("test.csv")

wykres_24h = Graph()
wykres_24h.load_from_file(katalog+"/Ask_Daily.csv", katalog+"/BID_Daily.csv")
wykres_24h.register_indicator(ichimoku_kijun_tenkan, "kijun_sen", 9)
wykres_24h.calculate_all_indicators()
#wykres_24h.save_to_file("test_24h.csv")

wykres_week = Graph()
wykres_week.load_from_file(katalog+"/Ask_Weekly.csv", katalog+"/BID_Weekly.csv")
wykres_week.register_indicator(najblizszy_opor, "najblizszy_opor", 1000, 2)
wykres_week.register_indicator(najblizsze_wsparcie, "najblizsze_wsparcie", 1000, 2)
wykres_week.calculate_all_indicators()
#wykres_week.save_to_file("test_tyg.csv")

"""
W pliku ichimoku_strategy zostawilem kilka komentarzy oznaczonych #####
"""

ichimoku = ichimoku_strategy.IchimokuStrategy(wykres_4h, wykres_24h, wykres_week)
ichimoku.traverse_graph('2011.11.01 00:00:00', '2012.02.01 00:00:00')

#print(ichimoku.results, ichimoku.entry_points, [wykres_4h.dates[i] for i, direct in ichimoku.entry_points])
out = open("costam.csv", "w")
random_index = 1111
out.write("{};{};{}\n".format(wykres_4h.dates[random_index], wykres_4h.linie[("kijun_sen", random_index)],\
          wykres_4h.linie[("tenkan_sen", random_index)]))
out.write("\n".join("{};{};{}".format(res, entry, date) for res, entry, date in \
                    zip(ichimoku.results, ichimoku.entry_points, [wykres_4h.dates[i] for i, direct in ichimoku.entry_points])))
out.close()
