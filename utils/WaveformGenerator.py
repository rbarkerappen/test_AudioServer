#!/usr/bin/env python

"""
IMPORTANT:
This is a modified version of our existing waveform generation code but
without a dependency on scikits.audiolab (which doesn't seem to be
supported anymore). Before using this, please:

 * test on our other supported audio formats - this has only been tested
   on pcm
 * add a setting field for nominating which channel for multi-channel audio
 * unpacking the frame string into the array seems to assume that the bytes
   per sample is two - not sure if this is a problem
"""

import Image
import ImageDraw
import numpy
import struct
import wave
from array import array
from cStringIO import StringIO
from scikits import audiolab
from HeaderSpec import HeaderSpec


DEFAULT_WAVEFORM_WIDTH = 1400 # pixels
DEFAULT_WAVEFORM_HEIGHT = 150 # pixels
DEFAULT_WAVEFORM_COLOUR = 0   # black
DEFAULT_BACKGROUND_COLOUR = 1 # white



# Based on wav2png.py, available at: http://research.coquipr.com/wiki/Fast_script_to_get_waveform_and_spectrogram_from_a_sound_file


class WaveformGenerator(object):
	
	def __init__(self, width=DEFAULT_WAVEFORM_WIDTH, height=DEFAULT_WAVEFORM_HEIGHT, backgroundColour=DEFAULT_BACKGROUND_COLOUR, waveformColour=DEFAULT_WAVEFORM_COLOUR):
		self.width = width
		self.height = height
		self.backgroundColour = backgroundColour
		self.waveformColour = waveformColour

	def read(self, waveFile, start, size, resizeIfLess=False):
		""" read size samples starting at start, if resize_if_less is True and less than size
		samples are read, resize the array to size and fill with zeros """

		# number of zeros to add to start and end of the buffer
		addToStart = 0
		addToEnd = 0
 
		if start < 0:
			# the first FFT window starts centered around zero
			if size + start <= 0:
				return numpy.zeros(size) if resizeIfLess else numpy.array([])
			else:
				waveFile.setpos(0)
 
				addToStart = -start # remember: start is negative!
				toRead = size + start
 
				if toRead > waveFile.getnframes():
					addToEnd = toRead - waveFile.getnframes()
					toRead = waveFile.getnframes()
		else:
			waveFile.setpos(start)
 
			toRead = size
			if start + toRead >= waveFile.getnframes():
				toRead = waveFile.getnframes() - start
				addToEnd = size - toRead
	
		try:
			samplesInBytes = waveFile.readframes(toRead)
		except IOError:
			# this can happen for wave files with broken headers...
			return numpy.zeros(size) if resizeIfLess else numpy.zeros(2)

		samples = array("h")			#TODO what if not 2 bytes per sample?
		samples.fromstring(samplesInBytes)	

		bytesPerSample = waveFile.getsampwidth()

		samples = [float(sample) / (2 ** (bytesPerSample * 8) / 2) for sample in samples]

		samples = numpy.array(samples)

		# convert to mono by selecting left channel only - TODO allow nomination of channel via settings
		if waveFile.getnchannels() > 1:
			samples = samples[:,0]
 
		if resizeIfLess and (addToStart > 0 or addToEnd > 0):
			if addToStart > 0:
				samples = numpy.concatenate((numpy.zeros(addToStart), samples), axis=1)
 
			if addToEnd > 0:
				samples = numpy.resize(samples, size)
				samples[size - addToEnd:] = 0
 
		return samples


	def getPeaks(self, waveFile, startSeek, endSeek):
		""" read all samples between start_seek and end_seek, then find the minimum and maximum peak
		in that range. Returns that pair in the order they were found. So if min was found first,
		it returns (min, max) else the other way around. """
 
		# larger blocksizes are faster but take more mem...
		# Aha, Watson, a clue, a tradeof!
		blockSize = 4096
 
		maxIndex = -1
		maxValue = -1
		minIndex = -1
		minValue = 1
 
		if endSeek > waveFile.getnframes():
			endSeek = waveFile.getnframes()
 
		if blockSize > endSeek - startSeek:
			blockSize = endSeek - startSeek
 
		if blockSize <= 1:
			samples = self.read(waveFile, startSeek, 1)
			return samples[0], samples[0]

		elif blockSize == 2:
			samples = self.read(waveFile, startSeek, True)
			return samples[0], samples[1]
		
		for i in range(startSeek, endSeek, blockSize):
			samples = self.read(waveFile, i, blockSize)
 
			localMaxIndex = numpy.argmax(samples)
			localMaxValue = samples[localMaxIndex]
 
			if localMaxValue > maxValue:
				maxValue = localMaxValue
				maxIndex = localMaxIndex
 
			localMinIndex = numpy.argmin(samples)
			localMinValue = samples[localMinIndex]
 
			if localMinValue < minValue:
				minValue = localMinValue
				minIndex = localMinIndex
 
		return (minValue, maxValue) if minIndex < maxIndex else (maxValue, minValue)

	def __call__(self, fp):
		"""
		filePath must be a valid wav file.
		"""
		
		waveFile = wave.open(fp)
		samplesPerPixel = 1.0 * waveFile.getnframes() / self.width
		waveform = WaveformImage(self.width, self.height, self.backgroundColour, self.waveformColour)

		for x in range(self.width):
			seekPoint = int(x * samplesPerPixel)
			nextSeekPoint = int((x + 1) * samplesPerPixel)
			peaks = self.getPeaks(waveFile, seekPoint, nextSeekPoint)
			waveform.drawPeaks(x, peaks)

		fp = StringIO()
		waveform.image.save(fp, format="PNG")
		fp.seek(0)

		return fp.read()
		

class WaveformImage(object):
	
	def __init__(self, width, height, backgroundColour, waveformColour):
		self.width = width
		self.height = height
		self.backgroundColour = backgroundColour
		self.waveformColour = waveformColour
		self.image = Image.new("1", (width, height), color=backgroundColour)
		self.draw = ImageDraw.Draw(self.image)
		self.previousX = None
		self.previousY = None

	def drawPeaks(self, x, peaks):
		y1 = self.height * 0.5 - peaks[0] * (self.height - 4) * 0.5
		y2 = self.height * 0.5 - peaks[1] * (self.height - 4) * 0.5
 
		if self.previousY is not None:
			self.draw.line([self.previousX, self.previousY, x, y1, x, y2], self.waveformColour)
		else:
			self.draw.line([x, y1, x, y2], self.waveformColour)
 
		self.previousX = x
		self.previousY = y2

	def save(self, fpOrFilename):
		self.image.save(fpOrFilename)


