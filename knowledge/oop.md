# Object-Oriented Programming

Object-oriented programming organizes software around objects that combine state and behavior. A class is a blueprint that defines attributes and methods, while an object is a concrete instance of that class.

## Encapsulation and inheritance

Encapsulation keeps an object's internal state behind a controlled public interface. This reduces coupling because callers depend on documented methods instead of implementation details. Inheritance lets a derived class reuse or specialize behavior from a base class, but composition is often clearer when the relationship is not truly "is-a."

## Polymorphism

Polymorphism lets code use different object types through a shared interface. For example, a drawing program can call `draw()` on circle and rectangle objects without knowing each concrete implementation. This makes systems easier to extend with new types.
