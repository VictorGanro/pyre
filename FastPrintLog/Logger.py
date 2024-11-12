from FastPrintLog.clrprint import *
class LoggerPrint:
    def __init__(self):
        self.clrprint = clrprint
        self.clrinput = clrinput
    def Info(self,text):
        clrprint("[INFO]", end=": ", clr="blue")
        clrprint(text, clr="white")
    def Error(self,text):
        clrprint("[-] ERROR",end=": ",  clr="red")
        clrprint(self,text, clr="yellow")
    def Warning(self,text):
        clrprint("[!] Waring",end=": ",  clr="yellow")
        clrprint(text, clr="brown")
    def Success(self,text):
        clrprint("[+] Success", end=": ", clr="green")
        clrprint(text, clr="pink")
