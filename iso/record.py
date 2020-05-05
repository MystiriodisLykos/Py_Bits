import functools
import typing

class Cache:
    @staticmethod
    def class_init(cls):
        class Cached(cls):
            @Cache.function
            def __new__(cls, *args, **kwargs):
                return super().__new__(cls, *args, **kwargs)
        return Cached

    @staticmethod
    def function(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = tuple(args) + tuple(kwargs)
            if key in wrapper.cache:
                return wrapper.cache[key]
            res = func(*args, **kwargs)
            wrapper.cache[key] = res
            return res
        wrapper.cache = {}
        return wrapper

def append_unique(iter_, val):
    return iter_ if val in iter_ else iter_ + iter_.__class__([val])

def _make_record(nm_tpl, bases = ()):
    nm_tpl_bases = nm_tpl.__bases__
    nm_tpl_bases = append_unique(nm_tpl_bases, Record)
    nm_tpl_bases = functools.reduce(append_unique, bases, nm_tpl_bases)
    nm_tpl.__bases__ = nm_tpl_bases
    for field in nm_tpl._fields:
        def inner(field):
            def lens(func, mapper, record):
                return mapper(lambda v: record._replace(**{field: v}),
                                func(getattr(record, field)))
            return lens
        setattr(nm_tpl, f'{field}_lens', lens)
    return Cache.class_init(nm_tpl)


class RecordMeta(typing.NamedTupleMeta):
    def __new__(mcs, typename, bases, namespace):
        nm_tpl = super().__new__(mcs, typename, bases, namespace)
        return nm_tpl if namespace.get('_root') else _make_record(nm_tpl, bases)


class Record(typing.NamedTuple, metaclass = RecordMeta):
    _root = True
    def __new__(cls, *args, bases = (), **kwargs):
        nm_tpl = super().__new__(cls, *args, **kwargs)
        return _make_record(nm_tpl, bases)

    @Cache.function
    def view(self, lens):
        return lens(lambda v: v, lambda f, v: v, self)

    @Cache.function
    def over(self, lens, f):
        return lens(f, lambda f, v: f(v), self)

    @Cache.function
    def set(self, lens, v):
        return self.over(lens, lambda _: v)

class Tuple:
    def __new__(cls, size, type_):
        return Record([(f'e{i}', type_) for i in range(size)], bases = (Vector,))

def tests():
    def lens_tests(record):
        v1, v2, v3, v4 = 101010, 202020, 303030, 404040
        t1 = record(v1, v2, v3)
        assert t1.x is v1,  'Regular named tuple access returns correct value'
        assert t1[0] is v1,  'Regular named tuple sub index returns correct value'

        assert t1.view(record.y_lens) is v2,  'View with built lens returns correct value'

        t2 = t1.set(record.y_lens, v4)
        assert t2.y is v4,  'Set produces correct value'
        assert t2.x is v1,  'Set leaves references to non-set values'

        t2 = t1.over(record.y_lens, lambda v: v*2)
        assert t2.y == t1.y*2,  'Over sets correct value'
        assert t2.x is v1,  'Over leaves references to non-set values'

    def cache_tests(record):
        v1, v2, v3, v4 = 101010, 202020, 303030, 404040
        t1 = record(v1, v2, v3)
        t2 = record(v1, v2, v3)
        assert t1 is t2,  'Creation is cached'
        times_two = lambda v: v*2
        t3 = t1.over(record.y_lens, times_two)
        t4 = t1.over(record.y_lens, times_two)
        assert t3 is t4,  'Over is cached'

    def mixin_tests(record):
          assert isinstance(record(1), Mixin),  'Supports Mixin classing'
          assert hasattr(record(1), 'mixin_method'),  'Mixin methods are carried'
          assert hasattr(record(1), 'class_method'),  'Mixin class methods are carried'
          assert hasattr(record(1), 'static_method'),  'Mixin static methods are carried'

    class TestClass(Record):
        x: int
        y: int
        z: int

    lens_tests(TestClass)
    cache_tests(TestClass)

    TestFunc = Record('TestFunc', (('x', int), ('y', int), ('z', int)))

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

    class Mixin_Class_Test(Mixin, Record):
        v1: int
    Mixin_Func_Test = Record('Mixin_Func_Test', [('v1', int)], bases = (Mixin, ))

    mixin_tests(Mixin_Class_Test)
    mixin_tests(Mixin_Func_Test)
