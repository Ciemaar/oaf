from distutils.core import setup

setup(
    name='orbLib',
    version='0.0.1',
    packages=['src.db', 'src.test', 'src.orbLib', 'src.slvend', 'src.desktopSLED'],
    url='https://channel3b.wordpress.com/orbLib',
    license='Pending',
    author='Andy Fundinger',
    author_email='Andy@ciemaar.com',
    description='twisted based monitoring framework.', requires=['sqlalchemy', 'wx', 'PySerial']
)
