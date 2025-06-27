from setuptools import setup, find_packages

setup(
    name='raster_to_svg',
    version='0.1.0',
    description='Batch convert PNGs to SVGs using alpha channel and Potrace',
    author='Your Name',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'raster-to-svg = raster_to_svg.__main__:main',
        ],
    },
    python_requires='>=3.6',
    install_requires=[],
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
) 