import  dis
import marshal
import io
import sys
from FastPrintLog.Logger import LoggerPrint
from pyinstxtractor import ExtractPyInstaller
import os
import subprocess
import shutil
import time
import difflib
Logger  =  LoggerPrint()
SoftPath  = os.getcwd()

# import 开头的python必定会存在
#   1           0 LOAD_CONST               0 (0)
#               2 LOAD_CONST               1 (None)
# # 一般 花之类为  JUMP_FORWARD    填充为 09 00 即可

HexByteHead = {
    "Python 2.7":"03f30d0a00000000",
    "Python 3.0":"3b0c0d0a00000000",
    "Python 3.1":"4f0c0d0a00000000",
    "Python 3.2":"6c0c0d0a00000000",
    "Python 3.3":"9e0c0d0a0000000000000000",
    "Python 3.4":"ee0c0d0a0000000000000000",
    "Python 3.5":"170d0d0a0000000000000000",
    "Python 3.6":"330d0d0a0000000000000000",
    "Python 3.7":"420d0d0a000000000000000000000000",
    "Python 3.8":"550d0d0a000000000000000000000000",
    "Python 3.9":"610d0d0a000000000000000000000000",
    "Python 3.10":"6f0d0d0a000000000000000000000000",
    "Python 3.11":"a70d0d0a000000000000000000000000"
}

#判断字符串的相似度
def similarity(str1, str2):
    return difflib.SequenceMatcher(None, str1,str2).quick_ratio()

#Pyc的反编译
class  PYC_BINARY:
    def __init__(self,FileName,OutDir="./"):
        try:
            self.OutDir = OutDir
            self.FileName = FileName
            self.bytecode = open(FileName,"rb").read() #二进制pyc
            self.magicByte = self.bytecode[:4] #python的魔法头
            Logger.Info("Scann Magic Head:"+self.magicByte.hex())
            self.PythonVersion = "Unknown" #Python的版本
        except:
            Logger.Error("File Not Found:"+FileName)
            return None
    '''
    @description: 匹配pyc的python版本
    @param Binary: 16进制字符串
    '''
    def MarchHexHead(self):
        BinaryCode = self.bytecode.hex()[:8]
        Logger.Info("Your 8 Byte Magic Head is :"+BinaryCode)
        BackEndMagic = None
        for key in HexByteHead:
            if similarity(BinaryCode,HexByteHead[key][:8]) > 0.7:
                BackEndMagic = key
            if BinaryCode == HexByteHead[key][:8]:
                Logger.Success("Find Python Version:"+key)
                self.PythonVersion = key
                if BinaryCode != self.magicByte:
                    Logger.Success("Mybe Real Magic Head should fix -> "+HexByteHead[key])
                    Logger.Warning("如果无法反编译,请尝试修复魔术头->"+HexByteHead[key])
                return True
        Logger.Error("Unknown Python Version or Not a Python Bytecode File (.pyc)")
        if BackEndMagic != None:
            Logger.Success("疑似Python魔术头为,猜测符合度为"+str(similarity(BinaryCode,HexByteHead[BackEndMagic][:8]))+",请修改为:"+HexByteHead[BackEndMagic])
        return False
    '''
    @description: 判断Python版本
    '''
    def CheckPythonVersion(self):
        if self.PythonVersion == "Unknown":
            return False
        else:
            now_py = sys.version.split(" ")[0].split(".")
            pyc_version  = self.PythonVersion.split(" ")[1].split(".")
            if now_py[0] == pyc_version[0] and now_py[1] == pyc_version[1]:
                return True
            else:
                return False
    '''
    @description: 反编译pyc为字节汇编码
    '''
    def AeesmionToHexCode(self,save=True):
        def toByteCode(magic_len):
            #magic_len = int(len(HexByteHead[self.PythonVersion])/2)
            #前八位 魔法头
            code = marshal.loads(self.bytecode[magic_len:])
            # 创建一个StringIO对象来作为输出buffer
            buffer = io.StringIO()
            
            # 将sys.stdout重定向到buffer
            original_stdout = sys.stdout
            sys.stdout = buffer

            dis.dis(code)

                    # 将sys.stdout恢复原样
            sys.stdout = original_stdout
            
            # 获取buffer中的数据
            collected_output = buffer.getvalue()
            Logger.Info(self.FileName+"汇编码:\n"+collected_output)
            if save:
                f = open(self.OutDir+self.FileName+"汇编码.txt","w")
                f.write(collected_output)
                f.close()
                Logger.Success("Assembly Code Save to ->"+self.FileName+"汇编码.txt")
        if self.CheckPythonVersion():
            try:
                toByteCode(int(len(HexByteHead[self.PythonVersion])/2))
            except:
                #暴力破解 魔术头长度
                Logger.Info("Start Burp Magic Head ......")
                isfind = False
                for i in range (0,30):
                    try:
                        toByteCode(i)
                        Logger.Success("Burp Magic Head Success ! Magic Head Len is :"+str(i))
                        isfind = True
                        break
                    except:
                        pass
                if not isfind: return False
            return True
                
        else:
            Logger.Error("当前Python版本与pyc文件版本不匹配,如果需要反编译为字节码,请让当前项目与pyc的版本一致")
            Logger.Info("当前python版本:Python "+sys.version.split(" ")[0].split(".")[0]+"."+sys.version.split(" ")[0].split(".")[1])
            Logger.Info("pyc编译版本:"+self.PythonVersion)
            return False

    '''
    @description: 查找操作码对应的十六进制
    '''
    def SearchByAessionToHexCode(self,OperatorName):
        res = hex(dis.opmap[OperatorName])
        Logger.Success("Search "+OperatorName+" HEX Code : "+res)
        return hex(dis.opmap[OperatorName])
    '''
    @description: 处理字节码 反编译为 py文件
    '''
    def toPy(self):
        try:
            os.system(SoftPath+"//pycdc "+self.FileName+" > "+self.OutDir+self.FileName+".py")
            Logger.Warning("Covering "+self.FileName+" to py file .....")
            Logger.Warning("如果出现错误，请手动根据汇编码修改，去除花指令")
            Logger.Info("例如：花指令  JUMP_FORWARD  填充为 09 00 (NOP指令)即可")
            testCode  = open(self.OutDir+self.FileName+".py","r").read()
            if testCode != "":
                Logger.Success("Cover PyByteCode to py Success !")
            else:
                Logger.Error("无法反编译，请检查汇编码(生成汇编码需与pyc的python版本一致)，是否存在花指令.......")
        except :
            Logger.Error("Cover PyByteCode to py Error ! Please Check Your File ! And Fix Byte Codec !")
        
        
