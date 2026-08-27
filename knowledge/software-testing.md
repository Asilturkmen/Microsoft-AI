# Software Testing

Software testing supplies evidence that a system behaves as intended and helps reveal defects before users encounter them. A useful test is repeatable, checks an observable outcome, and fails with a clear explanation when behavior changes.

## Test levels

Unit tests isolate small functions or classes and run quickly. Integration tests verify that components such as code and a database work together. End-to-end tests exercise a complete user-visible workflow and are slower, so a balanced suite uses many focused unit tests and fewer broad end-to-end tests.

## Test doubles and regression

Mocks and fakes can make unit tests deterministic at external boundaries, but they cannot prove that a real dependency is configured correctly. A regression test records behavior for a previously found bug so the same defect is detected if it returns.
