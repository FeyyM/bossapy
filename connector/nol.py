import socket
import struct
import time
import logging


class Sock:
    """Common base class for sync and async socket connection. Not to be 
    used directly.

    Raises:
        RuntimeError: Raises on broken of socket connection while sending or 
        receiving messages

    """

    # Main parameters for binary communication (from bossaapi manual)
    HEADERSIZE = 4
    HEADERFMT = "<I"
    TIMEOUT = 20
    START = 45
    STOP = -9


    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(Sock.TIMEOUT)
        
    def mysend(self, msg_str):
        msg = struct.pack(Sock.HEADERFMT, len(msg_str)) + msg_str.encode()
        sent = self.sock.send(msg)
        # print('SEND: ', msg)
        if sent == 0:
            raise RuntimeError("socket connection broken")

    def receive(self):
        chunks = []
        bytes_recd = 0
        isHeader = True
        msglen = Sock.HEADERSIZE
         
        while bytes_recd < msglen:
            chunk = self.sock.recv(min(msglen - bytes_recd, 2048))

            if chunk == b'':
                raise RuntimeError("Socket connection broken")
            if isHeader:
                msglen = msglen + struct.unpack(Sock.HEADERFMT, chunk)[0]
                isHeader = False
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        msg_str = b''.join(chunks)
        decoded = msg_str[Sock.HEADERSIZE:-1].decode(encoding='cp1250')
        # decoded = msg_str[Sock.START:Sock.STOP].decode()
        return decoded  #, msg_str

    def close(self):
        self.sock.close()


class SyncConnection(Sock):
    """Synchronous socket connection class
    """
    
    def __init__(self, port=24444):
        """Connects to synchronous socket opened by NOL.

        Args:
            port (int, optional): Port number for synchronous socket. 
            Defaults to 24444.
        """
        self.port = port
        super().__init__()
        self.sock.connect(('localhost', self.port))

    def back_forth(self, msg:str) -> str:
        """Sends and receives message from the socket

        Args:
            msg (str): Message to be send

        Returns:
            str: Received message
        """
        self.mysend(msg)
        received_msg = self.receive()
        return received_msg


class AsyncConnection(Sock):
    """Asynchronous socket connection class. 

    Args:
        Sock (_type_): _description_
    """
    def __init__(self, port=24445):
        """Connects to asynchronous socket opened by NOL.

        Args:
            port (int, optional): Port number for synchronous socket. 
            Defaults to 24445.
        """
        self.port = port
        super().__init__()
        self.sock.connect(('localhost', self.port))
        # self.listings()
    
    def receive(self):
        """Receives data from the soecket

        Raises:
            RuntimeError: _description_

        Returns:
            str: Received message 
        """
        chunks = []
        bytes_recd = 0
        isHeader = True
        msglen = Sock.HEADERSIZE
         
        while bytes_recd < msglen:
            chunk = self.sock.recv(min(msglen - bytes_recd, 1024))

            if chunk == b'':
                raise RuntimeError("Socket connection broken")
            if isHeader:
                msglen = msglen + struct.unpack(Sock.HEADERFMT, chunk)[0]
                isHeader = False
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        msg_str = b''.join(chunks)
        # decoded = msg_str[Sock.HEADERSIZE:-1].decode()
        decoded = msg_str[Sock.START:Sock.STOP].decode(encoding='cp1250')
        return decoded  #, msg_str

    def listings(self):
        while True:
            data = self.receive()
            return data
            
            # if data:
                # return data
            # if KeyboardInterrupt:
                # break