#!/usr/bin/env python

import pygtk
pygtk.require('2.0')

import gobject
import pygst
pygst.require('0.10')
import gst

from driver import Driver


class Microphone():
	def __init__(self):
		self.pipeline = gst.parse_launch("pulsesrc ! level message=true interval=100000000 ! fakesink")
		self.pipeline.get_bus().add_signal_watch()
		self.pipeline.get_bus().connect("message::element", self.on_message)
		self.pipeline.set_state(gst.STATE_PLAYING)
		self.peaks = 50*[-100]
	
	def on_message(self, bus, message):
		if message.structure.get_name() == "level":
			#print self.peaks
			self.peaks.pop(0)
			#print message.structure["peak"][0], message.structure["decay"][0], message.structure["rms"][0]
			self.peaks.append( message.structure["peak"][0] )
	
	def high(self):
		lsum = sum(self.peaks[-10:])/len(self.peaks[-10:])
		#print lsum
		return lsum > -15
		
	def continuous_high(self):
		gsum = sum(self.peaks)/len(self.peaks)
		#print gsum
		return gsum > -20

class MicDriver( Driver ):
	def __init__(self):
		self.microphone = Microphone()
		
	def read(self):
		return not self.microphone.high()



# Copyright (c) 2008 Carnegie Mellon University.
#
# You may modify and redistribute this file under the same terms as
# the CMU Sphinx system.  See
# http://cmusphinx.sourceforge.net/html/LICENSE for more information.

# http://cmusphinx.sourceforge.net/sphinx4/license.terms

class VoiceRecognition(object):
	def __init__(self):
		self.stopped = False
		self.end = False
		self.init_gst()
		self.pipeline.set_state(gst.STATE_PLAYING)
	
	
	def stop(self):
		self.pipeline.set_state(gst.STATE_NULL)
	

	def init_gst(self):
		"""Initialize the speech components"""
		self.pipeline = gst.parse_launch('pulsesrc ! audioconvert ! audioresample '
											+ '! vader name=vad auto-threshold=true '
											+ '! pocketsphinx name=asr ! fakesink')
		asr = self.pipeline.get_by_name('asr')
		asr.connect('partial_result', self.asr_partial_result)
		asr.connect('result', self.asr_result)
		asr.set_property('configured', True)
		bus = self.pipeline.get_bus()
		bus.add_signal_watch()
		bus.connect('message::application', self.application_message)


	def asr_partial_result(self, asr, text, uttid):
		"""Forward partial result signals on the bus to the main thread."""
		struct = gst.Structure('partial_result')
		struct.set_value('hyp', text)
		struct.set_value('uttid', uttid)
		asr.post_message(gst.message_new_application(asr, struct))


	def asr_result(self, asr, text, uttid):
		"""Forward result signals on the bus to the main thread."""
		struct = gst.Structure('result')
		struct.set_value('hyp', text)
		struct.set_value('uttid', uttid)
		asr.post_message(gst.message_new_application(asr, struct))


	def application_message(self, bus, msg):
		"""Receive application messages from the bus."""
		msgtype = msg.structure.get_name()
		if msgtype == 'partial_result':
			self.partial_result(msg.structure['hyp'], msg.structure['uttid'])
		elif msgtype == 'result':
			self.final_result(msg.structure['hyp'], msg.structure['uttid'])


	def partial_result(self, hyp, uttid):
		print "Partial Result:", hyp


	def final_result(self, hyp, uttid):
		print "Final Result:", hyp
		if "shut up" in hyp:
			self.stopped = True
		if "end conversation" in hyp:
			self.end = True

