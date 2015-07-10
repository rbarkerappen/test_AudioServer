#!/usr/bin/env python

"""
Demonstrates usage of the audio server.
"""

import os
import urllib2
from utils import AudioServerRequest, MP3Settings, OggSettings, WaveformSettings, HeaderSpec
from lib.wavfile import WavFile
from cStringIO import StringIO
from argparse import ArgumentParser


AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")
EXAMPLE_WAV_FILE = os.path.join(AUDIO_DIR, "example.wav")
EXAMPLE_PCM_FILE = os.path.join(AUDIO_DIR, "example.pcm")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def demo1(appURL):
	"""
	Convert a file to ogg.
	"""
	
	# build URL
	req = AudioServerRequest(filePath=EXAMPLE_WAV_FILE)
	url = os.path.join(appURL, "api/1.0/ogg", req.encoded)
	print "Making request to: %s" %url
	
	# call web server
	destination = os.path.join(OUTPUT_DIR, "demo1.ogg")
	fp = open(destination, "w")
	response = urllib2.urlopen(url)
	data = response.read()
	fp.write(data)
	fp.close()
	print "Ogg file saved at: %s" %destination


def demo2(appURL):
	"""
	Convert a file to mp3 with a specified bit rate.
	"""

	# define settings (either use create or instantiate)
	settings = MP3Settings.create(bitRate=192)
	
	# build URL
	req = AudioServerRequest(filePath=EXAMPLE_WAV_FILE, settings=settings)
	url = os.path.join(appURL, "api/1.0/mp3", req.encoded)
	print "Making request to: %s" %url

	# call web server
	destination = os.path.join(OUTPUT_DIR, "demo2.mp3")
	fp = open(destination, "w")
	response = urllib2.urlopen(url)
	data = response.read()
	fp.write(data)
	fp.close()
	print "MP3 file saved at: %s" %destination


def demo3(appURL):
	"""
	Generate a waveform with custom dimensions and colour.
	"""

	# define settings (either use create or instantiate)
	settings = WaveformSettings(height=100, width=200, colour="white-on-black")

	# build URL
	req = AudioServerRequest(filePath=EXAMPLE_WAV_FILE, settings=settings)
	url = os.path.join(appURL, "api/1.0/waveform", req.encoded)
	print "Making request to: %s" %url

	# call web server
	destination = os.path.join(OUTPUT_DIR, "demo3.png")
	fp = open(destination, "w")
	response = urllib2.urlopen(url)
	data = response.read()
	fp.write(data)
	fp.close()
	print "Waveform image saved at: %s" %destination


def demo4(appURL):
	"""
	Generate a wavefrom from a raw PCM file using the
	AudioServerRequest object to call the web server.
	"""

	# define header spec
	headerSpec = HeaderSpec("fmt=pcm,width=16,channels=1,rate=48000")
	
	# create request
	req = AudioServerRequest(filePath=EXAMPLE_PCM_FILE, headerSpec=headerSpec)
	
	# create destination
	destination = os.path.join(OUTPUT_DIR, "demo4.png")
	fp = open(destination, "w")

	# use the retrieve function to call the web server
	AudioServerRequest.retrieve(fp, req.buildURL(appURL, "waveform"))
	
	fp.close()
	print "Waveform image saved at: %s" %destination


def demo5(appURL):
	"""
	Convert a file to mp3 and validate the request.
	"""

	# define settings (either use create or instantiate)
	settings = MP3Settings(bitRate=96)
	
	# create request
	req = AudioServerRequest(filePath=EXAMPLE_WAV_FILE, settings=settings)
	req.validate(MP3Settings)

	# create destination
	destination = os.path.join(OUTPUT_DIR, "demo5.mp3")
	fp = open(destination, "w")

	# calling the object uses the retrieve function (same as above)
	req(fp, appURL, "mp3")

	fp.close()
	print "MP3 file saved at: %r" %destination


def main():
	parser = ArgumentParser()
	parser.add_argument("--url", type=str, default="http://localhost:5000", help="The application URL")
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("--demo1", action="store_true", default=False)
	group.add_argument("--demo2", action="store_true", default=False)
	group.add_argument("--demo3", action="store_true", default=False)
	group.add_argument("--demo4", action="store_true", default=False)
	group.add_argument("--demo5", action="store_true", default=False)
	args = parser.parse_args()

	if args.demo1:
		demo1(args.url)
	
	elif args.demo2:
		demo2(args.url)
	
	elif args.demo3:
		demo3(args.url)
	
	elif args.demo4:
		demo4(args.url)
	
	elif args.demo5:
		demo5(args.url)


if __name__ == '__main__':
	main()

