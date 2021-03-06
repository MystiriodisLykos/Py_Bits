import locust
import locust.env
import gevent
import random

# chain :: (a -> f a) -> f a -> f a
def chain(chainer):
  def decorator(func):
    def wrapper(self):
      func(self)
      next_ = chainer(self)
      if next_:
        self.tasks.insert(self._task_index, next_)
    return wrapper
  return decorator

conditional_next = lambda bool_, next_, else_ = None: chain(lambda self: next_ if bool_(self) else else_)

def if_(bool_):
  def decorator(func):
    res = chain(lambda self: func if bool_(self) else res._else)(lambda _: None)
    def else_(_else):
      res._else = _else
      return _else
    res.else_ = else_
    res._else = None
    return res

  return decorator

class Test(locust.SequentialTaskSet):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if not hasattr(self, 'og_tasks'):
      self.og_tasks = self.tasks
    self.tasks = list(self.og_tasks)
    self.n = 3

  @locust.task
  @if_(lambda self: random.randint(0,1) == 0)
  def _i(self):
    print('if was true')

  @_i.else_
  def _e(self):
    print('if was false')

  @locust.task
  def _1(self):
    print('normal 1')

  @locust.task
  @chain(lambda self: Test._r if self.n != 0 else None)
  def _r(self):
    print(f'recursion {self.n}')
    self.n -= 1

  @locust.task
  @conditional_next(lambda self: self.i != 0, _1)
  def _if(self):
    self.i = random.randint(0,1)
    print(f'conditional next if {self.i} == 1 then normal 1')

  def conditional_nextpositive(self):
    print('if was true')

  def conditional_nextnegative(self):
    print('if was false')

  @locust.task
  @conditional_next(lambda self: self.i != 0, conditional_nextpositive, conditional_nextnegative)
  def _if2(self):
    self.i = random.randint(0,1)
    print(f'conditional next if {self.i} == 1')

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

# start the test
env.runner.start(1, hatch_rate=10)

# in 60 seconds stop the runner
gevent.spawn_later(60, lambda: env.runner.quit())

# wait for the greenlets
env.runner.greenlet.join()
