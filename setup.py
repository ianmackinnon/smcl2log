# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pathlib import Path

import setuptools

TEST_PATH = Path(__file__).parent.resolve()

exec((TEST_PATH / "smcl2log" / "version.py").read_text())


setuptools.setup(
    name="smcl2log",
    version=__version__,
    author="Ian Mackinnon",
    author_email="imackinnon@gmail.com",
    description="Convert Stata Markup and Control Language (SMCL) files to plain text logs",
    long_description=(TEST_PATH / "README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/ianmackinnon/smcl2log",
    keywords='stata smcl convert log',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[],
    python_requires='>=3',
    scripts=[
        "scripts/smcl2log",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "tox", "coverage", "pytest-cov"],
)
