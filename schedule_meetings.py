import argparse
import datetime
import itertools
import random

import ortools.sat.python.cp_model


people = [
	'Dhruva', 'Michael', 'Mónika',
	'Adriano', 'Andy', 'Adriana',
	'Thomas', 'Ethan', 'Prannoy',
	'Saeed', 'Weiming', 'Ildikó'
]
slots = {
	'Mon': ['10:00'],
	'Tue': ['10:00'],
	'Wed': ['10:00'],
	'Thu': ['10:00'],
	'Fri': ['10:00']
}
num_people_per_meeting = 5


class PartialSolutionPrinter(ortools.sat.python.cp_model.CpSolverSolutionCallback):
	def __init__(self, meetings, solutions_to_print, max_solutions, table):
		ortools.sat.python.cp_model.CpSolverSolutionCallback.__init__(self)
		self._meetings = meetings
		if isinstance(solutions_to_print, int):
			self._solutions_to_print = range(solutions_to_print)
		elif isinstance(solutions_to_print, list):
			self._solutions_to_print = solutions_to_print
		else:
			raise Exception
		self._max_solutions = max_solutions
		self._solution_count = 0
		self._table = table

	def on_solution_callback(self):
		if self._solution_count in self._solutions_to_print:
			print('== Solution %i ==' % self._solution_count)
			if self._table == False:
				for day in list(slots.keys()):
					for time in slots[day]:
						print('%s, %s:  ' % (day, time), end='')
						for person in people:
							if self.Value(self._meetings[(day, time, person)]):
								print('%s ' % person, end='')
						print()
					print()
				print()
			else:
				max_num_slots = max([len(x) for x in slots.values()])
				schedule = [[[] for y in range(max_num_slots)] for x in slots.keys()]

				for day_idx, day in enumerate(list(slots.keys())):
					for time_idx, time in enumerate(slots[day]):
						schedule[day_idx][time_idx].extend([person for person in people if self.Value(self._meetings[(day, time, person)])])

				num_days = len(slots.keys())

				for time_idx in range(max_num_slots):
					for person_idx in range(num_people_per_meeting):
						for day_idx in range(num_days):
							sep = '\t'
							if day_idx == num_days - 1:
								sep = ''
							person = ' '
							if len(schedule[day_idx][time_idx]) > 0:
								person = schedule[day_idx][time_idx][person_idx]
							print('%s%s' % (person, sep), end='')
						print()
					print()
		self._solution_count += 1
		if self._max_solutions is not None and self._solution_count >= self._max_solutions:
			self.StopSearch()


	def solution_count(self):
		return self._solution_count


def main(args):
	model = ortools.sat.python.cp_model.CpModel()

	meetings = {}
	for day in list(slots.keys()):
		for time in slots[day]:
			for person in people:
				meetings[(day, time, person)] = model.NewBoolVar('%s__%s__%s' % (day, time, person))

	# Each meeting has exactly 5 people.
	for day in list(slots.keys()):
		for time in slots[day]:
			model.Add(sum(meetings[(day, time, person)] for person in people) == num_people_per_meeting)

	# Each person has at least two meetings per week.
	for person in people:
		model.Add(sum(meetings[(day, time, person)] for day in list(slots.keys()) for time in slots[day]) >= 2)

	# Each person has at most three meetings per week.
	for person in people:
		model.Add(sum(meetings[(day, time, person)] for day in list(slots.keys()) for time in slots[day]) <= 3)

	# All meetings are unique. I.e. every people combination occurs at most once across all slots.
	for combination in itertools.combinations(people, num_people_per_meeting):
		c = []
		for day in list(slots.keys()):
			for time in slots[day]:
				c.append(model.NewBoolVar('(%s)__%s__%s' % (','.join(combination), day, time)))
				model.AddMinEquality(c[-1], [meetings[(day, time, person)] for person in combination])
		model.Add(sum(c) <= 1)

	# Prannoy cannot meet on Wednesdays.
	model.Add(sum(meetings[('Wed', time, 'Prannoy')] for time in slots['Wed']) == 0)

	solver = ortools.sat.python.cp_model.CpSolver()
	solver.parameters.linearization_level = 0

	if args['rand'] is not None:
		sols = random.sample(range(args['rand'][1]), args['rand'][0])
		solution_printer = PartialSolutionPrinter(meetings, sols, max(sols) + 1, args['table'])
	elif args['num'] is not None:
		solution_printer = PartialSolutionPrinter(meetings, list(range(args['num'])), None, args['table'])
	elif args['id'] is not None:
		solution_printer = PartialSolutionPrinter(meetings, args['id'], max(args['id']) + 1, args['table'])
	solver.SearchForAllSolutions(model, solution_printer)

	# Statistics.
	print()
	print('Statistics')
	print('  - conflicts       : %i' % solver.NumConflicts())
	print('  - branches        : %i' % solver.NumBranches())
	print('  - wall time       : %f s' % solver.WallTime())
	print('  - solutions found : %i' % solution_printer.solution_count())


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--rand', action='store', metavar=('N', 'M'), dest='rand', type=int, nargs=2, help='print N random solutions from the first M solutions')
	group.add_argument('--num', action='store', metavar='N', dest='num', type=int, help='print the first N solutions')
	group.add_argument('--id', action='store', metavar='ID', dest='id', type=int, nargs='+', help='print the solutions with the specified IDs')
	parser.add_argument('--table', action='store_true', dest='table', help='instead of the default verbose output, print a tab-separated table that can directly be pasted into a spreadsheet')
	args = parser.parse_args()

	main(vars(args))