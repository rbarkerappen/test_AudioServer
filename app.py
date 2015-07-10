#!/usr/bin/env python

import copy
from cStringIO import StringIO
from flask import Flask, send_file
from lib.LossyAudioEncoder import MP3Encoder, OggEncoder
from lib.wavfile import WavFile
from utils import AudioServerRequest, MP3Settings, OggSettings, WaveformSettings, WaveformGenerator

class Config(object):
	DEBUG = True

app = Flask(__name__)
app.config.from_object(Config)


@app.route("/api/1.0/mp3/<data>")
def mp3(data):
	req = AudioServerRequest.decode(data)
	req.validate(MP3Settings)
	encoder = MP3Encoder()
	mp3 = encoder(req.filePath, req.headerSpec, **req.settings)
	return send_file(StringIO(mp3), mimetype="audio/mpeg3")


@app.route("/api/1.0/ogg/<data>")
def ogg(data):
	req = AudioServerRequest.decode(data)
	req.validate(OggSettings)
	encoder = OggEncoder()
	ogg = encoder(req.filePath, req.headerSpec, **req.settings)
	return send_file(StringIO(ogg), mimetype="audio/ogg")


@app.route("/api/1.0/waveform/<data>")
def waveform(data):
	req = AudioServerRequest.decode(data)
	req.validate(WaveformSettings)
	w = WavFile(req.filePath, req.headerSpec)
	fp = StringIO(w.header + w.data)

	# translate colour setting
	settings = copy.deepcopy(req.settings)
	try:
		colour = settings["colour"]
	except KeyError:
		pass
	else:
		settings.update(WaveformSettings.translateColours(colour))
		del settings["colour"]
	
	waveformGenerator = WaveformGenerator(**settings)
	waveform = waveformGenerator(fp)
	return send_file(StringIO(waveform), mimetype="image/png")


if __name__ == '__main__':
	app.run()
