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

import re
import os
import shutil
import logging
from io import StringIO
from typing import Union
from pathlib import Path
from tempfile import NamedTemporaryFile
from contextlib import contextmanager


LOG = logging.getLogger("smcl2log")



# Logging



def color_log(log):
    color_red = '\033[91m'
    color_green = '\033[92m'
    color_yellow = '\033[93m'
    color_blue = '\033[94m'
    color_end = '\033[0m'

    level_colors = (
        ("error", color_red),
        ("warning", color_yellow),
        ("info", color_green),
        ("debug", color_blue),
    )

    safe = None
    color = None

    def xor(a, b):
        return bool(a) ^ bool(b)

    def _format(value):
        if isinstance(value, float):
            return "%0.3f"
        return "%s"

    def message_args(args):
        if not args:
            return "", []
        if (
                not isinstance(args[0], str) or
                xor(len(args) > 1, "%" in args[0])
        ):
            return " ".join([_format(v) for v in args]), args
        return args[0], args[1:]

    def _message(args, color):
        message, args = message_args(args)
        return "".join([color, message, color_end])

    def _args(args):
        args = message_args(args)[1]
        return args

    def build_lambda(safe, color):
        return lambda *args, **kwargs: getattr(log, safe)(
            _message(args, color), *_args(args), **kwargs)

    for (level, color) in level_colors:
        safe = "%s_" % level
        setattr(log, safe, getattr(log, level))
        setattr(log, level, build_lambda(safe, color))



def init_logs(*logs, args=None):
    offset = args.verbose - args.quiet if args else 0
    level = (
        logging.FATAL,
        logging.ERROR,
        logging.WARNING,
        logging.INFO,
        logging.DEBUG
    )[max(0, min(4, 2 + offset))]

    for log in logs:
        if not isinstance(log, logging.Logger):
            log = logging.getLogger(log)
        log.addHandler(logging.StreamHandler())
        log.setLevel(level)
        color_log(log)



@contextmanager
def AtomicOutputFile(path: Union[Path, str], **kwargs):
    """
    Like a temporary file, but move to a desired permanent path
    if closed successful. Also create intermediate folders if necessary.
    """
    # pylint: disable=invalid-name
    # -   Matching capitalized `NamedTemporaryFile` `contextmanager` function

    path = Path(path)
    kwargs = {
        **kwargs,
        **{
            "delete": False,
        }
    }

    with NamedTemporaryFile("w", **kwargs) as temp:
        LOG.debug(
            "Opened temporary file `%s` for writing.",
            Path(temp.name).absolute())

        yield temp

        os.makedirs(path.parent, exist_ok=True)
        shutil.move(temp.name, path)
        LOG.info("Wrote `%s`", path.absolute())


def split_parts(s):
    out = []
    count = 0
    sub = ""
    for part in re.split(r"([{}])", s):
        if part == "{":
            count += 1
            sub += part
        elif part == "}":
            sub += part
            count -= 1
            if count == 0:
                out.append(sub)
                sub = ""
        else:
            if count == 0:
                out.append(part)
            else:
                sub += part

    return out



def smcl2log(out, smcl_path):
    LOG.info(smcl_path.name)

    if not isinstance(smcl_path, Path):
        smcl_path = Path(smcl_path)

    def parse(out, chunk, cmd=0, mode=None, line=None, col=0):
        for part in split_parts(chunk):
            if part.startswith("{"):
                cmd_parts = re.split(r"\s+", part[1:-1])

                if cmd_parts[0] == "smcl":
                    mode = "init"
                    assert len(cmd_parts) == 1
                    continue

                if cmd_parts[0] == ".-":
                    mode = None
                    assert len(cmd_parts) == 1
                    continue

                if cmd_parts[0] in ("txt", "res", ):
                    assert len(cmd_parts) == 1
                    mode = cmd_parts[0]
                    continue

                if cmd_parts[0] in ("bf", "sf", "err", "p_end"):
                    assert len(cmd_parts) == 1
                    continue

                if cmd_parts[0] in ("p"):
                    assert len(cmd_parts) == 3
                    continue

                if cmd_parts[0] in ("search"):
                    continue

                if cmd_parts[0] == "ul":
                    assert cmd_parts == ["ul", "off"]
                    continue

                if re.match(r"(res|bf|text)", cmd_parts[0]):
                    text = part[1:-1].split(":", 1)[1]
                    out.write(text)
                    col += len(text)
                    continue

                if cmd_parts[0] == "ralign":
                    count, code = re.match(r"\{ralign (\d+):(.*)\}", part).groups()
                    count = int(count)
                    out_ = StringIO()
                    (cmd_, mode_, line_, col_, ) = parse(out_, code)
                    value = ("%%%ds" % count) % out_.getvalue()
                    out.write(value)
                    col += len(value)
                    continue

                if cmd_parts[0] in ("help"):
                    null, code = re.match(r"\{help (.*):(.*)\}", part).groups()
                    out_ = StringIO()
                    (cmd_, mode_, line_, col_, ) = parse(out_, code)
                    value = out_.getvalue()
                    out.write(value)
                    col += len(value)
                    continue

                if cmd_parts[0] == "col":
                    assert len(cmd_parts) == 2
                    target = int(cmd_parts[1])
                    lack = max(0, target - col)
                    out.write(" " * lack)
                    col += lack
                    continue

                if cmd_parts[0] == "space":
                    assert len(cmd_parts) == 2
                    count = int(cmd_parts[1])
                    out.write(" " * count)
                    col += count
                    continue

                if cmd_parts[0] == "hline":
                    assert len(cmd_parts) == 2
                    count = int(cmd_parts[1])
                    out.write("-" * count)
                    # out.write(repr(count))
                    col += count
                    continue

                if cmd_parts[0] == "c":
                    assert len(cmd_parts) == 2
                    lookup = {
                        "|": "|",
                        "+": "+",
                        "TT": "+",
                        "BT": "+",
                    }
                    value = lookup[cmd_parts[1]]
                    out.write(value)
                    col += len(value)
                    continue

                if cmd_parts[0] == "com":
                    assert len(cmd_parts) == 1
                    if mode == "init":
                        continue
                    mode = cmd_parts[0]
                    cmd += 1
                    msg = "%d " % cmd
                    out.write(msg)
                    col += len(msg)
                    continue

                LOG.warning("Ignoring unrecognised token: %s", repr(part))

            else:
                if mode == "init":
                    continue

                msg = part
                if "\n" in part:
                    col = len(part.split("\n")[-1])
                else:
                    col += len(part)
                out.write(part)

        return (cmd, mode, line, col)


    cmd = 0
    mode = None
    line = None
    col = 0

    out.write("")
    with smcl_path.open() as fp:
        for i, line in enumerate(fp.readlines()):
            (cmd, mode, line, col) = parse(out, line, cmd, mode, line, col)
