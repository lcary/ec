import unittest


class TestLogoMain(unittest.TestCase):

    def test_imports(self):
        try:
            from eclib.domains.logo.main import (
                animateSolutions,
                dreamFromGrammar,
                list_options,
                outputDreams,
                enumerateDreams,
                visualizePrimitives,
                Flatten,
                LogoFeatureCNN,
                main
            )
        except Exception:
            self.fail('Unable to import logo module')


if __name__ == '__main__':
    unittest.main()
