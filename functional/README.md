# Functional
Utilities - small, expressively composed building blocks to modify behaviors of functions.


## rate_limited
Limit how often a method will be invoked despite calling it many times.

[source](./rate_limited.py)

Useful for things like smoothing out `loop()` iterations, spreading expensive/periodic work out, polling sensors on
some cadence.
