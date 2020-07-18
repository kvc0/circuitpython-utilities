import time

#
# Enable metrics by setting builtins.metrics_enabled = True before importing metrics the first time.
#
# import builtins
# builtins.metrics_enabled = True
# import metrics
#
# You can add @timer to all methods you want to time; when you start up with metrics disabled, the
#  function you decorate is unaltered.  Only when metrics is enabled do you pay any runtime cost.
#
# Call metrics.log_metrics() periodically.
# This will cost no more than a single unconditional `pass` when metrics is disabled/
#
try:
    global metrics_enabled
    if metrics_enabled:
        print('Enabling metrics instrumentation')
except NameError:
    # Set False by default to remove runtime overhead of decorators and make everything else early-out
    metrics_enabled = False


def timer(name):
    """
    @Decorator
    Record milliseconds per invocation when started with metrics_enabled.
    @:param name A string name for the function to be decorated.
    """
    if type(name) is str:
        def arg_wrapper(function):
            if not metrics_enabled:
                #  No runtime cost when metrics are disabled
                return function

            def wrapper(*args, **kwargs):
                with Timer(name):
                    return function(*args, **kwargs)
            return wrapper
        return arg_wrapper


def atimer(name):
    """
    @Decorator
    Record milliseconds per invocation when started with metrics_enabled.
    @:param name A string name for the function to be decorated.
    """
    if type(name) is str:
        def arg_wrapper(function):
            if not metrics_enabled:
                #  No runtime cost when metrics are disabled
                return function

            async def wrapper(*args, **kwargs):
                with Timer(name):
                    return await function(*args, **kwargs)
            return wrapper
        return arg_wrapper


