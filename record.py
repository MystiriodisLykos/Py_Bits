import functools
import typing

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
        setattr(nm_tpl, f'{field}_lens', inner(field))
    return nm_tpl


class RecordMeta(typing.NamedTupleMeta):
    def __new__(mcs, typename, bases, namespace):
        nm_tpl = super().__new__(mcs, typename, bases, namespace)
        return nm_tpl if namespace.get('_root') else _make_record(nm_tpl, bases)


class Record(typing.NamedTuple, metaclass = RecordMeta):
    _root = True
    def __new__(cls, *args, bases = (), **kwargs):
        nm_tpl = super().__new__(cls, *args, **kwargs)
        return _make_record(nm_tpl, bases)

    def view(self, lens):
        return lens(lambda v: v, lambda f, v: v, self)

    def over(self, lens, f):
        return lens(f, lambda f, v: f(v), self)

    def set(self, lens, v):
        return self.over(lens, lambda _: v)


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

    class TestClass(Record):
        x: int
        y: int
        z: int

    lens_tests(TestClass)

    TestFunc = Record('TestFunc', (('x', int), ('y', int), ('z', int)))

    lens_tests(TestFunc)
