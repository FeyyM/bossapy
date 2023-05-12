from enum import Enum
import datetime
import typing



class Order(Enum):
    PKC = '1'
    Limit = 'L'
    StopLoss = '3'
    StopLimit = '4'
    PCR = 'K'
    PEG = 'E'
    PEGLimit = 'G'
    
class TimeInForce(Enum):
    Day = '0'
    GoodTillCancelled = '1' 
    BeforeOpen = '2'
    FillorKill = '3'
    FillandKill = '4'
    TillDay = '6'
    Close = '7'
    Fixing = 'f'
    TillTime = 't'

class EntryType(Enum):
    Bid = '0'
    Offer = '1'
    Trade = '2'
    TradeVolume = 'B'
    OpenInterest = 'C'
    IndexValue = '3'
    OpenPrice = '4'
    ClosePrice = '5'
    HighPrice = '7'
    LowPrice = '8'
    RefPrice = 'r'

class OrderStatus(Enum):
    New = '0'
    Archival = 'C'
    Updating = 'E'
    Active = '1'
    Filled = '2'
    Anulled = '4'
    Anulling = '6'
    Rejected = '8'


class UserStatus(Enum):
    NOLclosed = '1'
    NOLoffline = '2'
    NOLonline = '3'
    NOLnotStarted = '4'
    NoInternetConnection = '5'
    ConnectingNOL = '6'
    ConnectingInternet = '7'


class UserResponse(Enum):
    LoggedIn = '1'
    LoggedOut = '2'
    NoUser = '3'
    BadPassword = '4'
    Offline = '5'
    Other = '6'
    NOLOffline = '7'


class RefMsgTyp(Enum):
    Logging = 'BE'
    NewOrder = 'D'
    CancelOrder = 'F'
    ModifyOrder = 'G'
    StatusOrder = 'H'
    ONlineQuots = 'V'
    Status = 'G'


class BizRejeRsn(Enum):
    Other = '0'
    BadID = '1'
    BadInstrument = '2'
    BadMessage = '3'
    NOLaccessProblem = '4'
    BadXML = '5'
    NoAuthorization = '6'
    NoCommunication = '7'


class SesSub(Enum):
    OversightConsultation = 'C'
    BeforeOpen = 'D'
    Intervention = 'E'
    Opening = 'o'
    ContinousTrading = 'S'
    OversightReview = 'N'
    OversightReviewFinished = 'F'
    AfterTrading = 'B'


class Stat(Enum):
    Balancing = 'AR'
    OnlyOrdersNoTrading = 'AS'
    InTrading = 'A'
    NoOvertimeNoorder = 'IR'
    NoTrading = 'IS'
    NoTradingAllowed = 'I'
    Freezed = 'AG'

class ExecTyp(Enum):
    New = '0'
    Transaction = 'F'
    Anullment = '4'
    Modification = 'E'
    InAnnulment = '6'
    Rejected = '8'
    Status = 'I'


