#!/bin/bash

# Most other autotools-based build systems add
# prefix/include and prefix/lib automatically!
export CFLAGS=${CFLAGS}" -I${PREFIX}/include"
export CXXFLAGS=${CXXFLAGS}" -I${PREFIX}/include"
export LDFLAGS=${LDFLAGS}" -L${PREFIX}/lib"

# Cf. https://github.com/conda-forge/staged-recipes/issues/673, we're in the
# process of excising Libtool files from our packages. Existing ones can break
# the build while this happens.
find $PREFIX -name '*.la' -delete

./configure \
    --prefix="${PREFIX}" \
    --enable-warnings \
    --enable-ft \
    --enable-ps \
    --enable-pdf \
    --enable-svg \
    --disable-gtk-doc \
    --enable-xcb-shm

make -j${CPU_COUNT}
# FAIL: check-link on OS X
# Hangs for > 10 minutes on Linux
#make check -j${CPU_COUNT}
make install -j${CPU_COUNT}

# Remove any new Libtool files we may have installed. It is intended that
# conda-build will eventually do this automatically.
find $PREFIX -name '*.la' -delete
