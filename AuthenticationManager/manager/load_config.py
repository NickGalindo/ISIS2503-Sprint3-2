import yaml
import os


#Hidden fail flag to register fatal errors
__failFlag = False

#Load and read local config
try:
    LOCAL = os.path.dirname(os.path.dirname(__file__))
    CONFIG_FILE = open(os.path.join(LOCAL, 'config.yaml'))
    CONFIG = yaml.load(CONFIG_FILE, Loader=yaml.FullLoader)
except Exception as e:
    print("ERROR -- Failed to open local config file --")
    print(e)
    __failFlag = True


#Exit if fatal error ocurred
if __failFlag:
    raise Exception("A fatal error ocurred on execution, please check ERROR messages")
