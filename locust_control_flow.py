import locust
import locust.env
import gevent
import random

def bind(binder):
  def decorator(func):
    def wrapper(self):
      func(self)
      next_ = binder(self)
      if next_:
        self.tasks.insert(self._task_index, next_)
    return wrapper
  return decorator

if_ = lambda bool_, next_: bind(lambda self: next_ if bool_(self) else None)

class Test(locust.SequentialTaskSet):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if not hasattr(self, 'og_tasks'):
      self.og_tasks = self.tasks
    self.tasks = list(self.og_tasks)
    self.n = 3

  @locust.task
  def _1(self):
    print('normal 1')

  @locust.task
  @bind(lambda self: Test._r if self.n != 0 else None)
  def _r(self):
    print(f'recursion {self.n}')
    self.n -= 1
  
  @locust.task
  @if_(lambda self: self.i != 0, _1)
  def _if(self):
    self.i = random.randint(0,1)
    print(f'if {self.i} == 1 then normal 1')
  
  @locust.task
  def _2(self):
    print('normal 2')
  
  @locust.task
  def stop(self):
    print('stop')
    self.interrupt()

class User(locust.User):
  tasks = [Test]
  wait_time = lambda *_, **__: 1

# setup Environment and Runner
env = locust.env.Environment(user_classes=[User])
env.create_local_runner()

# start a greenlet that periodically outputs the current stats
# gevent.spawn(stats_printer(env.stats))

# start the test
env.runner.start(1, hatch_rate=10)

# in 60 seconds stop the runner
gevent.spawn_later(60, lambda: env.runner.quit())

# wait for the greenlets
env.runner.greenlet.join()
