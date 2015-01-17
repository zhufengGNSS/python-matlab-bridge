import pymatbridge as pymat
import IPython

import numpy.testing as npt

class TestMagic:

    # Create an IPython shell and load Matlab magic
    @classmethod
    def setup_class(cls):
        cls.ip = IPython.InteractiveShell()
        cls.ip.run_cell('import random')
        cls.ip.run_cell('import numpy as np')
        pymat.load_ipython_extension(cls.ip)

    # Unload the magic, shut down Matlab
    @classmethod
    def teardown_class(cls):
        pymat.unload_ipython_extension(cls.ip)


    # Test single operation on different data structures
    def test_cell_magic_number(self):
        # A double precision real number
        self.ip.run_cell("a = np.float64(random.random())")
        self.ip.run_cell_magic('matlab', '-i a -o b', 'b = a*2;')
        npt.assert_almost_equal(self.ip.user_ns['b'],
                                self.ip.user_ns['a']*2, decimal=7)

    def test_cell_magic_number_complex(self):
        # A complex number
        self.ip.run_cell("x = 3.34+4.56j")
        self.ip.run_cell_magic('matlab', '-i x -o y', 'y = x*(11.35 - 23.098j)')
        self.ip.run_cell("res = x*(11.35 - 23.098j)")
        npt.assert_almost_equal(self.ip.user_ns['y'],
                                self.ip.user_ns['res'], decimal=7)


    def test_cell_magic_array(self):
        # Random array multiplication
        self.ip.run_cell("val1 = np.random.random_sample((3,3))")
        self.ip.run_cell("val2 = np.random.random_sample((3,3))")
        self.ip.run_cell("respy = np.dot(val1, val2)")
        self.ip.run_cell_magic('matlab', '-i val1,val2 -o resmat',
                               'resmat = val1 * val2')
        npt.assert_almost_equal(self.ip.user_ns['resmat'],
                                self.ip.user_ns['respy'], decimal=7)

    def test_cell_magic_array_complex(self):
        self.ip.run_cell("val1 = np.random.random((3,3)) + np.random.random((3,3))*1j")
        self.ip.run_cell("val2 = np.random.random((3,3)) + np.random.random((3,3))*1j")
        self.ip.run_cell("respy = np.dot(val1, val2)")
        self.ip.run_cell_magic('matlab', '-i val1,val2 -o resmat',
                               'resmat = val1 * val2')
        npt.assert_almost_equal(self.ip.user_ns['resmat'],
                                self.ip.user_ns['respy'], decimal=7)

    def test_line_magic(self):
        # Some operation in Matlab
        self.ip.run_line_magic('matlab', 'a = [1 2 3]')
        self.ip.run_line_magic('matlab', 'res = a*2')
        # Get the result back to Python
        self.ip.run_cell_magic('matlab', '-o actual', 'actual = res')

        self.ip.run_cell("expected = np.array([[2., 4., 6.]])")
        npt.assert_almost_equal(self.ip.user_ns['actual'],
                                self.ip.user_ns['expected'], decimal=7)

    def test_figure(self):
        # Just make a plot to get more testing coverage
        self.ip.run_line_magic('matlab', 'plot([1 2 3])')


    def test_matrix(self):
        self.ip.run_cell("in_array = np.array([[1,2,3], [4,5,6]])")
        self.ip.run_cell_magic('matlab', '-i in_array -o out_array',
                               'out_array = in_array;')
        npt.assert_almost_equal(self.ip.user_ns['out_array'],
                                self.ip.user_ns['in_array'],
                                decimal=7)

    # Matlab struct type should be converted to a Python dict
    def test_struct(self):
        self.ip.run_cell('num = 2.567')
        self.ip.run_cell('num_array = np.array([1.2,3.4,5.6]).reshape(3,1)')
        self.ip.run_cell('str = "Hello World"')
        self.ip.run_cell_magic('matlab', '-i num,num_array,str -o obj',
                                'obj.num = num;obj.num_array = num_array;obj.str = str;')
        npt.assert_equal(isinstance(self.ip.user_ns['obj'], dict), True)
        npt.assert_equal(self.ip.user_ns['obj']['num'], self.ip.user_ns['num'])
        npt.assert_equal(self.ip.user_ns['obj']['num_array'], self.ip.user_ns['num_array'])
        npt.assert_equal(self.ip.user_ns['obj']['str'], self.ip.user_ns['str'])
