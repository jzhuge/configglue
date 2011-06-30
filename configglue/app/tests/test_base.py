import os
import user
from unittest import TestCase

from mock import (
    Mock,
    patch,
)

from configglue.app.base import (
    App,
    Config,
)
from configglue.app.plugin import (
    Plugin,
    PluginManager,
)
from configglue.pyschema import (
    IntOption,
    Schema,
)


def make_app(name=None, schema=None, plugin_manager=None):
    # patch sys.argv so that nose can be run with extra options
    # without conflicting with the schema validation
    # patch sys.stderr to prevent spurious output
    mock_sys = Mock()
    mock_sys.argv = ['foo.py']
    with patch('configglue.pyschema.glue.sys', mock_sys):
        with patch('configglue.app.base.sys.stderr'):
            app = App(name=name, schema=schema, plugin_manager=plugin_manager)
    return app


def make_config(app=None):
    if app is None:
        app = make_app()
    # patch sys.argv so that nose can be run with extra options
    # without conflicting with the schema validation
    mock_sys = Mock()
    mock_sys.argv = ['foo.py']
    with patch('configglue.pyschema.glue.sys', mock_sys):
        config = Config(app)
    return config


class ConfigTestCase(TestCase):
    def get_xdg_config_dirs(self):
        xdg_config_home = os.environ.get('XDG_CONFIG_HOME',
            os.path.join(user.home, '.config'))
        xdg_config_dirs = ([xdg_config_home] + 
            os.environ.get('XDG_CONFIG_DIRS', '/etc/xdg').split(':'))
        return xdg_config_dirs

    @patch('configglue.app.base.merge')
    @patch('configglue.app.base.Config.get_config_files')
    @patch('configglue.app.base.configglue')
    def test_constructor(self, mock_configglue,
        mock_get_config_files, mock_merge):

        config = Config(App())

        self.assertEqual(config.schema, mock_merge.return_value)
        self.assertEqual(config.glue, mock_configglue.return_value)
        mock_configglue.assert_called_with(
            mock_merge.return_value, mock_get_config_files.return_value)

    def test_glue_valid_config(self):
        config = make_config()
        self.assertEqual(config.glue.schema_parser.is_valid(), True)

    def test_glue_invalid_config(self):
        class MySchema(Schema):
            foo = IntOption(fatal=True)
        self.assertRaises(SystemExit, make_app, schema=MySchema)

    def test_get_config_files(self):
        app = make_app()
        config = make_config(app=app)
        self.assertEqual(config.get_config_files(app), [])

    @patch('xdg.BaseDirectory.os.path.exists')
    def test_get_config_files_full_hierarchy(self, mock_path_exists):
        mock_path_exists.return_value = True

        config_files = []
        for path in reversed(self.get_xdg_config_dirs()):
            config_files.append(os.path.join(path, 'myapp', 'myapp.cfg'))
        config_files.append('./local.cfg')

        app = make_app(name='myapp')
        config = make_config(app=app)
        self.assertEqual(config.get_config_files(app=app), config_files)

    @patch('xdg.BaseDirectory.os.path.exists')
    def test_get_config_files_with_plugins_full_hierarchy(self,
        mock_path_exists):
        mock_path_exists.return_value = True

        class Foo(Plugin):
            enabled = True

        config_files = []
        for path in reversed(self.get_xdg_config_dirs()):
            config_files.append(os.path.join(path, 'myapp', 'myapp.cfg'))
            config_files.append(os.path.join(path, 'myapp', 'foo.cfg'))
        config_files.append('./local.cfg')

        app = make_app(name='myapp')
        app.plugins.register(Foo)
        config = make_config(app=app)
        self.assertEqual(config.get_config_files(app=app), config_files)


class AppTestCase(TestCase):
    def test_custom_name(self):
        app = make_app(name='myapp')
        self.assertEqual(app.name, 'myapp')

    @patch('configglue.app.base.sys')
    def test_default_name(self, mock_sys):
        mock_sys.argv = ['foo.py']
        app = make_app()
        self.assertEqual(app.name, 'foo')

    def test_default_plugin_manager(self):
        app = make_app()
        self.assertEqual(type(app.plugins), PluginManager)

    def test_custom_plugin_manager(self):
        mock_plugin_manager = Mock()
        mock_plugin_manager.schemas = []
        app = make_app(plugin_manager=mock_plugin_manager)
        self.assertEqual(app.plugins, mock_plugin_manager)

    @patch('configglue.app.base.Config')
    def test_config(self, mock_config):
        app = make_app()
        self.assertEqual(app.config, mock_config.return_value)
