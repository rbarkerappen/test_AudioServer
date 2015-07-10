#!/usr/bin/env python

import copy
import os
import simplejson
import urllib2
from itsdangerous import URLSafeSerializer
from HeaderSpec import HeaderSpec


class AudioServerRequest(object):
	"""
	Builds a client request for the audio server.
	"""

	SECRET_KEY = os.environ.get("AUDIO_SERVER_SECRET_KEY")

	def __init__(self, filePath=None, headerSpec=None, settings=dict()):
		self.filePath = filePath
		self.headerSpec = HeaderSpec(headerSpec)
		self.settings = copy.deepcopy(settings)

	def __call__(self, fp, *urlArgs, **urlKwArgs):
		url = self.buildURL(*urlArgs, **urlKwArgs)
		return self.retrieve(fp, url)

	def buildURL(self, appURL, type, version="1.0"):
		"""
		Helper function to build the request URL.
		"""
		return os.path.join(appURL, "api", version, type, self.encoded)

	@staticmethod
	def retrieve(fp, url):
		"""
		Calls the audio server using the provided
		request URL and saves the response to the
		file-like object.
		"""
		response = urllib2.urlopen(url)
		contents = response.read()
		fp.write(contents)

	def validate(self, settingValidator=None, checkFileExists=True):
		"""
		Validates the request.
		"""

		if self.filePath is None:
			raise ValueError("Missing filePath")

		if checkFileExists and not os.path.isfile(self.filePath):
			raise ValueError("Audio file does not exist: %s" %self.filePath)

		if self.headerSpec is not None:
			HeaderSpec(self.headerSpec)

		if self.settings:
			if settingValidator is None:
				raise ValueError("No setting validator provided.")

			settingValidator.validate(self.settings)
	
	@property
	def jsonDict(self):
		"""
		Converts the request to a json encodable
		dictionary.
		"""
		d = {"filePath" : self.filePath}

		if self.headerSpec:
			d["headerSpec"] = HeaderSpec(self.headerSpec)

		if self.settings:
			d["settings"] = self.settings

		return d

	@property
	def json(self):
		return simplejson.dumps(self.jsonDict)

	@property
	def encoded(self):
		"""
		Encodes the request.
		"""
		return URLSafeSerializer(self.SECRET_KEY).dumps(self.json)

	@classmethod
	def decode(cls, data):
		"""
		Decodes a request and returns the instantiated
		object.
		"""
		json = URLSafeSerializer(cls.SECRET_KEY).loads(data)
		jsonDict = simplejson.loads(json)
		req = cls(**jsonDict)
		return req
