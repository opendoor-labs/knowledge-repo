import os
import types
import inspect
import textwrap

class KnowledgeDeployer(object):

    def __init__(self,
                 knowledge_builder,
                 host='0.0.0.0',
                 port=7000,
                 workers=4,
                 timeout=60):
        assert isinstance(knowledge_builder, (str, types.FunctionType)), "Unknown builder type {}".format(type(knowledge_builder))
        self.knowledge_builder = knowledge_builder
        self.host = host
        self.port = port
        self.workers = workers
        self.timeout = timeout

    @property
    def builder_str(self):
        if isinstance(self.knowledge_builder, types.FunctionType):
            out = []
            for nl, cell in zip(self.knowledge_builder.__code__.co_freevars, self.knowledge_builder.__closure__):
                if isinstance(cell.cell_contents, str):
                    out.append('{} = "{}"'.format(nl, cell.cell_contents.replace('"','\\"')))
                else:
                    out.append('{} = {}'.format(nl, cell.cell_contents))
            out.append(textwrap.dedent(inspect.getsource(self.knowledge_builder)))
            return '\n'.join(out)
        return self.knowledge_builder

    @property
    def builder_func(self):
        if isinstance(self.knowledge_builder, str):
            knowledge_builder = 'def get_app():\n\t' + self.knowledge_builder.replace('\n','\t') + '\n\treturn app'
            namespace = {}
            exec(knowledge_builder, namespace)
            return namespace['get_app']
        return self.knowledge_builder

    def write_temp_files(self):
        import tempfile
        tmp_dir = tempfile.mkdtemp()
        tmp_path = os.path.join(tmp_dir, 'server.py')

        kr_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))

        out = []
        out.append('import sys')
        out.append('sys.path.insert(0, "{}")'.format(kr_path))
        out.append('import knowledge_repo')

        out.append(self.builder_str)
        if not isinstance(self.knowledge_builder, str):
            out.append('app = %s()'%self.knowledge_builder.__name__)

        with open(tmp_path, 'w') as f:
            f.write('\n'.join(out))

        return tmp_dir

    def run(self):
        raise NotImplementedError



