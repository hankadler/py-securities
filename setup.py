from distutils.core import setup


setup(
    name='securities',
    version='0.1.0',
    description='Library for analyzing securities',
    author='Hank Adler',
    packages=[
        'collector',
        'gui',
        'indicators',
        'plots',
        'screens',
        'statistics',
        'stocks',
        'utils'
    ],
)
