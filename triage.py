#!/usr/bin/env python

"""
Note: this has not been tested. It is just an illustration of the general concept.
"""

import os
from flask import Flask, redirect, abort
from utils import AudioServerRequest

class Config(object):
	DEBUG = True
	SERVERS = {
		"audio" : "https://audio-storage1.appen.com",
		"audio2" : "https://audio-storage2.appen.com",
		"audio3" : "https://audio-storage3.appen.com",
	}
	DEFAULT_SERVER = "audio"

app = Flask(__name__)
app.config.from_object(Config)


@app.route("/api/<version>/<type>/<data>")
def controller(version, type, data):
	req = AudioServerRequest.decode(data)
	server = req.filePath.split("/")[1]
	if server not in app.config["SERVERS"]:
		server = app.config["DEFAULT_SERVER"]
	baseURL = app.config["SERVERS"][server]
	redirectURL = os.path.join(baseURL, "api", version, type, data)
	return redirect(redirectURL)
