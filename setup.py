import setuptools

requires = [
    'SQLAlchemy >=0.9.8, <0.10'
]

entry_points = {
    'console_scripts': 'porydex = porydex.db.cli:main'
}

setuptools.setup(
    name='porydex',
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points=entry_points
)
