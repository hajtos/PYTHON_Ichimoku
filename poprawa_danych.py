"""
Otwiera plik z danymi, dzieli każdą z linijek, łączy odpowiednie symbole 
i zapisuje do nowego pliku. 
"""

plik = open("D:/Documents/FOREX/TESTY/zrodla.txt", "r")
nazwy = [linia.strip() for i, linia in enumerate(plik)]

#file_handle = open("D:/Documents/FOREX/TESTY/USDCAD.csv", "r")

#file_poprawiony = open("D:/Documents/FOREX/TESTY/USDCAD_POPRAWIONY.csv", "w")
file_handle_ask = open(nazwy[0], "r")
file_handle_bid= open(nazwy[1], "r")
file_poprawiony = open(nazwy[2], "w")

for i, (linia1, linia2) in enumerate(zip(file_handle_ask, file_handle_bid)): 
    if i==0:
        do_dopisania_1 = ";".join(linia1.split(",")).strip()
        do_dopisania_2 = ";".join(linia2.split(",")[1:]).strip()
        file_poprawiony.write(do_dopisania_1 + ";" + do_dopisania_2 + "\n" ) 
        continue

    tekst1 = linia1.strip().split(",")
    tekst2 = linia2.split(",")
    time = tekst1[0]
    #candle_open = tekst[1] + "," + tekst[2]
    candle_open_ask = ",".join(tekst1[1:3])
    candle_high_ask = ",".join(tekst1[3:5])
    candle_low_ask = ",".join(tekst1[5:7])
    candle_close_ask = ",".join(tekst1[7:9])
    volume_ask = ",".join(tekst1[9:11])

    candle_open_bid = ",".join(tekst2[1:3])
    candle_high_bid = ",".join(tekst2[3:5])
    candle_low_bid = ",".join(tekst2[5:7])
    candle_close_bid = ",".join(tekst2[7:9])
    volume_bid = ",".join(tekst2[9:11])
    
    file_poprawiony.write(";".join([time,candle_open_ask,candle_high_ask,candle_low_ask,candle_close_ask,volume_ask,\
                                    candle_open_bid,candle_high_bid,candle_low_bid,candle_close_ask,volume_bid])) 
file_poprawiony.close()
print("koniec")
    #2018.08.01 00:00:00,1,30202,1,30207,1,30193,1,30196,61,87
    
    
