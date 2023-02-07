import time
from flask import Flask
import subprocess as commands

app = Flask(__name__)

def list_ls():
        output = commands.getstatusoutput("ls -l")
        splittt = str(output[1]).splitlines()
        return splittt

@app.route('/')
def hello():
        return list_ls()
