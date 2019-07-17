

class Test1(unittest.TestCase):
    def test1(self):
        src = """
           var s16 A;
        main {
           A = 1;
        }
        """
        code = compile(src)
        vm = Vm()
        vm.run(code)
        self.assertEqual(1, vm.lookup('A'))

