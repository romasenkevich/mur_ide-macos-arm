from setuptools import setup

setup(name='pymurapi',
      version='0.0.2',
      description='murSimulator/murAUV API for python',
      url='https://github.com/murproject/pymurapi',
      author='MUR Project',
      author_email='support@robocenter.org',
      license='MIT',
      packages=['pymurapi'],
      zip_safe=False, install_requires=['pyzmq', 'numpy'])
