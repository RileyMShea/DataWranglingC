import subprocess
from pprint import pprint

#ls_output = subprocess.run(['ffmpeg'], capture_output=True, shell=True, text=True)
ls_output = subprocess.run(['dir'], capture_output=True, shell=True, text=True)
print(ls_output.stderr)
print(ls_output.stdout)