# budget_async
It is budget but it gets the job done.

This is a pure Python concurrency implemtation for the async/await language syntax.


## BudgetScheduler
Making coroutines on the cheap.

* lets you schedule tasks that may take a long time without making special state machines for them.
* supports non-blocking sleep() for such tasks.

[source](./budget_scheduler.py)

You can go full ham and make your entire app async, or just wrap device libraries with a non-blocking
  read/write api to spend more time looping and less time waiting.  Or I mean, go wild.  You know your
  app better than I do.  This just lets you write async/await.
If you're familiar with asyncio, this is basically just a very simple EventLoop that only lets you
  add tasks, sleep, and drive tasks.

