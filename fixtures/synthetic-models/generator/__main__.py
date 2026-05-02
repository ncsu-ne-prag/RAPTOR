import os
import shutil
import re

"""
--This script is able to create fault trees by allowing user to set number of basic events.
--The created fault trees are stored in as .xml in open PRA format.
--The quantification of fault trees are done using XFTA version 1.0 and SCRAM.
"""
###############################################################################################
#Creating a config .xml file tp run XFTA from a template
def prepare_xfta(name):

    with open('xfta.template', 'r') as file:
        filedata = file.read()
    filedata = re.sub("NAME", name, filedata)
    with open("xfta_" + name + ".xml", 'w') as file:
        file.write(filedata)
###############################################################################################

###############################################################################################
#Running XFTA with the command line
def run_xfta(xfta_config_name):
    xfta_exec_dir = "C:/Users/emaras/Desktop/xfta/xfta-1-3-1-win32/"
    command_to_run_xfta = xfta_exec_dir + "xftar " + xfta_config_name
    print(command_to_run_xfta)
    os.system(command_to_run_xfta)
###############################################################################################

###############################################################################################
#Running SCRAM with the command line
def run_scram(scram_input):
    scram_exec_command = "docker run -it --rm -v " + os.getcwd() + "/models/scram:/scram supra scram /scram/" + scram_input + ".xml --mocus --probability --importance > models/scram/" + scram_input + ".txt"
    print(scram_exec_command)
    os.system(scram_exec_command)
    #print(scram_input + '.xml kostu')
###############################################################################################

###############################################################################################
#Creating fault tree
def generate_multiple_ft():

    num_basic = 100
    while (num_basic <= 100):
        command_to_generate = "python scripts/fault_tree_generator.py -b " + str(num_basic) + " -o models/scram/ft_" + str(num_basic) + ".xml"
        # generate inputs in scram directory
        os.system(command_to_generate)
        run_scram("ft_" + str(num_basic))
        # copy ft inputs to xfta directory
        shutil.copy("models/scram/ft_" + str(num_basic) + ".xml", "models/xfta/ft_" + str(num_basic) + ".xml")
        # generate xfta config file and move
        prepare_xfta("ft_"+str(num_basic))
        os.replace("xfta_ft_"+str(num_basic)+".xml", "models/xfta/xfta_ft_"+str(num_basic)+".xml")
        # rest
        run_xfta(os.getcwd() + "/models/xfta/xfta_ft_" + str(num_basic) + ".xml")
        num_basic += 1
###############################################################################################

###############################################################################################
if __name__ == '__main__':
    if not os.path.exists("models/scram"):
        os.makedirs("models/scram")
    if not os.path.exists("models/xfta"):
        os.makedirs("models/xfta")
    generate_multiple_ft()
    # prepare_xfta()
###############################################################################################