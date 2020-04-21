import click

class TestGroup(click.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._test = {'Test Data': 'Test String'}
    def make_context(self, *args, **kwargs):
        obj = kwargs.get('obj', {})
        obj.update(self._test)
        kwargs['obj'] = obj
        res = super().make_context(*args, **kwargs)
        return res


@click.command(cls = TestGroup)
@click.pass_context
def cli(ctx):
    pass

@cli.command()
@click.argument('entry', nargs=-1)
@click.option('-f', type = click.File('a'), default = 'test')
@click.pass_context
def start(state, entry, f):
    print(state.obj)

if __name__ == '__main__':
    cli()
