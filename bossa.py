#  Main entry point for bossa api

import logging
import logging.config
import threading
import xml.etree.ElementTree as ET
import typing
import datetime
from collections import deque


# import yaml
from messaging.outgoing import FIXML_mes as fm, EntryType, Order, TimeInForce
from messaging.incoming import ReceiveTemplates as recv
from connector.nol import SyncConnection, AsyncConnection


class api:
    """Bossapi connection class
    """
    def __init__(self) -> None:
        self.accounts = {}
        self.acc_cash = None
        self.acc_derivatives = None
        self.base_account = None
        self.acc_ike = None
        self.portfolio = []
        self.orders = []
        self.log = None
        self.messages = None
        self.news = []
        self.perf = []
        self.instruments = {}
        
        self.ordb = {}
        self.ordb_h = {}
        self.tcks = {}
        
        self.logs = []
        self.stats = []
        self.strats = {}
        self.steps = {}
        self.files = {}

        


    def start_background(self, symbols):
        self.symbols = symbols
        msg_t = threading.Thread(target=self.msg_thread, args=(symbols,),
         daemon=True)
        self.run = True
        msg_t.start()

    def install_queues(self, tr: deque, book: deque, ords: deque, fills):
        self.transactions = tr
        self.ord_book = book
        self.orders = ords
        self.fills = fills


    def dispatch(self, xml_str: str) -> None:
        """Dispatch market data to queues

        Args:
            xml_str (str): NOL message

        Returns:
            _type_: _description_
        """
        try:
            root = ET.fromstring(xml_str)
            if root.tag == 'MktDataInc':
                symbol = root[0][0].attrib.get('Sym')
                now = datetime.datetime.now()
                # tdate = now.date().strftime('%Y-%m-%d')
                # ttime = now.time().strftime('%H:%M:%S.%f')
                for child in root:
                    # orderbook
                    if child.attrib.get('Typ') == EntryType.Bid.value or \
                        child.attrib.get('Typ') == EntryType.Offer.value:
                        orb = (child.attrib.get('Typ'), now, child.attrib.get('Px'),
                            int(child.attrib.get('Sz')), int(child.attrib.get('NumOfOrds')),
                            child.attrib.get('MDPxLvl'))
                        self.ordb.appendleft(orb)
                    # trades
                    elif child.attrib.get('Typ') == EntryType.Trade.value:
                        tr = (symbol, child.attrib.get('Typ'), child.attrib.get('Tm'),
                            float(child.attrib.get('Px')), int(child.attrib.get('Sz')))
                        self.transactions.appendleft(tr)
                    # tradesvolue
                    elif child.attrib.get('Typ') == EntryType.TradeVolume.value:
                        vol = (symbol, child.attrib.get('Typ'), int(child.attrib.get('Sz')), float(child.attrib.get('Tov')))
                        self.transactions.appendleft(vol)
                    # Open interest
                    elif child.attrib.get('Typ') == EntryType.OpenInterest.value:
                        oi = (symbol, child.attrib.get('Typ'), int(child.attrib.get('Sz'))) #float(child.attrib.get('Tov'))
                        self.transactions.appendleft(oi)
                    # elif child.attrib.get('Typ') == EntryType.IndexValue.value:
                        # mrk_data.append((child.attrib.get('Typ'), float(child.attrib.get('Px'))))
                    # Open price
                    elif child.attrib.get('Typ') == EntryType.OpenPrice.value:
                        self.transactions.appendleft((symbol, child.attrib.get('Typ'), float(child.attrib.get('Px'))))
                    elif child.attrib.get('Typ') == EntryType.HighPrice.value:
                        self.transactions.appendleft((symbol, child.attrib.get('Typ'), float(child.attrib.get('Px'))))
                    elif child.attrib.get('Typ') == EntryType.LowPrice.value:
                        self.transactions.appendleft((symbol, child.attrib.get('Typ'), float(child.attrib.get('Px'))))
                    elif child.attrib.get('Typ') == EntryType.RefPrice.value:
                        self.transactions.appendleft((symbol, child.attrib.get('Typ'), float(child.attrib.get('Px'))))
                    else:
                        continue
            
            elif root.tag == 'ExecRpt':
                symbol = root[0].attrib.get('Sym')
                qty = root
                phase = root.attrib.get('SesSub')
                stat = root.attrib.get('Stat') if root.attrib.get('Stat') else ''
                self.fills.appendleft((symbol, phase, stat))
            
            elif root.tag == 'TrdgSesStat':
                symbol = root[0].attrib.get('Sym')
                phase = root.attrib.get('SesSub')
                stat = root.attrib.get('Stat') if root.attrib.get('Stat') else ''
                self.stats.append((symbol, phase, stat))

            elif root.tag == 'ApplMsgRpt':
                self.perf.append(root.attrib.get('Txt'))

            elif root.tag == 'News':
                self.news.append(root.text)

        except ET.ParseError as e:
            if xml_str[1] == 'S':
                self.accounts.update(recv.extract_accounts(xml_str))
                logging.info("Updated accounts data")
            else:
                logging.error("Other parse error ocured %s", e)
        except Exception as e:
            logging.error("Non parse error ocured %s", e)

    @staticmethod
    def _call(message: str) -> str:
        """Helper function. Opens sync NOL socket connection, sends message,
        closes socket and returns response message from NOL sync socket.

        Args:
            message (str): Message to be send to NOL.

        Returns:
            str: Response message from NOL program. 
        """
        s = SyncConnection()
        resp = s.back_forth(message)[recv.START:recv.END]
        s.close()
        return resp

    @staticmethod
    def _write_to_file(name: str, txt: str) -> None:
        """Helper function saving text in txt format

        Args:
            name (str): Filename
            txt (str): Text string to save in the file
        """
        f = open(name + '.txt', 'w')
        f.write(txt)
        f.close()

    def _open_async_channel(self) -> None:
        """_summary_
        """
        self.async_channel = AsyncConnection()
        self.async_channel.listings()

    def connect(self):
        """Logs into the NOL program.
        """
        # logowanie
        message = fm.login('login')
        resp = api._call(message)
        logging.info(resp)

        # logowanie port asynchroniczny
        # self.t = threading.Thread(target=self._open_async_channel())
        # self.t.start()

    def check_status(self) -> str:
        """Checks status of the connection to NOL program.

        Returns:
            str: Response message
        """
        message = fm.login('status')
        resp = api._call(message)
        return resp

    def disconect(self) -> None:
        """Logs outs from NOL program.
        """
        if self.sock:
            self.sock.close()
        message = fm.login('logout')
        resp = api._call(message)
        logging.info(resp)

    def get_instruments(self) -> None:
        """Downloads full list of quoted instruments.
        """
        message = fm.get_instruments()
        resp = api._call(message)
        self.instruments = recv._instruments_2dict(resp)
        logging.info(resp)


    # def 
    def save_instruments_csv(self) -> None:
        self.get_instruments()


    def subscribe(self, sec_list: list['str'], data_type: typing.Union[list[EntryType],
        None] = None) -> str:
        """Subscribes to market data. 

        Args:
            sec_list (list): List of symbols for subscription. 
            Max number of symbols is 100.
            data_type (list of EntryTypes, optional): Type of market data to subscribe for.
            If not specified, subscribes to all types of market data. Defaults to None.
        """

        if fm.MarketDataRequest > 0:
            clear = fm.clear_filter()
            api._call(clear)
        if not self.instruments:
            self.get_instruments()
        isin_list = [self.instruments['all'].get(sym) for sym in sec_list]
        message = fm.request_quotes(isin_list, data_type)
        raw_list = {sym: [] for sym in sec_list}
        self.ordb.update(raw_list)
        self.ordb_h.update(raw_list)
        self.tcks.update(raw_list)
        resp = api._call(message)
        logging.info(resp)


    def subscribe_core(self, sec_list):
        """Subscribes to selected group of market data (Bid, Ask, Trade, Oi)

        Args:
            sec_list (list): List of symbols for subscription.
            Max number of symbols is 100.
        """
        self.subscribe(sec_list, [EntryType.Bid, EntryType.Offer, EntryType.Trade,
        EntryType.OpenInterest])
  
    def change_session_status_subs(self) -> str:
        """Turns on and off subscription to session status
        """
        
        if hasattr(self, 'session_status_on'):
            self.session_status_on = not self.session_status_on
            message = fm.session_status_request(on=self.session_status_on)
        else:
            self.session_status_on = True
            message = fm.session_status_request(on=True)
        resp = api._call(message)
        logging.info(resp)


    def send_order(self, symbol: str, side: str, qty: int,
         order: Order, px: float = None, tm: TimeInForce = TimeInForce.Day,
         acc: str = None) -> str:
        """Sends order to NOL platform. 

        Args:
            symbol (str): Financial instrument symbol
            side (str): 1 Buy, 2 Sell
            qty (int): Volume
            order (Orders): Order type 
            px (float): Price limit
            acc (str): Account number

        Returns:
            str: Response message
        """

        isin = self.instruments['all'].get(symbol)
        acc = acc if acc else self.base_account

        message = fm.order(acc, isin, side, qty, order, px, tm)
        resp = api._call(message)
        logging.info(resp)
        resp = recv.get_order_details(resp)
        return resp

    def cancel_order(self, symbol: str, side: str, qty: int, ord_id: str,
            acc: str = None) -> str:
        """Sends order to NOL platform. 

        Args:
            symbol (str): Financial instrument symbol
            side (str): 1 Buy, 2 Sell
            qty (int): Volume
            order_id (str): Order id
            px (float): Price limit
            acc (str): Account number

        Returns:
            str: Response message
        """

        isin = self.instruments['all'].get(symbol)
        acc = acc if acc else self.base_account

        message = fm.cancel_order(acc, isin, side, qty, ord_id)
        resp = api._call(message)
        logging.info(resp)
        return resp

    def load_accounts(self):
        """Initializes accounts"""
        i = 0
        while True:
            data = self.sock.receive()
            if data[1] == 'S':
                self.accounts.update(recv.extract_accounts(data))
                break
            elif i == 500:
                break
            i += 1

    def start(self, sym: list) -> AsyncConnection:
        """Logs to nol, subscribes 

        Args:
            sym (list): List of symbols to subscribe

        Returns:
            AsyncConnection: Asynchronous socket
        """
        self.connect()
        self.get_instruments()
        self.sock = AsyncConnection()
        self.load_accounts()
        self.subscribe(sym)
        return self.sock


    def gui_login(self):
        """Logs to nol, subscribes 

        Args:
            sym (list): List of symbols to subscribe

        Returns:
            AsyncConnection: Asynchronous socket
        """
        self.connect()
        self.get_instruments()
        self.sock = AsyncConnection()
        self.load_accounts()


    def _msg_thread_queue(self, sym: list, queue: deque):
        """Opens queue with incoming market data

        Args:
            sym (list): List of symbols with subscription
            queue (deque): Queue for data
        """
        self.msgq = queue if queue else deque() 
        feed = self.start(sym)
        while True:
            data = feed.receive()
            if data[1] != 'H':
                continue
            self.msgq.appendleft(data)

    def msg_thread2(self, sym: list):
        """Opens queue with incoming market data

        Args:
            sym (list): List of symbols with subscription
            # queue (deque): Queue for data
        """
        feed = self.start(sym)
        try:
            while True:
                data = feed.receive()
                if data[1] == 'H':
                    continue
                logging.info(data)
                ext = recv.extract_mkt_data(data)
                # logging.info(ext)
                if ext:
                    if len(ext) == 2:
                        symbol, lines = ext
                        for line in lines:
                            self.save_to_file(symbol, line)
        except Exception as e:
            logging.error("Exception occured, %s", e)
        
        finally:
            for f in self.files:
                self.files[f].close()

    def msg_thread(self, sym: list):
        """Opens queue with incoming market data

        Args:
            sym (list): List of symbols with subscription
            # queue (deque): Queue for data
        """
        feed = self.start(sym)
        try:
            while True:
                data = feed.receive()
                if data[1] != 'H':
                    logging.info(data)
                    continue
                # ext = recv.extract_mkt_data(data)
                # logging.info(ext)
        
        
        except Exception as e:
            logging.error("Async channel exception occured, type: %s", e)
        
        finally:
            for f in self.files:
                self.files[f].close()
    
    
    def select_account(self, acc_no: str):
        """Selects accounts as a base for a to trade

        Args:
            acc_no (str): Account number
        """

        if acc_no in self.accounts:
            self.base_account = acc_no
            logging.info(f"Successfully selected account {acc_no}")
        else:
            logging.error("Such account does not exist")

    def save_to_file(self, symbol: str, core_data: tuple, path: str='_data/') -> None:
        """Saves feed to file

        Args:
            symbol (str): _description_
            core_data (tuple): _description_
            path (str, optional): _description_. Defaults to '_data/'.
        """
        if symbol not in self.files:  #if ((not plik in pliki) and (len(odczyt.split(',')) == 4)):
            self.files[symbol] = open(path + symbol + '.txt', 'a+')
        f = self.files[symbol]
        f.write(','.join(str(item) for item in core_data) + '\n')
        f.flush()