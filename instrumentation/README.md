#Instrumentation
Tools to help debug code and understand performance over time.

## Metrics
Lightweight timings and measurements you can leave after development.

[source](./metrics.py)

Metrics apis respect a global `metrics_enabled` boolean to avoid all allocation and method invocations possible when 
you disable them.  The runtime cost for disabled metrics imports, decorators and method invocations is zero or close
to zero.


### What you get
Profile methods you are interested in, by the call stacks they spend time in.
```
--------------   Metrics   -------------------------------------------------------------------------------------------------

--------------   Timers    ------------------------------------------------------------------------
Elapsed: 10.0 seconds
Stack                               | Avg (ms) | Min (ms) | Max (ms) |    Count |  Sum (s) |      %
loop                                |    1.224 |    0.411 |   79.902 |     6543 |    8.007 |  80.0%
|-update_state                      |   56.718 |   50.065 |   77.466 |       51 |    2.893 |  28.9%
| |-s4                              |   23.271 |   17.917 |   44.781 |       51 |    1.187 |  11.9%
| | |-loop                          |   11.916 |    7.755 |   34.717 |       51 |    0.608 |   6.1%
| | | |-change_loop_uptime          |    3.005 |    0.160 |   17.455 |       51 |    0.153 |   1.5%
| | | |-change_loop_print_remain    |    0.361 |    0.159 |    8.459 |       51 |    0.018 |   0.2%
| | | |-change_loop_xyz             |    0.312 |    0.157 |    7.709 |       51 |    0.016 |   0.2%
| | | |-change_loop_spd_factor      |    0.175 |    0.164 |    0.359 |       51 |    0.009 |   0.1%
| | | |-change_loop_extr_factor     |    0.174 |    0.163 |    0.433 |       51 |    0.009 |   0.1%
| | | |-change_loop_temps           |    0.172 |    0.157 |    0.332 |       51 |    0.009 |   0.1%
| | | |-change_loop_fans            |    0.172 |    0.165 |    0.354 |       51 |    0.009 |   0.1%
| | | |-change_loop_print_s         |    0.168 |    0.157 |    0.348 |       51 |    0.009 |   0.1%
| | | |-change_loop_warmup_s        |    0.168 |    0.160 |    0.334 |       51 |    0.009 |   0.1%
| | | |-change_loop_layer_s         |    0.167 |    0.157 |    0.446 |       51 |    0.009 |   0.1%
| | | |-change_loop_speed           |    0.167 |    0.157 |    0.333 |       51 |    0.008 |   0.1%
| | | |-change_loop_file_completed  |    0.166 |    0.157 |    0.512 |       51 |    0.008 |   0.1%
| | | |-change_loop_print_completed |    0.166 |    0.157 |    0.335 |       51 |    0.008 |   0.1%
| | | |-change_loop_layer_n         |    0.164 |    0.157 |    0.363 |       51 |    0.008 |   0.1%
| | | |-change_loop_extruder        |    0.164 |    0.157 |    0.345 |       51 |    0.008 |   0.1%
| | | |-change_loop_sensors         |    0.164 |    0.157 |    0.373 |       51 |    0.008 |   0.1%
| | | |-change_loop_duet_temp       |    0.163 |    0.157 |    0.335 |       51 |    0.008 |   0.1%
| | | |-change_loop_status          |    0.163 |    0.157 |    0.332 |       51 |    0.008 |   0.1%
| | |-change_update_uptime          |    0.322 |    0.165 |    7.692 |       51 |    0.016 |   0.2%
| | |-change_update_print_s         |    0.320 |    0.166 |    7.588 |       51 |    0.016 |   0.2%
| | |-change_update_print_completed |    0.314 |    0.163 |    7.582 |       51 |    0.016 |   0.2%
| | |-change_update_fans            |    0.266 |    0.259 |    0.470 |       51 |    0.014 |   0.1%
| | |-change_update_temps           |    0.243 |    0.212 |    0.439 |       51 |    0.012 |   0.1%
| | |-change_update_xyz             |    0.205 |    0.198 |    0.368 |       51 |    0.010 |   0.1%
| | |-change_update_speed           |    0.203 |    0.192 |    0.389 |       51 |    0.010 |   0.1%
| | |-change_update_sensors         |    0.187 |    0.181 |    0.397 |       51 |    0.010 |   0.1%
| | |-change_update_warmup_s        |    0.180 |    0.171 |    0.341 |       51 |    0.009 |   0.1%
| | |-change_update_extr_factor     |    0.177 |    0.166 |    0.422 |       51 |    0.009 |   0.1%
| | |-change_update_extruder        |    0.176 |    0.164 |    0.353 |       51 |    0.009 |   0.1%
| | |-change_update_status          |    0.176 |    0.164 |    0.368 |       51 |    0.009 |   0.1%
| | |-change_update_print_remain    |    0.174 |    0.163 |    0.360 |       51 |    0.009 |   0.1%
| | |-change_update_file_completed  |    0.170 |    0.163 |    0.406 |       51 |    0.009 |   0.1%
| | |-change_update_layer_s         |    0.170 |    0.163 |    0.390 |       51 |    0.009 |   0.1%
| | |-change_update_spd_factor      |    0.169 |    0.163 |    0.354 |       51 |    0.009 |   0.1%
| | |-change_update_layer_n         |    0.166 |    0.159 |    0.349 |       51 |    0.008 |   0.1%
| | |-change_update_duet_temp       |    0.162 |    0.154 |    0.333 |       51 |    0.008 |   0.1%
| |-duet.read_response_line         |   17.344 |   16.370 |   25.084 |       51 |    0.885 |   8.8%
| | |-read_into_buffer              |   16.059 |    7.617 |   16.818 |       51 |    0.819 |   8.2%
| | |-copy_buffer                   |    0.196 |    0.188 |    0.361 |       51 |    0.010 |   0.1%
| |-json.load                       |   11.617 |   11.156 |   21.254 |       51 |    0.592 |   5.9%
|-rotary                            |    0.451 |    0.413 |   14.446 |     1257 |    0.566 |   5.7%
|-menustack                         |    0.203 |    0.176 |    7.578 |      824 |    0.167 |   1.7%
|-lights                            |    0.215 |    0.205 |    0.459 |       73 |    0.016 |   0.2%

-------------  Measurements   -------------------------------------------------------
Measurement |      avg |      min |      max |    count
free_memory |   14.697 |    1.781 |   31.484 |       32

Metrics report completed in 138.541ms
----------------------------------------------------------------------------------------------------------------------------
```


