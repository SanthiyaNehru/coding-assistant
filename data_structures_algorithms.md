# Data Structures and Algorithms
Choosing the right data structure decides performance. Big-O describes how running time grows with input size n.

## Big-O Complexity
O(1) constant, O(log n) logarithmic (binary search), O(n) linear (scan a list), O(n log n) efficient sorting, O(n^2) nested loops, O(2^n) naive recursion such as plain Fibonacci.

## Recursion
A recursive function calls itself and needs a base case and a recursive case. Example: factorial(n) returns 1 if n <= 1 else n * factorial(n-1). Missing base case causes RecursionError (stack overflow). Memoization with functools.lru_cache removes repeated work, turning Fibonacci from O(2^n) into O(n).

## Stack and Queue
A stack is LIFO (last in, first out): use a Python list with append and pop. A queue is FIFO: use collections.deque with append and popleft, because list.pop(0) is O(n).

## Searching and Sorting
Linear search is O(n). Binary search needs a sorted list and runs in O(log n): keep low and high pointers and compare the middle element. Bubble sort is O(n^2) and is good for learning. Python's built-in sorted() uses Timsort, O(n log n).

## Hash Tables
Python dict and set are hash tables with average O(1) lookup, insert and delete. Keys must be hashable, so lists cannot be keys but tuples can.
