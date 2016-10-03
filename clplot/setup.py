from setuptools import setup

setup(name='clplot',
      version='0.1',
      description='CASA Calculation of closure quantities and plotting',
#      url='http://github.com/storborg/funniest',
      author='Bojan Nikolic',
      author_email='b.nikolic@mrao.cam.ac.uk',
      license='GPL (Like CASA)',
      packages=['clplot'],
      scripts = ['heraadd.py'],
      zip_safe=False)
