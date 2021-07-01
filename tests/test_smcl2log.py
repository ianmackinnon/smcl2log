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

import sys
from pathlib import Path

sys.path.append("../")

from smcl2log.smcl2log import smcl2log

from conftest import get_test_case, api_compare, cli_compare



TEST_PATH = Path(__file__).parent.resolve()



def test_api(smcl2log_case_name):
    (smcl_path, log_known_path) = get_test_case(
        "smcl2log", smcl2log_case_name)

    def f(out):
        smcl2log(out, smcl_path)

    api_compare(log_known_path, f)



def test_cli(smcl2log_case_name):
    (smcl_path, log_known_path) = get_test_case(
        "smcl2log", smcl2log_case_name)

    cli_compare(log_known_path, "smcl2log", smcl2log_case_name, [
        "smcl2log",
        smcl_path,
        "__result_path__",
    ])
