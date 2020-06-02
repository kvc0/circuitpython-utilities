from unittest import TestCase

from budget_async.budget_scheduler import BudgetScheduler


class TestBudgetScheduler(TestCase):
    def test_add_task(self):
        bs = BudgetScheduler()
        ran = False

        async def foo():
            nonlocal ran
            ran = True
        bs.add_task(foo())
        next(bs)
        self.assertTrue(ran)
