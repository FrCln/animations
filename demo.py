import time

from animation import AbstractAnimation


class Timer:
    def __init__(self):
        self.now = time.time()


class TimeUpdater(AbstractAnimation):
    def __init__(self, timer, tick=None):
        super().__init__(tick)
        self.timer = timer

    def update(self):
        self.timer.now = time.time()
        return True


t = Timer()
updater = TimeUpdater(t, 100)
updater.run_in_thread()

for i in range(10):
    print(t.now)
    time.sleep(1)
