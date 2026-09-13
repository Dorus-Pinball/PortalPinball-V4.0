# Writing Machine Tests

Archived 2026-09-13 from
<https://raw.githubusercontent.com/missionpinball/mpf/dev/docs/testing/writing_machine_tests.rst>.
Rendered summary, not a byte-perfect copy (the source tool returned a content summary rather
than the literal `.rst`). This project's own `tests/` suite (`python -m unittest discover tests`)
already follows this general philosophy.

## Summary

MPF includes everything needed to write automated tests for a machine's logical functionality.
Tests catch configuration issues early — as config files grow more complex over time, unrelated
changes can inadvertently break existing behavior. "If you get in the habit of running your tests
often, then you'll know right away if a change that you made broke something."

A tutorial series for writing custom tests parallels MPF's general tutorial — each testing step
corresponds to the same numbered step in the main tutorial (tutorial/1, tutorial/2, etc., per the
source).

Underlying philosophy: unit testing is essential for maintaining machine configurations,
preventing regressions, and building confidence in changes over the life of a project.
