import time


def yield_one():
    """await the return value of this function to yield the processor"""
    class _CallMeNextTime:
        def __iter__(self):
            yield
        __await__ = __iter__

    return _CallMeNextTime()


class BudgetEventLoop:
    """It's budget but it works"""

    def __init__(self):
        self._tasks = []
        self._sleeping = []
        self._current = None

    async def sleep(self, seconds):
        """
        From within a coroutine, this suspends your call stack for some amount of time.

        NOTE:  Always `await` this!  You will have a bad time if you do not.

        :param seconds: Floating point; will wait at least this long to call your task again.
        """
        assert self._current is not None, 'You can only sleep from within a task'
        # This is inside the scheduler where we know generator yield is the
        #   implementation of task switching in CircuitPython.  This throws
        #   control back out through user code and up to the scheduler's
        #   __iter__ stack which will see that we've suspended _current.
        # Don't yield in async methods; only await unless you're making a library.
        delayed_continuation = yield_one()
        self._sleeping.append((time.monotonic(), seconds, self._current))
        self._sleeping.sort(key=lambda t: t[0] + t[1])  # heap would be better but hey this is budget.
        self._current = None
        await delayed_continuation  # Pretty subtle here.  This class yields once, then it continues.  This is the yield

    def create_task(self, awaitable_task):
        """
        Add a concurrent task (known as a coroutine, implemented as a generator in CircuitPython)
        Use:
          scheduler.add_task( my_async_method() )
        :param awaitable_task:  The coroutine to be driven to completion.
        """
        self._tasks.append(awaitable_task)
        return awaitable_task  # Yeah this is not a Task.  But it is awaitable, which is a subset of CPython's Task.

    def run(self, main_loop_coroutine):
        """
        Use:
            async def main_loop():
              pass

            def run():
              loop = BudgetEventLoop()
              loop.run(main_loop())

            if __name__ == '__main__':
              run()
        The crucial StopIteration exception signifies the end of a coroutine in CurcuitPython.
        Other Exceptions that reach the runner break out, stopping your app and showing a stack trace.
        """
        assert self._current is None, 'BudgetScheduler can only be advanced by 1 stack frame at a time.'
        self.create_task(main_loop_coroutine)  # a non-awaited root-level task
        while self._tasks or self._sleeping:
            for _ in range(len(self._tasks)):
                task = self._tasks.pop(0)
                self._run_task(task)
            # Consider each sleeping function at most once (avoids sleep(0) problems)
            for i in range(len(self._sleeping)):
                sleep_start, sleep_duration, task = self._sleeping[0]
                now = time.monotonic()
                if now >= sleep_start + sleep_duration:
                    self._sleeping.pop(0)
                    self._run_task(task)
                else:
                    # We didn't pop the task and it wasn't time to run it.  Only later tasks past this one.
                    break
        print('Loop completed')

    def schedule(self, hz: float, coroutine_function, *args, **kwargs):
        """
        Describe how often a method should be called.

        Your event loop will call this coroutine on the hz schedule.

        :param hz: How many times per second should the function run?
        :param event_loop: An event loop that can .sleep() and .add_task.  Like BudgetEventLoop.
        :return: Decorator for your function suitable for loop().
        """

        async def schedule_at_rate(decorated_async_fn):
            seconds_per_invocation = 1 / hz

            while True:
                start = time.monotonic()
                await decorated_async_fn(*args, **kwargs)
                seconds_to_wait = seconds_per_invocation - (time.monotonic() - start)
                await self.sleep(seconds_to_wait)
        self.create_task(schedule_at_rate(coroutine_function))

    def _run_task(self, task):
        """
        Runs a task and re-queues for the next loop if it is both (1) not complete and (2) not sleeping.
        """
        self._current = task
        try:
            task.send(None)
            # Sleep gate here, in case the current task suspended.
            # If a sleeping task re-suspends it will have already put itself in the sleeping queue.
            if self._current is not None:
                self._tasks.append(task)
        except StopIteration:
            # This task is all done.
            pass
        finally:
            self._current = None
