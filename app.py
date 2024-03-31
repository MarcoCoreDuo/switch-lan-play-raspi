from flask import Flask, render_template, request, redirect
import configparser
import subprocess
import os
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

runningServer = "None"
proc = None


def startProgramm(cmd):
	global proc
	stopProgramm()
	command = f"./lan-play --relay-server-addr {cmd}"
	proc = subprocess.Popen(command.split())


def stopProgramm():
	global runningServer
	if proc is not None:
		proc.terminate()
		proc.wait()
	runningServer = "None"


def check_server(server, address):
	split_addr = address.split(":")

	# Using os.system nc to check if the port is open
	up = os.system(f"nc -zv -w 1 {split_addr[0]} {split_addr[1]}") == 0

	# get online count
	data = urllib.request.urlopen(f"http://{address}/info").read()

	return [server, address, up, json.loads(data)["online"]]


def getServers():
	config = configparser.ConfigParser()
	config.read('config.ini')
	with ThreadPoolExecutor() as executor:
		servers = list(executor.map(check_server, config['Servers'].keys(), config['Servers'].values()))
	return servers


@app.route('/', methods=['POST', 'GET'])
def index():
	servers = getServers()
	return render_template('index.html', servers=servers, runningServer=runningServer)


@app.route("/run/", methods=['POST', 'GET'])
def execute():
	global runningServer
	cmd = request.form['serverAddr']
	if runningServer != cmd:
		startProgramm(cmd)
		runningServer = cmd
	return redirect('/')


@app.route("/stop/")
def stop():
	stopProgramm()
	return redirect('/')
