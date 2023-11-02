from setuptools import setup, find_packages

setup(name='ziprepo',
      version='1.0a.dev1',
      description='Sync your data between remote directories',
      long_description="",
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3',
      ],
      keywords='files zip repository',
      url='http://github.com/brookite/ZipRepo',
      author='brookite',
      packages=find_packages(),
      py_modules=['ziprepo'],
      include_package_data=True,
      entry_points={
        'console_scripts': [
            'ziprepo = ziprepo:main'
        ]
      },
      zip_safe=False)