#!/usr/bin/env python


class AudioServerSettings(dict):
	"""
	Used to define custom settings for audio server requests.
	"""
	
	class Field(object):
		"""
		Defines available settings fields.
		"""

		def __init__(self, type=None, required=False, min=None, max=None, allowed=None):
			self.type = type
			self.required = required
			self.min = min
			self.max = max
			self.allowed = allowed

		def validate(self, attr, value):
			value = self.type(value)

			if self.min is not None and value < self.min:
				raise ValueError("Invalid %r field: %r is lower than the allowed minimum (%r)" %(attr, value, self.min))

			if self.max is not None and value > self.max:
				raise ValueError("Invalid %r field: %r is higher than the allowed maximum (%r)" %(attr, value, self.max))

			if self.allowed is not None and value not in self.allowed:
				raise ValueError("Invalid %r field: %r is not an allowed value. Must be one of: %s" %(attr, value, ", ".join(map(unicode, self.allowed))))


	def __init__(self, **kwArgs):
		for key, value in kwArgs.items():
			self[key] = value

	@classmethod
	def create(cls, **kwArgs):
		d = cls(**kwArgs)
		cls.validate(d)
		return d

	@classmethod
	def validate(cls, d):
		fields = cls.getFields()

		# validate all fields
		for key, value in d.items():
			
			if key not in fields:
				raise KeyError("Unknown settings field: %r" %key)
			
			field = fields[key]
			field.validate(key, value)

		# check required fields are provided
		requiredFields = [key for key, field in fields.items() if field.required]
		for key in requiredFields:
			if key not in d:
				raise KeyError("Missing required field: %r" %key)

	@classmethod
	def getFields(cls):
		"""
		Returns the available settings fields
		as a dictionary of attr -> Field
		"""
		fields = {}

		for attr in dir(cls):
			value = getattr(cls, attr)
			if isinstance(value, cls.Field):
				fields[attr] = value

		return fields


class MP3Settings(AudioServerSettings):
	bitRate = AudioServerSettings.Field(type=int, allowed=[32, 64, 96, 128, 192, 256, 320])


class OggSettings(AudioServerSettings): pass
	#TODO modify OggEncoder to allow specified bitRate
	#bitRate = AudioServerSettings.Field(type=int, allowed=[32, 64, 96, 128, 192, 256, 320])


class WaveformSettings(AudioServerSettings):
	height = AudioServerSettings.Field(type=int, min=1)
	width = AudioServerSettings.Field(type=int, min=1)
	colour = AudioServerSettings.Field(type=str, allowed=["black-on-white", "white-on-black"])

	@classmethod
	def translateColours(cls, colour):
		"""
		Helper function to translate the colour 
		setting field to valid keyword arguments
		for the WaveformGenerator.
		"""

		if colour == "black-on-white":
			return dict(backgroundColour=1, waveformColour=0)

		elif colour == "white-on-black":
			return dict(backgroundColour=0, waveformColour=1)
		
		raise ValueError("Unknown colour: %r" %colour)
