@ECHO ON

mkdir "%SRC_DIR%\stage"

set "PKG_CONFIG_PATH=%LIBRARY_LIB%\pkgconfig;%LIBRARY_PREFIX%\share\pkgconfig;%BUILD_PREFIX%\Library\lib\pkgconfig"

:: get the prefix in "mixed" form
set "LIBRARY_PREFIX_M=%SRC_DIR\stage:\=/%"

%BUILD_PREFIX%\Scripts\meson setup builddir ^
  --buildtype=release ^
  --default-library=both ^
  --prefix=%LIBRARY_PREFIX_M% ^
  --wrap-mode=nofallback ^
  --backend=ninja ^
  -Dfontconfig=enabled ^
  -Dfreetype=enabled ^
  -Dglib=enabled
if errorlevel 1 exit 1

ninja -v -C builddir -j %CPU_COUNT%
if errorlevel 1 exit 1

ninja -C builddir install -j %CPU_COUNT%
if errorlevel 1 exit 1

setlocal EnableExtensions EnableDelayedExpansion
for %%f in ( "%SRC_DIR%\stage\lib\pkgconfig\*.pc" ) do (
    sed -i.bak "s,prefix=.*,prefix=/opt/anaconda1anaconda2anaconda3/Library,g" %%f
    del %%f.bak
)
endlocal
sed -i.bak "s,prefix=.*,prefix=/opt/anaconda1anaconda2anaconda3/Library,g" %SRC_DIR%\stage\bin\cairo-trace
del %SRC_DIR%\stage\bin\cairo-trace.bak
