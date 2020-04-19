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
    
    def view(self, lens):
        return lens(lambda v: v, lambda f, v: v, self)

    def over(self, lens, f):
        f_ = f if callable(f) else lambda v: f
        return lens(lambda v: f_(v), lambda f, v: f(v), self)
