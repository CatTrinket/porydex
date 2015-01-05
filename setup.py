import setuptools

requires = [
    'SQLAlchemy >=0.9.8, <0.10'
]

entry_points = {
    'console_scripts': 'catdexdb = catdex.db.cli:main'
}

setuptools.setup(
    name='catdex',
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    entry_points=entry_points
)
