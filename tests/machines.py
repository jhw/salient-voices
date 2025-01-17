from sv.machines import SVMachine, SVSamplerMachine

from unittest.mock import MagicMock, patch

import unittest

class MachineTest(unittest.TestCase):

    def setUp(self):
        self.mock_container = MagicMock()
        self.mock_container.n_ticks = 16
        self.namespace = "TestNamespace"
        self.svmachine = SVMachine(container = self.mock_container,
                                   namespace = self.namespace,
                                   colour = [127, 127, 127])
        def mock_generator(machine, rand, n, **env):
            for i in range(n):
                yield [MagicMock()]
        self.mock_generator = mock_generator

    def test_namespace_initialization(self):
        self.assertEqual(self.svmachine.namespace, "Testnamespace")

    def test_render(self):
        self.svmachine.render(generator=self.mock_generator, seeds={"test": 123})
        self.assertTrue(self.mock_container.add_trigs.called)

    @patch("copy.deepcopy")
    def test_modules_property(self, mock_deepcopy):
        self.svmachine.Modules = [{"name": "TestModule", "links": ["Output", "AnotherModule"]}]
        mock_deepcopy.return_value = self.svmachine.Modules
        self.svmachine.defaults = {"TestModule": {"volume": 100}}
        modules = self.svmachine.modules
        self.assertEqual(modules[0]["name"], "TestnamespaceTestModule")
        self.assertEqual(modules[0]["defaults"]["volume"], 100)
        self.assertEqual(modules[0]["links"][1], "TestnamespaceAnotherModule")

class SamplerMachineTest(unittest.TestCase):

    def setUp(self):
        self.mock_container = MagicMock()
        self.mock_container.n_ticks = 16
        self.namespace = "SamplerNamespace"
        self.root = "/sample/path"
        self.svsampler = SVSamplerMachine(
            container = self.mock_container,
            namespace = self.namespace,
            colour = [127, 127, 127],
            root = self.root
        )
        def mock_generator(machine, rand, n, **env):
            for i in range(n):
                yield [MagicMock()]
        self.mock_generator = mock_generator

    def test_root_initialization(self):
        self.assertEqual(self.svsampler.root, self.root)

    @patch("copy.deepcopy")
    def test_modules_property(self, mock_deepcopy):
        self.svsampler.Modules = [{"name": "SamplerModule", "links": ["Output"]}]
        mock_deepcopy.return_value = self.svsampler.Modules
        with patch("sv.machines.SVModule") as MockSVModule:
            MockSVModule.return_value.is_sampler = True
            modules = self.svsampler.modules

        self.assertEqual(modules[0]["root"], self.root)

    def test_render(self):
        self.svsampler.render(generator=self.mock_generator, seeds={"test": 123})
        self.assertTrue(self.mock_container.add_trigs.called)

if __name__ == "__main__":
    unittest.main()