class FIXML_mes:
    """Set of templates for messages to NOL system

    """

    # Outer tag for FIXML message
    FIX_TAG = '<FIXML v="5.0" r="20080317" s="20080314">{}</FIXML>'
    DATE_TODAY = datetime.date.today().strftime('%Y%m%d')
    # Counters
    UserReqID = 0 #User login, status, logout messages counter
    ReqId = 1 #Market lists messags counter
    NewOrderSingle = 0 #Orders market counter
    OrderCancelReplaceRequest = 0 #
    OrderCancelRequest = 0 #
    OrderStatusRequest = 0 #
    TradingSessionStatusRequest = 0
    MarketDataRequest = 0

    @staticmethod
    def login(action: str) -> str:
        """Message for user login, logout and status check method

        Args:
            action (str): Type of action: 'login', 'logout', 'status'

        Returns:
            Message (str) to NOL system
        """

        user_req_template = ' UserReqTyp="{}" Username="BOS" Password="BOS"/>'
        
        req_no = f'<UserReq UserReqID="{FIXML_mes.UserReqID}"'
        FIXML_mes.UserReqID += 1

        if action == 'login':
            msg = user_req_template.format('1')
        elif action == 'status':
            msg = user_req_template.format('4')
        elif action == 'logout':
            msg = user_req_template.format('2')
        else:
            raise ValueError("Acceptable actions: login', 'logout, 'status'")
        
        return FIXML_mes.FIX_TAG.format(req_no + msg)

    @staticmethod
    def get_instruments(kind:str= 'full', sym=None) -> str:
        """Message to obtain securities list from NOL

        Args:
            kind (str): Category of list: 'single', 'full', 'equities', 'derivs'.
            Defaults to 'full'.
            sym (str, optional): Single symbol e.g. 'PZU'. Defaults to None.

        Returns:
            Message (str): XML string readable by NOL system
        """

        id = f'<SecListReq ReqID="{FIXML_mes.ReqId}" '
        FIXML_mes.ReqId += 1

        if kind == 'full':
            msg = id + 'ListReqTyp="4"></SecListReq>'
        elif kind == 'equities':
            msg = id + 'ListReqTyp="5" MktID="NM"></SecListReq>'
        elif kind == 'derivs':
            msg = id + 'ListReqTyp="5" MktID="DN"></SecListReq>'
        elif kind == 'single':
            msg =  id + f'ListReqTyp="0"><Instrmt Sym="{sym}"></SecListReq>'
        else:
            raise ValueError("Acceptable types of security lists: 'full', \
            'equties', 'derivs', 'single' + sym='symname'")
        
        return FIXML_mes.FIX_TAG.format(msg)
        

    @staticmethod
    def clear_filter() -> str:
        """Message to clear filter of securities.

        Returns:
            Message (str): XML string readable by NOL system
        """
        msg = f'<MktDataReq ReqID="{FIXML_mes.ReqId}" SubReqTyp="2"></MktDataReq>'
        FIXML_mes.ReqId += 1

        return FIXML_mes.FIX_TAG.format(msg)

    @staticmethod
    def request_quotes(names: list, data_type: typing.Union[list[EntryType],
        None] = None):
        """Message requesting data on securities.

        Returns:
            Message (str): XML string readable by NOL system
        """
        
        id = f'<MktDataReq ReqID="{FIXML_mes.ReqId}"'
        FIXML_mes.ReqId += 1
        market_data = id + ' SubReqTyp="1" MktDepth="0">'

        data_type = data_type if data_type else EntryType
        for item in data_type:
            market_data += f'<req Typ="{item.value}"/>'

        market_data += '{}</MktDataReq>'
        txt = '<InstReq>'

        names = names if isinstance(names, list) else [names]
        for name in names:
            txt += f'<Instrmt ID="{name}" Src="4"/>'

        txt += '</InstReq>'
        msg = market_data.format(txt)
        return FIXML_mes.FIX_TAG.format(msg)

    @staticmethod
    def session_status_request(on=True):
        """Session status request on/off message

        Args:
            on (bool, optional): Turn on/off switch. Defaults to True.

        Returns:
            Message (str): XML string readable by NOL system
        """

        id = f'<TrdgSesStatReq ReqID="{FIXML_mes.ReqId}"'
        FIXML_mes.ReqId += 1
        if on:
            msg = id + ' SubReqTyp="1">'
        else:
            msg = id + ' SubReqTyp="2">'
        return FIXML_mes.FIX_TAG.format(msg)



    @staticmethod
    def order(acc: str, isin: str, side: str, qty: int, ordt: Order,
        px: float= None, tm: TimeInForce= TimeInForce.Day, **kwargs):
        """Order message.

        Returns:
                (str): XML string readable by NOL system
        """
        TxnTm = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')
        order = f'<Order ID="{FIXML_mes.NewOrderSingle}" TrdDt="{FIXML_mes.DATE_TODAY}" Acct="{acc}" Side="{side}" TxnTm="{TxnTm}" '
        FIXML_mes.NewOrderSingle += 1

        if ordt == Order.Limit:
            order += f'OrdTyp="{ordt.value}" Px="{px:.6f}" Ccy="PLN" TmInForce="{tm.value}">'
        elif ordt == Order.PEGLimit:
            order += f'OrdTyp="{ordt.value}" StopPx="{px:.6f}" Ccy="PLN" TmInForce="{tm.value}">'
        else:
            order += f'OrdTyp="{ordt.value}" Ccy="PLN" TmInForce="{tm.value}">'

        order += f'<Instrmt ID="{isin}" Src="4"/><OrdQty Qty="{qty}"/></Order>'
        # f string is c. 10% faster than .format()
        return f'<FIXML v="5.0" r="20080317" s="20080314">{order}</FIXML>'
    
    @staticmethod
    def cancel_order(acc:str, isin:str, side:str, qty:str, ord_id: str) -> str:
        """_summary_

        Args:
            ord_id (str): Order id
            side (str): direction of the trade
            acct (str): account of the trade
            isin (str): isin
            qty (str): number of instruments

        Returns:
            (str): XML string readable by NOL system
        """

        TxnTm = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')
        msg = f'<OrdCxlReq ID="{FIXML_mes.OrderCancelReplaceRequest}" OrdID="{ord_id}" Acct="{acc}" Side="{side}" TxnTm="{TxnTm}"><Instrmt ID="{isin}" Src="4"/><OrdQty Qty="{qty}"/></OrdCxlReq>'
        # f string is c. 10% faster than .format()
        FIXML_mes.OrderCancelReplaceRequest += 1
        return f'<FIXML v="5.0" r="20080317" s="20080314">{msg}</FIXML>'

    @staticmethod
    def get_order_stat(acc:str, isin:str, side:str, ord_id: str) -> str:
        """_summary_

        Args:
            ord_id (str): Order id
            side (str): direction of the trade
            acct (str): account of the trade
            isin (str): isin
            qty (str): number of instruments

        Returns:
            (str): XML string readable by NOL system
        """

        TxnTm = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')
        msg = f'<OrdStatReq StatReqID="{FIXML_mes.OrderStatusRequest}" OrdID="{ord_id}" Acct="{acc}" Side="{side}"><Instrmt ID="{isin}" Src="4"/></OrdStatReq>'
        # f string is c. 10% faster than .format()
        FIXML_mes.OrderStatusRequest += 1
        return f'<FIXML v="5.0" r="20080317" s="20080314">{msg}</FIXML>'

    @staticmethod
    def modify_order(acc:str, isin:str, side:str, ord_id: str, ord_id2: str,
     qty:str, ordt: Order, px: float= None, tm: TimeInForce= TimeInForce.Day,
     **kwargs) -> str:
        """_summary_

        Args:
            ord_id (str): Order id
            ord_id2 (str): Order id from brokerage
            ord (Order): Order type
            side (str): direction of the trade
            acct (str): account of the trade
            isin (str): isin
            qty (str): number of instruments
            px (float): price
            tm (TimeInForce): 

        Returns:
            (str): XML string readable by NOL system
        """

        TxnTm = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')

        m_ord = f'<OrdCxlRplcReq ID="{FIXML_mes.OrderCancelReplaceRequest}" OrdID="{ord_id}" OrdID2="{ord_id2}" TrdDt="{FIXML_mes.DATE_TODAY}" Acct="{acc}" Side="{side}" TxnTm="{TxnTm}" '
        FIXML_mes.OrderCancelReplaceRequest += 1

        if ordt == Order.Limit:
            m_ord += f'OrdTyp="{ordt.value}" Px="{px:.6f}" Ccy="PLN" TmInForce="{tm.value}">'
        elif ordt == Order.PEGLimit:
            m_ord += f'OrdTyp="{ordt.value}" StopPx="{px:.6f}" Ccy="PLN" TmInForce="{tm.value}">'
        else:
            m_ord += f'OrdTyp="{ordt.value}" Ccy="PLN" TmInForce="{tm.value}">'

        m_ord += f'<Instrmt ID="{isin}" Src="4"/><OrdQty Qty="{qty}"/></OrdCxlRplcReq>'
        # f string is c. 10% faster than .format()
        return f'<FIXML v="5.0" r="20080317" s="20080314">{m_ord}</FIXML>'
    
    @staticmethod
    def sess_status(action='subscribe') -> str:
        """Session status message.

        Returns:
            Message (str): XML string readable by NOL system
        """

        action = '1' if action == 'subscribe' else '2'
        msg = f'<trdgSesStatReq ReqID={FIXML_mes.TradingSessionStatusRequest} SubReqTyp={action}'
        return FIXML_mes.FIX_TAG.format(msg)


