from setuptools import setup, find_packages


setup(name='pd',
      version='1.0.0',
      install_requires=['Pillow>=8.0.0', 'aggdraw>=1.3.16'],
      python_requires='>=3.11.5',
      description='Object oriented drawing library',
      url='https://github.com/setanarut/pd',
      author='setanarut',
      license='MIT',
      packages=find_packages(),
          classifiers=[
          'Programming Language :: Python :: 3.11.5',],
      zip_safe=False)
