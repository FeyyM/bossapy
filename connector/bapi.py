import ctypes
# from ctypes import *


nocpath = "C:\\zc\\bapi\\nolclientapi.dll"

# ctypes.WinDLL(nocpath)


# give location of dll
# mydll = ctypes.cdll.LoadLibrary(nocpath)

# result1= mydll.add(10,1)
# result2= mydll.sub(10,1)
# print "Addition value:-"+result1
# print "Substraction:-"+result2

mydll = ctypes.windll.LoadLibrary(nocpath)
