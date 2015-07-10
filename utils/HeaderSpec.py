#! /usr/bin/env python

"""
For manipulating/constructing WAV files from other audio files.
"""

import os, stat, sys, struct, datetime


class BadHeaderSpecError(Exception): pass


class HeaderSpec(dict):
	"""
	Describes an audio file using the following fields:
	 * fmt
	 * rate
	 * width
	 * channels

	Also handles offsets within the audio file using:
	 * start
	 * end
	"""
	
	# keys
	FORMAT = 'fmt'
	RATE = 'rate'
	WIDTH = 'width'
	CHANNELS = 'channels'
	START = 'start'
	END = 'end'

	# formats
	WAV = 'wav'
	PCM = 'pcm'
	ALAW = 'alaw'
	MULAW = 'mulaw'

	VALID_FORMATS = (WAV, PCM, ALAW, MULAW)
	VALID_CHANNELS = (1, 2)
	VALID_WIDTHS = (8, 16, 24)

	def __init__(self, spec=None, **kwArgs):
	
		if spec is not None and kwArgs:
			raise ValueError("Provide either a spec object or args to build one; not both")

		if isinstance(spec, dict):
			
			for key, value in spec.items():
				self[key] = value

		elif isinstance(spec, (str, unicode)):
			
			spec = self.parse(spec)
			for key, value in spec.items():
				self[key] = value

		elif kwArgs:
			for key, value in kwArgs.items():
				self[key] = value

		# assume wav if not provided
		if self.FORMAT not in self:
			self[self.FORMAT] = self.WAV

		self.validate()

	@property
	def fmt(self):
		return self.get(self.FORMAT)

	@property
	def rate(self):
		return self.get(self.RATE)

	@property
	def width(self):
		return self.get(self.WIDTH)

	@property
	def channels(self):
		return self.get(self.CHANNELS)

	@property
	def start(self):
		return self.get(self.START)

	@property
	def end(self):
		return self.get(self.END)
	
	@classmethod
	def parse(klass, s):
	
		d = {}

		pairs = s.split(",")

		for pair in pairs:
			key, value = pair.split("=")
			d[key] = value

		return d

	def validate(self):

		# convert integer fields
		for field in ("width", "channels", "rate", "start", "end"):
			
			# extract value
			try:
				value = self[field]

			# field not provided in this spec
			except KeyError:
				continue


			# convert field
			try:
				self[field] = int(value)
			except (TypeError, ValueError):
				raise BadHeaderSpecError("Invalid %s. Expected integer")


		# format
		self.validateFormat(self.fmt)

		# width
		if self.width is not None:
			self.validateWidth(self.width)

		# channels
		if self.channels is not None:
			self.validateChannels(self.channels)
			
		# rate
		if self.rate is not None:
			self.validateRate(self.rate)

		# start
		if self.start is not None:
			self.validateStart(self.start)

		# end
		if self.end is not None:
			self.validateEnd(self.end)

		# start/end range
		if self.start is not None and self.end is not None:
			if self.start >= self.end:
				raise BadHeaderSpecError("Invalid start/end range - start:%s, end:%s" %(self.start, self.end))

	@classmethod
	def validateFormat(klass, fmt):
		if fmt not in klass.VALID_FORMATS:
			raise BadHeaderSpecError("Invalid format: %s. Expected one of: %s" %(fmt, ", ".join(klass.VALID_FORMATS)))

	@staticmethod
	def validateRate(rate):
		if rate < 1:
			raise BadHeaderSpecError("Invalid rate: %s. Expected integer >= 1" %rate)
	
	@classmethod
	def validateChannels(klass, channels):
		if channels not in klass.VALID_CHANNELS:
			raise BadHeaderSpecError("Invalid channels: %s. Expected one of: %s" %(channels, ", ".join(map(str, klass.VALID_CHANNELS))))

	@classmethod
	def validateWidth(klass, width):
		if width not in klass.VALID_WIDTHS:
			raise BadHeaderSpecError("Invalid width: %s. Expected one of: %s" %(width, ", ".join(map(str, klass.VALID_WIDTHS))))

	@staticmethod
	def validateStart(start):
		if start < 0:
			raise BadHeaderSpecError("Invalid start: %s. Expected >= 0" %start)

	@staticmethod
	def validateEnd(end):
		if end <= 0:
			raise BadHeaderSpecError("Invalid end: %s. Expected > 0" %end)

	def isWav(self):
		return self.fmt == self.WAV

	def pop(self, key):
		try:
			value = self[key]
		except KeyError:
			value = None
		else:
			del self[key]
		return value

	def __str__(self):
		pairs = []

		for key, value in self.items():
			pairs.append("%s=%s" %(key, value))

		return ",".join(pairs)
