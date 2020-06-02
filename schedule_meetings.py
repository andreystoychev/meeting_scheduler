import itertools
import datetime
import ortools.sat.python.cp_model


people = [
	'Dhruva', 'Michael', 'Monika',
	'Adriano', 'Andy', 'Adriana',
	'Thomas', 'Ethan', 'Prannoy',
	'Saeed', 'Weiming'
]
slots = {
	'Mon': ['10:00', '14:00'],
	'Tue': ['10:00', '14:00'],
	'Wed': ['10:00', '14:00'],
	'Thu': ['10:00'],
	'Fri': ['10:00', '14:00']
}
num_people_per_meeting = 4


class PartialSolutionPrinter(ortools.sat.python.cp_model.CpSolverSolutionCallback):
	def __init__(self, meetings, solutions_to_print):
		ortools.sat.python.cp_model.CpSolverSolutionCallback.__init__(self)
		self._meetings = meetings
		if isinstance(solutions_to_print, int):
			self._solutions_to_print = range(solutions_to_print)
		elif isinstance(solutions_to_print, list):
			self._solutions_to_print = solutions_to_print
		else:
			raise Exception
		self._solution_count = 0

	def on_solution_callback(self):
		if self._solution_count in self._solutions_to_print:
			print('== Solution %i ==' % self._solution_count)
			for day in list(slots.keys()):
				for time in slots[day]:
					print('%s, %s:  ' % (day, time), end='')
					for person in people:
						if self.Value(self._meetings[(day, time, person)]):
							print('%s ' % person, end='')
					print()
				print()
			print()
		self._solution_count += 1

	def solution_count(self):
		return self._solution_count


def main():
	model = ortools.sat.python.cp_model.CpModel()

	meetings = {}
	for day in list(slots.keys()):
		for time in slots[day]:
			for person in people:
				meetings[(day, time, person)] = model.NewBoolVar('%s__%s__%s' % (day, time, person))

	# Each meeting has exactly 4 people.
	for day in list(slots.keys()):
		for time in slots[day]:
			model.Add(sum(meetings[(day, time, person)] for person in people) == num_people_per_meeting)

	# Each person has at most one meeting per day.
	for person in people:
		for day in list(slots.keys()):
			model.Add(sum(meetings[(day, time, person)] for time in slots[day]) <= 1)

	# Each person has at least one meeting per week.
	for person in people:
		model.Add(sum(meetings[(day, time, person)] for day in list(slots.keys()) for time in slots[day]) >= 1)

	# All meetings are unique. I.e. every people combination occurs at most once across all slots.
	for combination in itertools.combinations(people, num_people_per_meeting):
		c = []
		for day in list(slots.keys()):
			for time in slots[day]:
				c.append(model.NewBoolVar('(%s)__%s__%s' % (','.join(combination), day, time)))
				model.AddMinEquality(c[-1], [meetings[(day, time, person)] for person in combination])
		model.Add(sum(c) <= 1)

	# Andy cannot meet on Tuesdays.
	model.Add(sum(meetings[('Tue', time, 'Andy')] for time in slots['Tue']) == 0)

	# Adriano cannot meet on mornings.
	model.Add(sum(meetings[(day, time, 'Adriano')] for day in list(slots.keys()) for time in slots[day] if datetime.datetime.strptime(time, '%H:%M') < datetime.datetime.strptime('14:00', '%H:%M')) == 0)

	# Adriano cannot meet on Fridays.
	model.Add(sum(meetings[('Fri', time, 'Adriano')] for time in slots['Fri']) == 0)

	# Saeed cannot meet on afternoons.
	model.Add(sum(meetings[(day, time, 'Saeed')] for day in list(slots.keys()) for time in slots[day] if datetime.datetime.strptime(time, '%H:%M') >= datetime.datetime.strptime('14:00', '%H:%M')) == 0)

	# Adriana cannot meet on Wednesdays. 
	model.Add(sum(meetings[('Wed', time, 'Adriana')] for time in slots['Wed']) == 0)

	solver = ortools.sat.python.cp_model.CpSolver()
	solver.parameters.linearization_level = 0

	solutions_to_print = 1
	solution_printer = PartialSolutionPrinter(meetings, solutions_to_print)
	solver.SearchForAllSolutions(model, solution_printer)

	# Statistics.
	print()
	print('Statistics')
	print('  - conflicts	   : %i' % solver.NumConflicts())
	print('  - branches		: %i' % solver.NumBranches())
	print('  - wall time	   : %f s' % solver.WallTime())
	print('  - solutions found : %i' % solution_printer.solution_count())


if __name__ == '__main__':
	main()
