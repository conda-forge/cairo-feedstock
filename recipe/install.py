# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <https://unlicense.org>

"""A python install script for conda-build recipes with multiple outputs

Used in outputs/script to split the files of a top-level package into multiple
outputs instead of using the outputs/files dictionary of globs. The advantage
of this approach is that you don't need to choose glob expressions that include
files installed by this package while excluding files installed by the host
dependencies. For example, this script just globs "include", whereas using
outputs/files, you would need to glob "include/foo.h", "include/foo" and
possibly others in order to exclude the headers from dependencies.

To use this script, set your install prefix in your build script to a new
directory named `$SRC_DIR / stage`. Change `basename` to the basename of the
package. Replace the stage directory with the conda prefix placeholder in any
pkg-config files using sed. i.e.

on unix
sed -i.bak "s,$SRC_DIR/stage,/opt/anaconda1anaconda2anaconda3,g" $SRC_DIR/stage/lib/pkgconfig/*.pc
rm $SRC_DIR/stage/lib/pkgconfig/*.bak

on windows with m2-sed installed
setlocal EnableExtensions ENABLEDELAYEDEXPANSION
for %%f in ( "%SRC_DIR%\stage\lib\pkgconfig\*.pc" ) do (
    sed -i.bak "s,prefix=.*,prefix=/opt/anaconda1anaconda2anaconda3/Library,g" %%f
    del %%f.bak
)
endlocal

https://gist.github.com/carterbox/188ac74647e703cfa6700b58b076d712
"""

import os
import pathlib
import re
import shutil
import typing
import itertools

target_platform = os.environ["target_platform"]
STAGE = pathlib.Path(os.environ["SRC_DIR"]) / "stage"
PREFIX = pathlib.Path(os.environ["PREFIX"])
if target_platform[:3] == "win":
    PREFIX = PREFIX / "Library"


def glob_install(
    include: typing.List[str],
    exclude: typing.List[str] = [],
):
    """Install files and symlinks (broken or not) from the glob expressions."""
    included = set(itertools.chain(*(STAGE.glob(item) for item in include)))
    excluded = set(itertools.chain(*(STAGE.glob(item) for item in exclude)))
    for match in sorted(included - excluded):
        match = pathlib.Path(match)
        if match.is_file() or match.is_symlink():
            relative = match.relative_to(STAGE)
            print(relative)
            os.makedirs((PREFIX / relative).parent, exist_ok=True)
            shutil.copy(
                match,
                PREFIX / relative,
                # copy the link itself; not the linked-file
                follow_symlinks=False,
            )


def sort_artifacts_based_on_name(basename):
    PKG_NAME = os.environ["PKG_NAME"]

    print(f"Installing {PKG_NAME} to {PREFIX} for {target_platform}")
    print("Based on the package name, ", end="")

    if PKG_NAME.endswith("-split"):
        raise ValueError("The top level package should not run this script.")

    # libfoo OR foo-dev OR libfoo-dev
    # dav1d-dev, v8-dev, m-dev, secp256k1-dev
    # libdav1d, libv8, libm, libsecp256k1
    # libdav1d-dev, libv8-dev, libm-dev, libsecp256k1-dev
    if (
        PKG_NAME == basename
    ):
        print("this package is needed for compiling/linking.")
        glob_install(
            include=[
                "bin/**/*",
                "doc/**/*",
                "share/**/*",
                "include/**/*",
                "lib/**/*",
            ],
            exclude=[
                # versioned libs
                "lib/**/lib*.*.dylib",
                "lib/**/lib*.so.*",
                # static libs
                "lib/**/*.a",
                "lib/**/lib*.lib",
                "lib/**/*.a.lib",
                "lib/**/*_a.lib",
                "lib/**/*static.lib",
                "lib/**/*static*",
                "bin/**/*.dll",
            ],
        )
        return

    # libfoo1
    # libdav1d1, libv8-1, libm1, libsecp256k1-1
    if re.match(f"^lib{ basename }-?[0-9]+$", PKG_NAME):
        print("this package is versioned so/dylib, dlls.")
        glob_install(
            include=[
                "bin/**/*.dll",
                "lib/**/lib*.*.dylib",
                "lib/**/lib*.so.*",
            ]
        )
        return

    # libfoo-static
    # libdav1d-static, libv8-static, libm-static, libsecp256k1-static
    if PKG_NAME == f"lib{ basename }-static":
        print("this package is anything needed for static linking.")
        glob_install(
            include=[
                "lib/**/lib*.a",
                "lib/**/lib*.lib",
                "lib/**/*.a.lib",
                "lib/**/*_a.lib",
                "lib/**/*static.lib",
                "lib/**/*static*",
            ]
        )
        # FIXME: Add static library files here; exclude above
        return

    print("this package has unknown purpose!")
    raise ValueError("None of the packages names matched!")


if __name__ == "__main__":
    sort_artifacts_based_on_name(basename="cairo")
