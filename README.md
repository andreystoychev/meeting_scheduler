## Overview
A little programme for solving scheduling problems using a constraint programming (CP) solver [OR-Tools](https://github.com/google/or-tools).

It defines a list of people and meeting slots, adds Boolean variables to the CP model for every combination of people and slots and for every combination of 4 people per slot, and adds logical and linear constraints on the variables to the CP model. Then, it solves the model and prints out solutions and statistics.

## Usage
First, make sure you have Python 3. Then, [install OR-Tools](https://developers.google.com/optimization/install).
<br>
To run the programme:
```
python ./schedule_meetings.py --rand N M | --num N | --id ID [ID ...]

arguments:
  --rand N M          print N random solutions from the first M solutions
  --num N             print the first N solutions
  --id ID [ID ...]    print the solutions with the specified IDs
```
E.g. to print 4 random solutions from the first 100'000 solutions, run
```
python ./schedule_meetings.py --rand 4 100000
```
and wait for the programme to finish (around 2 minutes).

There are typically too many solutions to wait for the programme to finish by itself, so when using the `--num` switch, you probably want to interrupt the execution after a bit, e.g. with `Ctrl-C`.

The CP solver seems to be deterministic, as it always produces the same solutions in the same order, given the same set of variables and constraints. 

By default, only the first solution is printed to standard output. If you want to print more solutions, change `solutions_to_print` to another integer. And if you want to print specific solutions, change `solutions_to_print` to a list of solutions numbers. E.g. `solutions_to_print = [0 4 9]` will print the first, fifth, and tenth solutions.

## Constraints

### Global

Each meeting has exactly 4 people.
<br>
Each person has at most one meeting per day.
<br>
Each person has at least three meetings per week.
<br>
Each person has at most four meetings per week.
<br>
All meetings are unique in a week. I.e. every combination of 4 people occurs at most once across all slots in a week.

### Personal

Andy cannot meet on Tuesdays.
<br>
Adriano cannot meet on mornings.
<br>
Adriano cannot meet on Fridays.
<br>
Saeed cannot meet on afternoons.
<br>
Adriana cannot meet on Wednesdays.