### How you use it
Decorate your methods with `@timer()`s.  When you're done working on perf, un-set `builtins.metrics_enabled` and your
  methods will not be decorated anymore (clean stacks, no loop overhead).

Here's an example program that spends some time and prints metrics about it every 10 seconds.
```python
import builtins
builtins.metrics_enabled = True
from instrumentation.metrics import timer, log_metrics

import time
import random


@timer('a while')
def runs_a_while():
    time.sleep(0.100 * random.random())


@timer('faster')
def runs_faster():
    time.sleep(0.050 * random.random())


@timer('fastest')
def runs_fastest():
    time.sleep(0.001 * random.random())


@timer('composite')
def composite(loop_number):
    loop_index = loop_number % 100
    if loop_index < 50:
        runs_fastest()
    elif loop_index < 95:
        runs_faster()
    else:
        runs_a_while()


@timer('loop')
def loop():
    for _ in range(3):
        runs_fastest()
    composite()
    log_metrics(target_seconds=10)  # Prints every 10 seconds


def run():
    # ----------------------------------------------
    # Run program forever waiting for input.
    while True:
        loop()


if __name__ == '__main__':
    run()
```

## memory_logging
Enable/disable-able detailed debug memory logging.

[source](./memory_logging.py)

By calling `print_mem('imported foo')` after each import, or after instantiating some library you can dig into who is using all that memory.

When you're done, you can set `builtins.memory_logging_enabled = False` or just leave it unset and leave the logging code there for when you
need to debug a regression...
