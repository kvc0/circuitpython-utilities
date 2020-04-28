# Enable memory logging by setting builtins.memory_logging_enabled = True before importing this the first time.
# import builtins
# builtins.memory_logging_enabled = True
try:
    global memory_logging_enabled
    if memory_logging_enabled:
        print('Enabling memory instrumentation')
except NameError:
    # Set False by default to remove runtime overhead of decorators and make everything else early-out
    memory_logging_enabled = False

if memory_logging_enabled:
    import gc
    import time

    baseline = gc.mem_alloc()
    last_invocation = time.monotonic_ns()

    # @instrumentation.metrics.timer('print_mem')
    def print_mem(when: str):
        global baseline
        global last_invocation
        alloc_start = gc.mem_alloc()
        gc.collect()
        alloc_after = gc.mem_alloc()
        garbage = alloc_start - alloc_after
        now = time.monotonic_ns()
        print('  {:>8.1f}ms {:36s}:  free:{:6d} alloc:{:6d}  difference:{:6d}  garbage:{:6d}'.format(
            (now - last_invocation) / 1000000,
            when,
            gc.mem_free(),
            alloc_after,
            alloc_after-baseline,
            garbage
        ))
        baseline = alloc_after
        last_invocation = now
else:
    def print_mem(when):
        pass