import functools
import typing

import pprint

def deep_tuple(v):
    if hasattr(v, 'deep_tuple'):
      return v.deep_tuple()
    if hasattr(v, 'items'):
      return tuple((k, deep_tuple(v)) for k, v in v.items())

    try:
      if len(v) != 1:
        return tuple(deep_tuple(v_) for v_ in v)
      return (v[0],)
    except TypeError as e:
      if 'cell' in str(e):
        try:
          contents = v.cell_contents
        except ValueError as e:
          return ()
        return deep_tuple(contents)
      pass

    return v


class Cache:
    @staticmethod
    def class_new(cls):
        class Cached(cls):
            @Cache.function
            def __new__(cls, *args, **kwargs):
                return super().__new__(cls, *args, **kwargs)
        return Cached

    @staticmethod
    def function(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = deep_tuple(args) + deep_tuple(kwargs)
            if key in wrapper.cache:
                return wrapper.cache[key]
            res = func(*args, **kwargs)
            wrapper.cache[key] = res
            return res
        wrapper.cache = {}
        return wrapper


@Cache.function
def append_unique(iter_, val):
    return iter_ if val in iter_ else iter_ + iter_.__class__([val])


def _make_product(nm_tpl, bases = ()):
    nm_tpl_bases = nm_tpl.__bases__
    nm_tpl_bases = append_unique(nm_tpl_bases, Product)
    nm_tpl_bases = functools.reduce(append_unique, bases, nm_tpl_bases)
    nm_tpl.__bases__ = nm_tpl_bases
    for field in nm_tpl._fields:
        def inner(field):
            def lens(func, mapper, product):
                return mapper(lambda v: product._replace(**{field: v}),
                                func(getattr(product, field)))
            return lens
        setattr(nm_tpl, f'{field}_lens', inner(field))
    return Cache.class_new(nm_tpl)


class ProductMeta(typing.NamedTupleMeta):
    def __new__(mcs, typename, bases, namespace):
        nm_tpl = super().__new__(mcs, typename, bases, namespace)
        return nm_tpl if namespace.get('_root') else _make_product(nm_tpl, bases)


class Product(typing.NamedTuple, metaclass = ProductMeta):
    _root = True
    def __new__(cls, *args, bases = (), namespace = None, **kwargs):
        nm_tpl = super().__new__(cls, *args, **kwargs)
        nm_tpl = _make_product(nm_tpl, bases)
        if namespace:
          for k,v in namespace.items():
            setattr(nm_tpl, k, v)
        return nm_tpl

    @Cache.function
    def view(self, lens):
        return lens(lambda v: v, lambda f, v: v, self)

    @Cache.function
    def over(self, lens, f):
        return lens(f, lambda f, v: f(v), self)

    @Cache.function
    def set(self, lens, v):
        return self.over(lens, lambda _: v)


class SumMeta(type):
  def __new__(mcs, typename, bases, namespace):
    values = {}
    if '__annotations__' in namespace:
      annotations = namespace.pop('__annotations__')
      for annotation, type_ in annotations.items():
        if issubclass(type_, Product) or issubclass(type_, Sum):
          values[annotation] = type_
        else:
          values[annotation] = Product(annotation, [(annotation.lower(), type_)], namespace = namespace)

    namespace.update(values)
    return super().__new__(mcs, typename, bases, namespace)

class Sum(metaclass = SumMeta):
  _root = True

def product_tests():
    def lens_tests(product):
        v1, v2, v3, v4 = 101010, 202020, 303030, 404040
        t1 = product(v1, v2, v3)
        assert t1.x is v1,  'Regular named tuple access returns correct value'
        assert t1[0] is v1,  'Regular named tuple sub index returns correct value'

        assert t1.view(product.y_lens) is v2,  'View with built lens returns correct value'

        t2 = t1.set(product.y_lens, v4)
        assert t2.y is v4,  'Set produces correct value'
        assert t2.x is v1,  'Set leaves references to non-set values'

        t2 = t1.over(product.y_lens, lambda v: v*2)
        assert t2.y == t1.y*2,  'Over sets correct value'
        assert t2.x is v1,  'Over leaves references to non-set values'

    def cache_tests(product):
        v1, v2, v3, v4 = 101010, 202020, 303030, 404040
        t1 = product(v1, v2, v3)
        t2 = product(v1, v2, v3)
        assert t1 is t2,  'Creation is cached'
        times_two = lambda v: v*2
        t3 = t1.over(product.y_lens, times_two)
        t4 = t1.over(product.y_lens, times_two)
        assert t3 is t4,  'Over is cached'

    def mixin_tests(product):
          assert isinstance(product(1), Mixin),  'Supports Mixin classing'
          assert hasattr(product(1), 'mixin_method'),  'Mixin methods are carried'
          assert hasattr(product(1), 'class_method'),  'Mixin class methods are carried'
          assert hasattr(product(1), 'static_method'),  'Mixin static methods are carried'

    class TestClass(Product):
        x: int
        y: int
        z: int

    lens_tests(TestClass)
    cache_tests(TestClass)

    TestFunc = Product('TestFunc', (('x', int), ('y', int), ('z', int)))

    lens_tests(TestFunc)
    cache_tests(TestFunc)

    class Mixin():
        def mixin_method(self, v):
            pass
        @classmethod
        def class_method(cls, v):
            pass
        @staticmethod
        def static_method(v):
            pass

    class Mixin_Class_Test(Mixin, Product):
        v1: int
    Mixin_Func_Test = Product('Mixin_Func_Test', [('v1', int)], bases = (Mixin, ))

    mixin_tests(Mixin_Class_Test)
    mixin_tests(Mixin_Func_Test)

def sum_tests():
  class S1(Sum):
    X: int
    Y: str

  assert not hasattr(S1, '__annotations__'),  'Annotations removed'
  assert issubclass(S1.X, Product),  'Creates Products when needed'

  class P1(Product):
    v1: int
    v2: str

  class S2(Sum):
    P: P1
    S: S1

  assert S2.P is P1,  'Can have products'
  assert S2.S is S1,  'Can have sums'
