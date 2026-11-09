# Debugging Guide
Debugging is a systematic process: reproduce the bug, read the error, isolate the cause, fix, and re-test.

## Reading a Traceback
Read from the bottom: the last line shows the exception type and message, and the lines above show where it happened. The most recent call is last.

## Common Python Errors
SyntaxError: invalid syntax such as a missing colon or unmatched bracket. IndentationError: inconsistent spaces or tabs. NameError: a variable is used before it is defined or misspelled. TypeError: wrong type used, for example adding a str to an int; convert with int() or str(). IndexError: list index out of range; indexes start at 0 and end at len-1. KeyError: dictionary key not found; use d.get(). ZeroDivisionError: dividing by zero; check the divisor first. AttributeError: object has no such attribute or method. ModuleNotFoundError: package not installed; run pip install. RecursionError: missing or unreachable base case.

## Logic Bugs
Off-by-one errors in loops and ranges, using = instead of == in comparisons, modifying a list while iterating over it, forgetting to return a value, and integer vs float division (/ vs //). Use print statements, the debugger (pdb), and small test inputs to trace variable values.

## Good Habits
Write small functions, test edge cases (empty input, zero, negative numbers), use meaningful names, and commit working code often.
