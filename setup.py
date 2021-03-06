from setuptools import setup, find_packages

setup(name='parkinglot',
      version='0.1.0',
      description='Parking Lot: Go Jek Interview',
      url='',
      license='Proprietary',
      author='Vinaya Mandke',
      author_email='vmandke',
      packages=find_packages(),
      include_package_data=True,
      install_requires=['pytest==3.0.7'],
      entry_points={'console_scripts': ['runner = parkinglot.runner:run']})
