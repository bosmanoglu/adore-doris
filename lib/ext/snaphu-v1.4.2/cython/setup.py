from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
    cmdclass = {'build_ext' : build_ext},
    ext_modules=[Extension("_snaphu", 
    sources=["_snaphu.pyx",
        "../src/snaphu.c",
        "../src/snaphu_solver.c",
        "../src/snaphu_util.c",
        "../src/snaphu_cost.c",
        "../src/snaphu_cs2.c",
        "../src/snaphu_io.c",
        "../src/snaphu_tile.c"],
    include_dirs=['../src'],
    extra_compile_args=['-Wstrict-prototypes', ],
    language="c")]
)