def get_price_step(id: str, px: float) -> float:
    """Acquires minimum step for the company

    Args:
        id (str): _description_
        px (float): _description_

    Returns:
        float: _description_
    """
    
    #futures on shares and FX
    if id == '1': 
        step = 0.001
    # index options
    elif id == '2':
        if 0.01 <= px < 50:
            step = 0.01
        else:
            step = 0.05
    # futures on indices
    elif id == '3':
        step = 1
    # bonds, inv certificates, futures on Treasuries, Wibor
    elif id == '4':
        step = 0.01
    # structured instruments ex bonds
    elif id == '7':
        if 0.01 <= px < 10:
            step = 0.01
        elif 10 <= px < 20:
            step = 0.02
        elif 20 <= px < 50:
            step = 0.05
        elif 50 <= px < 100:
            step = 0.1
        elif 100 <= px < 200:
            step = 0.12
        else:
            step = 0.5
    # shares, ETFs (8, 9, 10, 11, 12, 13)
    elif id == '8':
        if 0.01 <= px < 0.1:
            step = 0.0005
        elif 0.1 <= px < 0.2:
            step = 0.001
        elif 0.2 <= px < 0.5:
            step = 0.002
        elif 0.5 <= px < 1:
            step = 0.005
        elif 1 <= px < 2:
            step = 0.01
        elif 2 <= px < 5:
            step = 0.02
        elif 5 <= px < 10:
            step = 0.05
        elif 10 <= px < 20:
            step = 0.1
        elif 20 <= px < 50:
            step = 0.2
        elif 50 <= px < 100:
            step = 0.5
        elif 100 <= px < 200:
            step = 1.0
        elif 200 <= px < 500:
            step = 2.0
        elif 500 <= px < 1000:
            step = 5.0
        elif 1000 <= px < 2000:
            step = 10.0
        elif 2000 <= px < 5000:
            step = 20.0
        elif 5000 <= px < 10000:
            step = 50.0
        elif 10000 <= px < 20000:
            step = 100.0
        elif 20000 <= px < 50000:
            step = 200.0
        elif 50000 <= px:
            step = 500.0
    elif id == '9':
        if 0.01 <= px < 0.1:
            step = 0.0002
        elif 0.1 <= px < 0.2:
            step = 0.0005
        elif 0.2 <= px < 0.5:
            step = 0.001
        elif 0.5 <= px < 1:
            step = 0.002
        elif 1 <= px < 2:
            step = 0.005
        elif 2 <= px < 5:
            step = 0.01
        elif 5 <= px < 10:
            step = 0.02
        elif 10 <= px < 20:
            step = 0.05
        elif 20 <= px < 50:
            step = 0.1
        elif 50 <= px < 100:
            step = 0.2
        elif 100 <= px < 200:
            step = 0.5
        elif 200 <= px < 500:
            step = 1.0
        elif 500 <= px < 1000:
            step = 2.0
        elif 1000 <= px < 2000:
            step = 5.0
        elif 2000 <= px < 5000:
            step = 10.0
        elif 5000 <= px < 10000:
            step = 20.0
        elif 10000 <= px < 20000:
            step = 50.0
        elif 20000 <= px < 50000:
            step = 100.0
        elif 50000 <= px:
            step = 200.0
    elif id == '10':
        if 0.01 <= px < 0.1:
            step = 0.0001
        elif 0.1 <= px < 0.2:
            step = 0.0002
        elif 0.2 <= px < 0.5:
            step = 0.0005
        elif 0.5 <= px < 1:
            step = 0.001
        elif 1 <= px < 2:
            step = 0.002
        elif 2 <= px < 5:
            step = 0.005
        elif 5 <= px < 10:
            step = 0.01
        elif 10 <= px < 20:
            step = 0.02
        elif 20 <= px < 50:
            step = 0.05
        elif 50 <= px < 100:
            step = 0.1
        elif 100 <= px < 200:
            step = 0.2
        elif 200 <= px < 500:
            step = 0.5
        elif 500 <= px < 1000:
            step = 1.0
        elif 1000 <= px < 2000:
            step = 2.0
        elif 2000 <= px < 5000:
            step = 5.0
        elif 5000 <= px < 10000:
            step = 10.0
        elif 10000 <= px < 20000:
            step = 20.0
        elif 20000 <= px < 50000:
            step = 50.0
        elif 50000 <= px:
            step = 100.0
    elif id == '11':
        if 0.01 <= px < 0.2:
            step = 0.0001
        elif 0.2 <= px < 0.5:
            step = 0.0002
        elif 0.5 <= px < 1:
            step = 0.0005
        elif 1 <= px < 2:
            step = 0.001
        elif 2 <= px < 5:
            step = 0.002
        elif 5 <= px < 10:
            step = 0.005
        elif 10 <= px < 20:
            step = 0.01
        elif 20 <= px < 50:
            step = 0.02
        elif 50 <= px < 100:
            step = 0.05
        elif 100 <= px < 200:
            step = 0.1
        elif 200 <= px < 500:
            step = 0.2
        elif 500 <= px < 1000:
            step = 0.5
        elif 1000 <= px < 2000:
            step = 1.0
        elif 2000 <= px < 5000:
            step = 2.0
        elif 5000 <= px < 10000:
            step = 5.0
        elif 10000 <= px < 20000:
            step = 10.0
        elif 20000 <= px < 50000:
            step = 20.0
        elif 50000 <= px:
            step = 50.0
    elif id == '12':
        if 0.01 <= px < 0.5:
            step = 0.0001
        elif 0.5 <= px < 1:
            step = 0.0002
        elif 1 <= px < 2:
            step = 0.0005
        elif 2 <= px < 5:
            step = 0.001
        elif 5 <= px < 10:
            step = 0.002
        elif 10 <= px < 20:
            step = 0.005
        elif 20 <= px < 50:
            step = 0.01
        elif 50 <= px < 100:
            step = 0.02
        elif 100 <= px < 200:
            step = 0.05
        elif 200 <= px < 500:
            step = 0.1
        elif 500 <= px < 1000:
            step = 0.2
        elif 1000 <= px < 2000:
            step = 0.5
        elif 2000 <= px < 5000:
            step = 1.0
        elif 5000 <= px < 10000:
            step = 2.0
        elif 10000 <= px < 20000:
            step = 5.0
        elif 20000 <= px < 50000:
            step = 10.0
        elif 50000 <= px:
            step = 20.0
    elif id == '13':
        if 0.01 <= px < 1:
            step = 0.0001
        elif 1 <= px < 2:
            step = 0.0002
        elif 2 <= px < 5:
            step = 0.0005
        elif 5 <= px < 10:
            step = 0.001
        elif 10 <= px < 20:
            step = 0.002
        elif 20 <= px < 50:
            step = 0.005
        elif 50 <= px < 100:
            step = 0.01
        elif 100 <= px < 200:
            step = 0.02
        elif 200 <= px < 500:
            step = 0.05
        elif 500 <= px < 1000:
            step = 0.1
        elif 1000 <= px < 2000:
            step = 0.2
        elif 2000 <= px < 5000:
            step = 0.5
        elif 5000 <= px < 10000:
            step = 1.0
        elif 10000 <= px < 20000:
            step = 2.0
        elif 20000 <= px < 50000:
            step = 5.0
        elif 50000 <= px:
            step = 10.0
    return step
    
