# Object Oriented Programming
OOP organises code into classes (blueprints) and objects (instances).

## Classes and Objects
class Student: def __init__(self, name): self.name = name. The __init__ method is the constructor and self refers to the current instance. Create an object with s = Student("Asha").

## Four Pillars
Encapsulation bundles data and methods and hides internals (use a leading underscore by convention). Inheritance lets a child class reuse a parent: class Dog(Animal). Polymorphism lets different classes share a method name with different behaviour. Abstraction exposes only what is necessary, for example with abc.ABC and abstractmethod.

## Special Methods
__str__ controls print output, __repr__ gives a debugging representation, __eq__ defines equality, __len__ supports len(obj). Use @property for controlled attribute access and @staticmethod or @classmethod for methods not tied to an instance.
