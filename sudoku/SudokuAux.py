#!/usr/bin/env python3

import Solvers

VALID_CELL_CONTENTS = [i for i in range(1,9+1)]

STATUS_OKAY = True
STATUS_INVALID_PUZZLE = False

class SudokuCell(object):
	def __init__(self,val):
		if val:
			self._val = val
			self._filled = True
			self._possibilities = set([val])
		else:
			self._val = None
			self._filled = False
			self._possibilities = set(VALID_CELL_CONTENTS)
		self._neighbors = set() # for neighbors in the graph rather than strictly neighbors in the grid
	
	def addConnection(self,other):
		if other != self and other not in self._neighbors:
			self._neighbors.add(other)
			
	def getValue(self):
		return self._val
	
	def getPossibilitySet(self):
		return self._possibilities
	
	def isFilled(self):
		return self._filled
	
	def limitPossibilities(self):
		""" Circumscribe the set of possibilities based on the values of
			neighboring cells in the graph """
		if self._filled:
			return STATUS_OKAY
		neighboringValues = {n.getValue() for n in self._neighbors}
		# reset possibilities and 
		self._possibilities = set(VALID_CELL_CONTENTS) - neighboringValues
		if len(self._possibilities)==1:
			self._val = list(self.possibilities)[0] # safe since there's only 1 now
			return STATUS_OKAY
		elif len(self._possibilities)==0:
			# can't be anything
			return STATUS_INVALID_PUZZLE
		return STATUS_OKAY
	
	def __str__(self):
		if self._filled:
			return str(self._val)
		return '-' # generic blank space filler
