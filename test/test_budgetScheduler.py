import time
from unittest import TestCase

from budget_async.budget_loop import BudgetEventLoop


class TestBudgetScheduler(TestCase):
    def test_add_task(self):
        bs = BudgetEventLoop()
        ran = False

        async def foo():
            nonlocal ran
            ran = True
        bs.create_task(foo())
        next(bs)
        self.assertTrue(ran)

    def test_sleep(self):
        bs = BudgetEventLoop()
        complete = False

        async def foo():
            nonlocal complete
            await bs.sleep(0.1)
            complete = True
        bs.create_task(foo())
        start = time.monotonic()
        while not complete and time.monotonic() - start < 1:
            next(bs)
        self.assertTrue(complete)
