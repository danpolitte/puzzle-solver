#!/usr/bin/env python3

from SudokuAux import SudokuCell
from collections import defaultdict

class SudokuSolver(object):
	def __init__(self,board):
		""" board: an array of 9 arrays of 9 elements each. Expects the numbers
			1 through 9 for filled-in clues, and other elements are interpreted
			as blanks
		"""
		self._numSteps = 0
		cells = [[None for i in range(9)] for j in range(9)] # for the 9x9 array of SudokuCell objs
		cellsFlat = []
		
		row_groups = defaultdict(set)
		col_groups = defaultdict(set)
		block_groups = defaultdict(set)
		
		# build board of SudokuCell objects
		for rNum, row in enumerate(board):
			for cNum, cellVal in enumerate(row):
				newCell = SudokuCell(cellVal if cellVal in SudokuAux.VALID_CELL_CONTENTS else None)
				cells[rNum][cNum] = newCell
				cellsFlat.append(newCell)
				row_groups[rNum].add(newCell)
				col_groups[cNum].add(newCell)
				block_groups[(rNum//3) + 3*(cNum//3)].add(newCell) # TODO: make sure this actually maps to diff blocks right
		
		groups = []
		for i in row_groups:
			groups.append(row_groups[i])
		for i in col_groups:
			groups.append(col_groups[i])
		for i in block_groups:
			groups.append(block_groups[i])
		
		# build relationships between the cells
		for g in groups:
			for c1 in g:
				for c2 in g:
					c1.addConnection(c2)
		
		self._groups = groups
		self._cells = cells
		self._cellsFlat = cellsFlat
		
	def advanceStep(self):
		pass #TODO
	
	def printState(self):
		for row in self._cells:
			rowAsStr = ''.join([str(cell) for cell in row])
			print(rowAsStr)
