import locust
import locust.env
import gevent
import random

def extractor(func):
  def wrapper(self):
    response = func(self)
    if (ext := getattr(self, f'{func.__name__}_ext', None)):
      ext(self, response)
  return wrapper


class CustomMeta(locust.user.sequential_taskset.SequentialTaskSetMeta):
  def __new__(cls, *args, **kwargs):
    res = super().__new__(cls, *args, **kwargs)
    res.tasks = [extractor(task) for task in res.tasks]
    def stop(self):
      self.interrupt()
    res.tasks.append(stop)
    return res


class Login(locust.SequentialTaskSet, metaclass = CustomMeta):
  @locust.task
  def login(self):
    print('login')
    return {'login': random.randint(0,1)}


class Master(locust.TaskSet):
  @locust.task
  def other(self):
    print('other')
  
  @locust.task
  class Login_Validate(Login):

    @staticmethod
    def login_ext(self, response):
      assert response['login'] == True


class User(locust.User):
  tasks = [Master]
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