# Anulowanie zlecenia
# Przykład:
# <FIXML v="5.0" r="20080317" s="20080314">
# 
# </FIXML>


# Modyfikacja zlecenia
# Przykład:
# <FIXML v="5.0" r="20080317" s="20080314">
# <OrdCxlRplcReq ID="0" OrdID="530471817" OrdID2="103282541" TrdDt="20170802"
# Acct="00-55-006039" Side="1" TxnTm="20170802-10:29:47" OrdTyp="L" Px="6.590000"
# Ccy="PLN" TmInForce="0">
# <Instrmt ID="PLPGNIG00014" Src="4"/>
# <OrdQty Qty="1"/>
# </OrdCxlRplcReq>
# </FIXML>


# Zapytanie o status zlecenia
# Przykład:
# <FIXML v="5.0" r="20080317" s="20080314">
# <OrdStatReq StatReqID="5" OrdID="530478088" Acct="00-55-006039" Side="1">
# <Instrmt Sym="PGNIG" Src="4" ID="PLPGNIG00014"/>
# </OrdStatReq>
# </FIXML>

# class UserStat(enum):
    
#     LOGGED = 1
#     LOGOFF = 2
#     NOUSER = 3
#     PASS = 4
#     OFFLINE = 5
#     OTHER = 6
#     NOL = 7

        




