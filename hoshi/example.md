# Example Behavior

Describe the behavior you want to test in plain English here.
For example: Users should be able to run a simple echo command
and verify its output.

<!-- hoshi:spec -->

## Scenario: Echo command works

- Given environment is loaded from `.env`
- When we run command `echo hello hoshi`
- Then exit code is `0`
- Then stdout contains `hello hoshi`
