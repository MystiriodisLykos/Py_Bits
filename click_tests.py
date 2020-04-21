import click

class TestGroup(click.Group):
    def __init__(self, *args, **kwargs):
        print('TestGroup, self')
        # print(args, kwargs)
        super().__init__(*args, **kwargs)
        self._test = 'X'
    def get_command(self, ctx, cmd_name):
        command = super().get_command(ctx, cmd_name)
        print(ctx.scope())
        return command

@click.command(cls = TestGroup)
@click.pass_context
def cli(ctx):
    # with open('entries.txt', 'a') as file:
    ctx.obj = 'ctx test'

@cli.command()
@click.argument('entry', nargs=-1)
@click.option('-f', type = click.File('a'), default = 'test')
@click.pass_context
def start(state, entry, f):
    pass

if __name__ == '__main__':
    cli()
