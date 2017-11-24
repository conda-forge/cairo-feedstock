#!/bin/bash

# As of Mac OS 10.8, X11 is no longer included by default
# (See https://support.apple.com/en-us/HT201341 for the details).
# Due to this change, we disable building X11 support for cairo on OS X by
# default.
export XWIN_ARGS=""
if [ $(uname) == Darwin ]; then
    export XWIN_ARGS="--disable-xlib -disable-xcb --disable-glitz"
fi

# Most other autotools-based build systems add
# prefix/include and prefix/lib automatically!
export CFLAGS=${CFLAGS}" -I${PREFIX}/include"
export CXXFLAGS=${CXXFLAGS}" -I${PREFIX}/include"
export LDFLAGS=${LDFLAGS}" -L${PREFIX}/lib"

./configure \
    --prefix="${PREFIX}" \
    --enable-warnings \
    --enable-ft \
    --enable-ps \
    --enable-pdf \
    --enable-svg \
    --disable-gtk-doc \
    $XWIN_ARGS

make -j${CPU_COUNT}
# FAIL: check-link on OS X
# Hangs for > 10 minutes on Linux
#make check -j${CPU_COUNT}
make install -j${CPU_COUNT}
