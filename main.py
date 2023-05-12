"""Starts communication with NOL program and logs the data"""

import os
import logging
import logging.config
import xml.etree.ElementTree as ET
import datetime

from bossa import api
from messaging.incoming import ReceiveTemplates as rt
from messaging.outgoing import Order

logging.config.fileConfig('./config/base.conf')
logger = logging.getLogger('mem')

path = '_data/'
files = {}

if not os.path.isdir(path):
    os.makedirs(path)


def save_to_file(symbol: str, core_data: tuple) -> None:
    if symbol not in files:  #if ((not plik in pliki) and (len(odczyt.split(',')) == 4)):
        files[symbol] = open(path + symbol + '.txt', 'a+')
    f = files[symbol]
    f.write(','.join(item for item in core_data) + '\n')
    f.flush()


def extract_mkt_data(xml_str):
    try:
        root = ET.fromstring(xml_str)
    except:
        return
    else:
        if root.tag == 'MktDataInc':
                symbol = root[0][0].attrib.get('Sym')
                now = datetime.datetime.now()
                tdate = now.date().strftime('%Y-%m-%d')
                ttime = now.time().strftime('%H:%M:%S.%f')
                for child in root:
                    if child.attrib.get('Typ') == '0' or child.attrib.get('Typ') == '1':
                        core_data = (tdate, ttime, child.attrib.get('Typ'), 
                            child.attrib.get('Px'), child.attrib.get('Sz'), 
                            child.attrib.get('NumOfOrds'), child.attrib.get('MDPxLvl'))
                    elif child.attrib.get('Typ') == '2':
                        core_data = (tdate, ttime, child.attrib.get('Typ'), child.attrib.get('Px'),
                            child.attrib.get('Sz'), child.attrib.get('Tm'))
                    elif child.attrib.get('Typ') == 'B':
                        core_data = (tdate, ttime, child.attrib.get('Typ'), child.attrib.get('Sz'),
                            child.attrib.get('Tov'))
                    else:
                        continue
                    save_to_file(symbol, core_data)


tickers = """F11BH23 FACPH23 FALEH23 FALRH23 FATTH23 FBMLH23 FCCCH23 FCDRH23 FCHFH23 FCIEH23 FCIGH23 FCPSH23 FDNPH23 FENAH23 FEUHH23 FEURH23 FFINH23 FGBPH23 FGMSH23 FGPWH23 FINGH23 FJSWH23 FKGHH23 FKRUH23 FKTYH23 FLPPH23 FLVCH23 FLWBH23 FMABH23 FMBKH23 FMILH23 FMRCH23 FOPLH23 FPCOH23 FPEOH23 FPGEH23 FPKNH23 FPKOH23 FPLWH23 FPXMH23 FPZUH23 FSPLH23 FTENH23 FTPEH23 FUSDH23 FW20H2320 FW40H23 FXTBH23""".split()
tickers += ['VOTUM', 'CCC', 'ARCTIC', 'SUNEX', 'JSW', 'LPP', 'MILLENNIUM', 'ALIOR', 'CIECH', 'MIRBUD', 'EUROTEL']

bossa = api()
tickers = ['OW20F232000', 'OW20R232000']
options_pop = ['OW20E232000','OW20Q231850','OW20R231800','OW20F232100','OW20Q231800','OW20Q231900','OW20Q231925',
               'OW20E232050','OW20Q231950','OW20F231900','OW20Q231750','OW20R231850','OW20C242300','OW20E231950',
               'OW20F231850','OW20Q231975','OW20R231600','OW20U231900','OW20I231900','OW20Q231825','OW20Q231875',
               'OW20R231700','OW20R231900','OW20E231900','OW20E232025','OW20F231700','OW20F231950','OW20F232000',
               'OW20G232100','OW20Q231775','OW20R231750','OW20R232000','OW20S231750','OW20U231600','OW20U231700',
               'OW20C241600','OW20C242000','OW20E231975','OW20F232050','OW20I232200','OW20L231900','OW20L232000',
               'OW20O241300','OW20O241600','OW20R231950','OW20R232300','OW20S231700','OW20S231850','OW20U231400',
               'OW20U231500','OW20X231700','OW20X231800','OW20C241300','OW20C241400','OW20C241500','OW20C241700',
               'OW20C241800','OW20C241900','OW20C242100','OW20C242200','OW20E231300','OW20E231325','OW20E231350',
               'OW20E231375','OW20E231400','OW20E231425','OW20E231450','OW20E231475','OW20E231500','OW20E231525',
               'OW20E231550','OW20E231575','OW20E231600','OW20E231625','OW20E231650','OW20E231675','OW20E231700',
               'OW20E231725','OW20E231750','OW20E231775','OW20E231800','OW20E231825','OW20E231850','OW20E231875',
               'OW20E231925','OW20E232075','OW20E232100','OW20E232125','OW20E232150','OW20E232175','OW20E232200',
               'OW20E232225','OW20E232250','OW20E232275','OW20E232300','OW20E232325','OW20F231000','OW20F231050']

feed = bossa.start(options_pop)

# W celu zlozenia zlecenia
# wybierz domyslne konto gdzie beda wysylane zlecenia
# bossa.select_account("607035 PLN")
# bossa.send_order("SUNEX", "1", 1, Orders.Limit, 22.0)
# 
# albo
# bossa.send_order("SUNEX", "1", 1, Orders.Limit, 22.0, "607035 PLN")

while True:
    data = feed.receive()
    if data[1] != 'H':
        logger.info(data)
        extract_mkt_data(data)
