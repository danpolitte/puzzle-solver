#!/usr/bin/env python3

import sys
import Solvers

""" A script for running a puzzle through the sudoku solver """
def main(filename):
	f = open(filename,'r')
	board = []
	for line in f:
		lineArray = [e for e in line[:9]] # ignore newlines or any extra characters in the line
		lineArray = [(int(e) if e.isdigit() else e) for e in lineArray]
		board.append(lineArray)
	
	# feed 2D list into solver
	solver = Solvers.SudokuSolver(board)
	
	# as a test, print the resulting board
	solver.printState()

if __name__ == '__main__':
	programName = sys.argv[0]
	if len(sys.argv) < 2: # no non-program name arg
		print(programName,"requires an argument _filename_")
	filename = sys.argv[1]
	main(filename)