#移动文件夹
def move_folder(source, destination):
    print(source,destination)
    shutil.move(source, destination)


#Pyinstaller 反编译
def UnpackPyistaller(FileName):
    Logger.Info("Unpacking PyInstaller File:"+FileName)
    ExtractPyInstaller(FileName)
    pycFileDir  = FileName+"_extracted"
    Logger.Info("Extract to ->"+"./"+pycFileDir)


    #Python 反编译为py的目录
    OutDIR  = os.getcwd()+"//"+FileName.split(".")[0]+"_py"
    pycFiles = [f for f in os.listdir(os.getcwd()) if f.endswith(".pyc")]


    if not os.path.exists(OutDIR):
        os.mkdir(OutDIR)

    for file in pycFiles:
        RE =  PYC_BINARY("./"+file,OutDIR)
        if RE.MarchHexHead():
            if not RE.AeesmionToHexCode():
                Logger.Warning("发现当前Python版本与pyc版本不一致")
                Logger.Warning("现在尝试直接反编译,如果无法反编译,请更换环境再执行该项目,获取汇编码去除花指令！")
            RE.toPy()

    Logger.Info("Done!")



#最终自动反编译函数
def runner(filename):
    endStr = filename.split(".")[1]
    if endStr == "exe":
        UnpackPyistaller(filename)
    elif endStr == "pyc":
        RE =  PYC_BINARY(filename)
        if RE.MarchHexHead():
            if not RE.AeesmionToHexCode():
                Logger.Warning("发现当前Python版本与pyc版本不一致")
                Logger.Warning("现在尝试直接反编译,如果无法反编译,请更换环境再执行该项目,获取汇编码去除花指令！")
            RE.toPy()
    else:
        Logger.Error("Unsupport File Type:"+endStr)

#额外搜素汇编码 字节功能
def SearchByAessionToHexCode(OperatorName):
    try:
        res = hex(dis.opmap[OperatorName])
        Logger.Success("Search "+OperatorName+" HEX Code : "+res)
        return hex(dis.opmap[OperatorName])
    except:
        Logger.Warning("Sorry , Not Find Operator Hex .....")


if __name__ == "__main__":
    #判断输入的参数
    if len(sys.argv) < 2:
        Logger.Error("Please input file name")
        sys.exit(1)
    else:
        if sys.argv[1] == "-h" or sys.argv[1] == "--help":
            Logger.Info("Usage: pyre.py [file] 反编译文件 exe [pyinstaller] / pyc")
            Logger.Info("       pyre.py -s / --search 获取指令HEX")
            sys.exit(0)
        elif sys.argv[1] == "-s" or sys.argv[1] == "--search":
            if len(sys.argv) < 3:
                Logger.Error("Please input operator name")
                sys.exit(1)
            else:
                SearchByAessionToHexCode(sys.argv[2])
        elif  ("." in sys.argv[1])  and  (sys.argv[1].split(".")[1] == "exe" or sys.argv[1].split(".")[1] == "pyc"):
            runner(sys.argv[1])
        else:
            Logger.Warning("Sorry,Unknow Command !")


            
# UnpackPyistaller("repyf.exe")
# RE =  PYC_BINARY("ezRe.pyc")
# RE.MarchHexHead()
# RE.AeesmionToHexCode()
# RE.SearchByAessionToHexCode("LOAD_CONST")
# RE.SearchByAessionToHexCode("IMPORT_NAME")
# RE.toPy()

# print( hex(dis.opmap["LOAD_CONST"]))
# print( hex(dis.opmap["JUMP_FORWARD"]))
# print( hex(dis.opmap["LOAD_NAME"]))
# print( hex(dis.opmap["IMPORT_NAME"]))