if metrics_enabled:
    def measure(name, observation):
        """
        Record some numeric observation.
        Gets aggregated now, and later is printed when you call log_metrics()
        """
        if name not in measurements:
            measurements[name] = _StatisticSet()
        measurements[name].observe(observation)


    class Timer:
        """
        Prefer @timer(name) to this as there is 0 runtime cost on that strategy when
          metrics is disabled.
        Tracks time for scope open to scope close (use in a `with Timer('name'):` block).
        Emits the time into the stack tracker.
        Get your results by calling log_metrics() periodically.
        """

        def __init__(self, name):
            self.name = name

        def __enter__(self):
            self.start = time.monotonic_ns()
            self.timer = timer_stack[-1].get(self.name, None)
            if self.timer is None:
                self.timer = _TimerNode(self.name)
                timer_stack[-1][self.name] = self.timer
            self.pushed_timer = timer_stack[-1] is not self.timer
            if self.pushed_timer:
                timer_stack.append(self.timer)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            elapsed = time.monotonic_ns() - self.start
            if self.pushed_timer:
                timer_stack.pop(-1)
            self.timer.observe(elapsed / 1000000)


    def log_metrics(target_seconds=10) -> None:
        """
        Call on a timer, like every 10 seconds or every 60 seconds.  Whatever tickles your fancy.
        """
        global last_timer_reset
        start = time.monotonic_ns()
        elapsed_nanos = start - last_timer_reset
        if (start - last_timer_reset) < (target_seconds * 1000000000):
            return
        last_timer_reset = start
        print('\n\n--------------   Metrics   -------------------------------------------------------------------------------------------------')
        # Print out the recursive formatted timer stack
        timer_stack[0].print(elapsed_nanos / 1000000)
        timer_stack[0].reset()

        # Print out the literal measurements table
        if len(measurements) > 0:
            maxname = max(len(name) for name in measurements)
            stackname_format = '{{:{}s}}'.format(maxname)
            # Print measurement header
            print('\n-------------  Measurements   ', end='')
            for _ in range(maxname + 11*4):
                print('-', end='')
            print()
            print('{{:>{}s}}'.format(maxname).format('Measurement'), end='')
            print(' | {avg:>8s} | {min:>8s} | {max:>8s} | {count:>8s}'.format(
                avg='avg', min='min', max='max', count='count'
            ))

            for name, stats in measurements.items():
                print('{stackname} | {avg:8.3f} | {min:8.3f} | {max:8.3f} | {count:8d}'.format(
                    stackname=stackname_format.format(name),
                    avg=stats.sum / max(1, stats.count),
                    min=stats.min,
                    max=stats.max,
                    count=stats.count,
                ))
                stats.reset()
        print('\nMetrics report completed in {}ms'.format((time.monotonic_ns() - start) / 1000000))
        print('----------------------------------------------------------------------------------------------------------------------------\n\n')


    ########################################################################################
    #
    # Framework tools below.  You probably only care about what's above here.
    #
    ########################################################################################


    class _StatisticSet:
        def __init__(self):
            self.min = float('inf')
            self.max = -float('inf')
            self.sum = 0
            self.count = 0

        def observe(self, value):
            self.min = min(self.min, value)
            self.max = max(self.max, value)
            self.sum += value
            self.count += 1

        def reset(self):
            self.min = float('inf')
            self.max = -float('inf')
            self.sum = 0
            self.count = 0

        def __str__(self):
            # 41 chars
            return 'avg:{avg:8.3f}  min:{min:8.3f}  max:{max:8.3f}  count:{count:6d}'.format(
                avg=self.sum / self.count,
                min=self.min,
                max=self.max,
                count=self.count,
            )

    class _TimerNode:
        def __init__(self, name):
            self.min = float('inf')
            self.max = -float('inf')
            self.sum = 0
            self.count = 0
            self.children = {}

        def observe(self, value):
            self.min = min(self.min, value)
            self.max = max(self.max, value)
            self.sum += value
            self.count += 1

        def reset(self):
            """Called on the root node"""
            self.children.clear()

        def print(self, elapsed_ms):
            # Root node
            # 123 characters wide
            if len(self.children) == 0:
                print('no timers encountered')
                return
            max_namewidth = max(child._namewidth(name) for name, child in self.children.items())
            header_format_string = '{{:{:d}s}} | {:>8s} | {:>8s} | {:>8s} | {:>8s} | {:>8s} | {:>6s}'
            step_1_format = header_format_string.format(max_namewidth, 'Avg (ms)', 'Min (ms)', 'Max (ms)', 'Count', 'Sum (s)', '%')
            format_string = step_1_format.format('Stack')
            header_preamble = '\n--------------   Timers    '
            print(header_preamble, end='')
            for _ in range(max(0, len(format_string) - len(header_preamble))):
                print('-', end='')
            print()

            print('Elapsed: {:.1f} seconds'.format(elapsed_ms / 1000))
            print(format_string)
            # By time spent descending
            for name, child in sorted(self.children.items(), key=lambda c: c[1].sum, reverse=True):
                child._print(name, 0, elapsed_ms, max_namewidth)

        def _print(self, name, level, elapsed_ms, max_namewidth):
            print(''.join('| ' for _ in range(max(0, level))), end='')
            if level > 0:
                print('\b-', end='')
            leading_chars = max(len(name), max_namewidth - 2*level)
            format_string = '{{:{}s}} | {{:8.3f}} | {{:8.3f}} | {{:8.3f}} | {{:8d}} | {{:8.3f}} | {{:6.1%}}'.format(leading_chars)
            percent_time_this_node = self.sum / elapsed_ms
            print(format_string.format(name, self.sum / max(1, self.count), self.min, self.max, self.count, self.sum / 1000, percent_time_this_node))
            for name, child in sorted(self.children.items(), key=lambda c: c[1].sum, reverse=True):
                child._print(name, level+1, elapsed_ms, max_namewidth)

        def _namewidth(self, name, level=0):
            self_length = max(1, level * 2 + len(name))
            return self_length if len(self.children) == 0 else max(
                max(child._namewidth(name, level+1) for name, child in self.children.items()),
                self_length
            )

        def get(self, item, default):
            return self.children.get(item, default)

        def __setitem__(self, key, value):
            self.children[key] = value

        def __str__(self):
            # 41 chars
            return 'avg:{avg:8.3f}  min:{min:8.3f}  max:{max:8.3f}  count:{count:6d}'.format(
                avg=self.sum / self.count,
                min=self.min,
                max=self.max,
                count=self.count
            )


    measurements = {}
    timer_stack = [_TimerNode('root')]
    last_timer_reset = time.monotonic_ns()
else:
    # Stubs so you don't have to change your code, just the global metrics_enabled boolean when you're doing perf work.

    def measure(_, __):
        pass


    def log_metrics():
        pass


    class Timer:
        def __init__(self, _):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
