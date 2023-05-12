import xml.etree.ElementTree as ET
import datetime
import logging

from messaging.outgoing import EntryType, SesSub, Stat, RefMsgTyp, BizRejeRsn


class ReceiveTemplates:

    START = 41 # len('<FIXML v="5.0" r="20080317" s="20080314">')
    END = -8 # -len('/></FIXML>')

    @staticmethod
    def market_data_inc(element: str):
        return

    @staticmethod
    def _instruments_2dict(tree: str) -> dict[str, list]:
        ins = dict()
        for element in ET.fromstring(f'<S>{tree}</S>'):
            if element.attrib.get('MktID') == 'NM':
                ins['shares'] = {attr.attrib.get('Sym'): attr.attrib.get('ID') 
                    for attr in element[0]}
            if element.attrib.get('MktID') == 'DN':
                ins['deriv'] = {attr.attrib.get('Sym'): attr.attrib.get('ID') 
                    for attr in element[0]}
            if element.attrib.get('MktID') == 'IN':
                ins['structA'] = {attr.attrib.get('Sym'): attr.attrib.get('ID') 
                    for attr in element[0]}
            if element.attrib.get('MktID') == 'LE':
                ins['structB'] = {attr.attrib.get('Sym'): attr.attrib.get('ID') 
                    for attr in element[0]}
            if element.attrib.get('MktID') == 'IX':
                ins['indices'] = {attr.attrib.get('Sym'): attr.attrib.get('ID') 
                    for attr in element[0]}
        ins['all'] = {sym: isin for group in ins.values() for sym, isin in group.items()}
        return ins
    
   
    @staticmethod
    def _instrument_details(xml_deformed, save=False) -> tuple[list, dict]:
        lookup = {'NM': 'Shares', 'DN': 'Derivatives', 'IN': 'StructA', 'LE': 'StructB',
        'IX': 'Indices'}
        instruments_list = []
        instruments_dict = {}
        for secList in ET.fromstring(f'<S>{xml_deformed}</S>'):
            group = lookup[secList.attrib.get('MktID')]
            for child in secList[0]:
                info = {'Group': group, 'Sym': child.attrib['Sym'], 'ISIN': child.attrib['ID'],
                 'SecGrp': child.attrib['SecGrp'], 'PxPrcsn': child.attrib['PxPrcsn']}
                instruments_list.append(info.copy())
                sym = info.pop('Sym')
                instruments_dict[sym] = info
        
        if save:
            import csv
            myFile = open('./xml/instr.csv', 'w', newline='')
            writer = csv.writer(myFile)
            writer.writerow(['Group', 'Symbol', 'ID', 'SecGrp', 'PxPrcsn'])
            for dictionary in instruments_list:
                writer.writerow(dictionary.values())
            myFile.close()

        return instruments_list, instruments_dict



    @staticmethod
    def extract_core_data2(xml_str):
        # data = {'ordb':[], 'tr':[], 'vol':[], 'oi':[], 'in':[], 'op':[], 'hi':[], 'lo':[], 'ref':[]}
        root = ET.fromstring(xml_str)
        
        if root.tag == 'MktDataInc':
            symbol = root[0][0].attrib.get('Sym')
            updates = []
            now = datetime.datetime.now()
            tdate = now.date().strftime('%Y-%m-%d')
            ttime = now.time().strftime('%H:%M:%S.%f')
            for child in root:
                if child.attrib.get('Typ') in [EntryType.Bid.value, EntryType.Offer.value]:
                    orderNew = (tdate, ttime, child.attrib.get('Typ'), 
                        child.attrib.get('Px'), child.attrib.get('Sz'), 
                        child.attrib.get('NumOfOrds'), child.attrib.get('MDPxLvl'))
                    updates.append(orderNew)
                elif child.attrib.get('Typ') == EntryType.Trade.value:
                    trade = (tdate, ttime, child.attrib.get('Typ'), child.attrib.get('Px'),
                        child.attrib.get('Sz'), child.attrib.get('Tm'))
                    updates.append(trade)
                elif child.attrib.get('Typ') == EntryType.TradeVolume.value:
                    vol = (tdate, ttime, child.attrib.get('Typ'), child.attrib.get('Sz'),
                        child.attrib.get('Tov'))
                    updates.append(vol)
            return updates, symbol


    @staticmethod
    def extract_mkt_data(xml_str: str) -> list:
        try:
            root = ET.fromstring(xml_str)
            if root.tag == 'MktDataInc':
                symbol = root[0][0].attrib.get('Sym')
                # now = datetime.datetime.now()
                # tdate = now.date().strftime('%Y-%m-%d')
                # ttime = now.time().strftime('%H:%M:%S.%f')
                mrk_data = []
                for child in root:
                    if child.attrib.get('Typ') == EntryType.Bid.value or \
                        child.attrib.get('Typ') == EntryType.Offer.value:
                        order_book = (child.attrib.get('Typ'), child.attrib.get('Px'),
                            int(child.attrib.get('Sz')), int(child.attrib.get('NumOfOrds')),
                            child.attrib.get('MDPxLvl'))
                        mrk_data.append(order_book)
                    elif child.attrib.get('Typ') == EntryType.Trade.value:
                        transaction = (child.attrib.get('Typ'), child.attrib.get('Tm'),
                            float(child.attrib.get('Px')), int(child.attrib.get('Sz')))
                        mrk_data.append(transaction)
                    elif child.attrib.get('Typ') == EntryType.TradeVolume.value:
                        vol = (child.attrib.get('Typ'), int(child.attrib.get('Sz')), float(child.attrib.get('Tov')))
                        mrk_data.append(vol)
                    elif child.attrib.get('Typ') == EntryType.OpenInterest.value:
                        oi = (child.attrib.get('Typ'), int(child.attrib.get('Sz'))) #float(child.attrib.get('Tov'))
                        mrk_data.append(oi)
                    elif child.attrib.get('Typ') == EntryType.IndexValue.value:
                        mrk_data.append((child.attrib.get('Typ'), float(child.attrib.get('Px'))))
                    elif child.attrib.get('Typ') == EntryType.OpenPrice.value:
                        mrk_data.append((child.attrib.get('Typ'), float(child.attrib.get('Px'))))
                    elif child.attrib.get('Typ') == EntryType.HighPrice.value:
                        mrk_data.append((child.attrib.get('Typ'), float(child.attrib.get('Px'))))
                    elif child.attrib.get('Typ') == EntryType.LowPrice.value:
                        mrk_data.append((child.attrib.get('Typ'), float(child.attrib.get('Px'))))
                    elif child.attrib.get('Typ') == EntryType.RefPrice.value:
                        mrk_data.append((child.attrib.get('Typ'), float(child.attrib.get('Px'))))
                    else:
                        continue
                return symbol, mrk_data
            
            # elif root.tag == 'ExecRpt':
            # To check what is general
            #     symbol = root[0].attrib.get('Sym')
            #     qty = root
            #     phase = root.attrib.get('SesSub')
            #     phase_name = SesSub(phase)
            #     stat = Stat(root.attrib.get('Stat')) if root.attrib.get('Stat') else ''
            #     return symbol, phase, phase_name, stat
            
            elif root.tag == 'TrdgSesStat':
                symbol = root[0].attrib.get('Sym')
                phase = root.attrib.get('SesSub')
                phase_name = SesSub(phase)
                stat = Stat(root.attrib.get('Stat')) if root.attrib.get('Stat') else ''
                return symbol, phase, phase_name, stat

            elif root.tag == 'ApplMsgRpt':
                delay = root.attrib.get('Txt')
                return delay

            elif root.tag == 'News':
                return root.text

            
            else:
                return

        except ET.ParseError as e:
            if xml_str[1] == 'S':
                logging.info("Updated accounts data")
                return ReceiveTemplates.extract_accounts(xml_str)
            else:
                logging.error("Other parse error ocured %s", e)
        except Exception as e:
            logging.error("Non parse error ocured %s", e)


    @staticmethod
    def extract_accounts(xml_deformed: str) -> dict[str: str]:
        """Extract account balances from data

        Args:
            xml_deformed (_type_): _description_

        Returns:
            _type_: _description_
        """
        root = ET.fromstring(f'<S>{xml_deformed}</S>')
        accs = {}
        for child in root:
            acc_no = child.attrib.get('Acct')
            acc_type = child.attrib.get('type') + child.attrib.get('ike')
            accs[acc_no] = {'acc_type' : acc_type}
            accs[acc_no]['funds'] = {}
            accs[acc_no]['positions'] = {}
            for item in child:
                if item.tag == 'Fund':
                    if pos_name := item.attrib.get('name'):
                        accs[acc_no]['funds'][pos_name] = float(item.attrib.get('value'))
                elif item.tag == 'Position':
                    if pos_name := item[0].attrib.get('Sym'):
                        # accs[acc_no]['positions'][pos_name] = (float(item.attrib.get('Acc110')), 
                        #     float(item.attrib.get('Acc120')))
                        accs[acc_no]['positions'][pos_name] = tuple([float(el)
                         for el in item.attrib.values()])
        return accs

    @staticmethod
    def get_order_details(fxml: str) -> dict:
        """Returns order details from BOSSA system

        Args:
            xml (str): _description_

        Returns:
            dict: Details of the order returned by trading system
        """
        root = ET.fromstring(fxml)
        if root.tag == 'ExecRpt':
            ord = dict(root.items())
            for item in root:
                ord.update(item.items())
            return ord
        if root.tag == 'BizMsgRej':
            reject = dict(root.items())
            return reject

    
    # class (Enum):
    #     Logging = 'BE'
    #     NewOrder = 'D'
    #     CancelOrder = 'F'
    #     ModifyOrder = 'G'
    #     StatusOrder = 'H'
    #     OnlineQuotes = 'V'
    #     Status = 'G'

    @staticmethod
    def _reject_message(root: ET) -> str: 
        kind = RefMsgTyp(root.attrib.get('RefMsgTyp'))
        reason = BizRejeRsn(root.attrib.get('BizRejeRsn'))
        expl = root.attrib.get('Txt')
        return kind, reason, expl


   

