from setuptools import setup

setup(name='clplot',
      version='0.1.1',
      description='CASA calculation of closure quantities and plotting',
#      url='http://',
      author='Bojan Nikolic',
      author_email='b.nikolic@mrao.cam.ac.uk',
      license='GPL (same as CASA)',
      packages=['clplot'],
      scripts = ['heraadd.py'],
      zip_safe=False)
