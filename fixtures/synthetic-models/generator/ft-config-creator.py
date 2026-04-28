"""
{Egemen M. Aras}
This script creates fault-tree(s) and config files necessary for benchmarking
"""
import os

commandToRun = ""
"""Generates openpsa .xml format fault trees and store them in the openpsa directory"""
def ftGenOpenpsa():
    commandToRun = "python scripts/ft-gen-openpsa.py -o models/xfta"
    os.system(commandToRun)

"""Generates SAPHIRE .JSInp format fault trees and store them in the saphsolve directory"""
def ftGenSaphire():
    commandToRun = "python scripts/ft-gen-saphsolve.py -o models/saphire"
    os.system(commandToRun)

"""Generates config files for Benchexec in .xml format and store them in the benchexec-config directory"""
def configFileGenBenchexec():
    pass


#<======================================================================================>#
"""test-run"""
def runXFTA(XFTAConfigName):
    XFTAExecDir = "C:/Users/emaras/Desktop/Repo/xfta/xfta-1-3-1-win32/xftar"
    commandToRunXFTA = XFTAExecDir + "xftar " + XFTAConfigName
    print(commandToRunXFTA)
    os.system(commandToRunXFTA)

def runSCRAM(inputFile):
    SCRAMExecCommand = "docker run -it --rm -v " + os.getcwd() + "/models/scram:/scram supra scram /scram/" + inputFile + ".xml --mocus --probability --importance > models/scram/" + inputFile + ".txt"
    print(SCRAMExecCommand)
    os.system(SCRAMExecCommand)

def runSAPHSOLVE():
    pass


#<======================================================================================>#
"""compare-results"""
def getResults():
    pass


if __name__ == '__main__':
    if not os.path.exists("models/scram"):
        os.makedirs("models/scram")
    if not os.path.exists("models/xfta"):
        os.makedirs("models/xfta")
    if not os.path.exists(("models/saphsolve")):
        os.makedirs("models/saphsolve")
    ftGenOpenpsa()
    ftGenSaphire()
    #runXFTA()