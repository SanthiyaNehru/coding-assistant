# Python Basics
Python is a high-level, dynamically typed language. Variables are created on assignment: x = 5. Common types: int, float, str, bool, list, tuple, dict, set.

## Lists and Loops
A list is an ordered, mutable collection: nums = [1, 2, 3]. Use nums.append(4) to add, nums.pop() to remove the last item, and slicing nums[1:3]. A for loop iterates: for n in nums: print(n). Use range(start, stop, step) for counting loops. List comprehension: squares = [x*x for x in range(5)]. A while loop repeats while a condition is true; make sure the condition eventually becomes false to avoid infinite loops.

## Functions
Define with def name(params): and return a value with return. Default arguments: def greet(name="World"). Never use a mutable default such as def f(x=[]) because the same list is shared between calls. Use *args and **kwargs for flexible arguments. Lambdas are small anonymous functions: lambda x: x + 1.

## Dictionaries and Sets
A dict maps keys to values: d = {"a": 1}. Access with d["a"] or d.get("a", default). Iterate with d.items(). A set stores unique items and supports union, intersection and difference with fast membership tests.

## File Handling and Exceptions
Use with open("f.txt") as f: so the file closes automatically. Handle errors with try / except / finally. Catch specific exceptions such as ValueError or FileNotFoundError, not a bare except.
