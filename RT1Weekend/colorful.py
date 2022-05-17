# simple print style
class ColorCodes:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_error(msg):
    print(f"{ColorCodes.FAIL}{msg}{ColorCodes.ENDC}")

def print_warning(msg):
    print(f"{ColorCodes.WARNING}{msg}{ColorCodes.ENDC}")

def print_bold(msg):
    print(f"{ColorCodes.BOLD}{msg}{ColorCodes.ENDC}")

def print_ok(msg):
    print(f"{ColorCodes.OKBLUE}{msg}{ColorCodes.ENDC}")

def print_header(msg):
    print(f"{ColorCodes.HEADER}{msg}{ColorCodes.ENDC}")

def print_underline(msg):
    print(f"{ColorCodes.UNDERLINE}{msg}{ColorCodes.ENDC}")
