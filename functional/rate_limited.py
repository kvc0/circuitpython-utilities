import time


def rate_limited(hz: float):
    """
    Describe how often a method should be called from your loop().

    You call this every loop() iteration and it invokes your method
      on your schedule.

    :param hz: How many times per second should the function run?
    :return: Decorator for your function suitable for loop().
    """
    def decorator_rate_limit(decorated_fn):
        last_invocation = 0
        nanos_per_invocation = 1000000000 / hz
        rate_limited_value = None

        def rate_limited_fn(*args, **kwargs):
            nonlocal last_invocation
            nonlocal rate_limited_value
            now = time.monotonic_ns()
            if now - last_invocation > nanos_per_invocation:
                # Normally we can schedule at the intended rate.
                last_invocation += nanos_per_invocation
                if last_invocation + nanos_per_invocation < now:
                    # If we're falling behind, fall back to "with fixed delay"
                    last_invocation = now
                rate_limited_value = decorated_fn(*args, **kwargs)
            return rate_limited_value
        return rate_limited_fn
    return decorator_rate_limit
