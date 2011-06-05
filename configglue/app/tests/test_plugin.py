from unittest import TestCase

from configglue.app.plugin import (
    Plugin,
    PluginManager,
)
from configglue.pyschema import Schema


def make_plugins(available=None, enabled=None):
    plugins = PluginManager()
    if available:
        for plugin in available:
            plugins.register(plugin)
    if enabled is not None:
        for plugin in enabled:
            plugins.enable(plugin)
    return plugins


class Foo(Plugin):
    pass


class PluginTestCase(TestCase):
    def test_defaults(self):
        plugin = Plugin()
        self.assertEqual(plugin.schema, Schema)
        self.assertEqual(plugin.enabled, False)


class PluginManagerTestCase(TestCase):
    def test_constructor(self):
        plugins = make_plugins()
        self.assertEqual(plugins.available, set([]))

    def test_enabled(self):
        plugins = make_plugins(available=[Foo], enabled=[Foo])
        self.assertEqual(plugins.enabled, set([Foo]))

    def test_enable(self):
        plugins = make_plugins(available=[Foo])
        self.assertEqual(Foo.enabled, False)
        self.assertTrue(Foo in plugins.available)
        self.assertFalse(Foo in plugins.enabled)

        plugins.enable(Foo)
        self.assertEqual(Foo.enabled, True)
        self.assertTrue(Foo in plugins.enabled)

    def test_disable(self):
        plugins = make_plugins(available=[Foo], enabled=[Foo])
        self.assertEqual(Foo.enabled, True)
        self.assertTrue(Foo in plugins.enabled)
        self.assertTrue(Foo in plugins.enabled)

        plugins.disable(Foo)

        self.assertEqual(Foo.enabled, False)
        self.assertFalse(Foo in plugins.enabled)

    def test_schemas(self):
        class Bar(Plugin):
            pass
        plugins = make_plugins(available=[Foo, Bar], enabled=[Foo])
        self.assertEqual(plugins.schemas, [Foo.schema])

    def test_load(self):
        plugins = make_plugins()
        self.assertEqual(plugins.load(), set([]))

    def test_register(self):
        plugins = PluginManager()
        self.assertEqual(plugins.available, set([]))

        plugins.register(Foo)
        self.assertEqual(plugins.available, set([Foo]))
