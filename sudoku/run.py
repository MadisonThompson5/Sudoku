import subprocess

process = subprocess.Popen("*/Library/Frameworks/Python.framework/Versions/3.6/bin/python3.6* main.py arg1 arg2 arg3 arg4")
process.wait()
