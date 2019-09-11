import os
import shutil

from conans import ConanFile, CMake, tools
from fnmatch import fnmatch


class LibCeresConan(ConanFile):
    name = "ceres"
    upstream_version = "1.14.0"
    package_revision = "-r3"
    version = "{0}{1}".format(upstream_version, package_revision)

    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    exports = [
        "patches/CMakeProjectWrapper.txt",
        "patches/CMakeLists.patch"
    ]
    url = "https://git.ircad.fr/conan/conan-ceres"
    license = "New BSD license"
    description = "Ceres Solver is an open source C++ library for modeling and solving large, complicated optimization problems."
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    short_paths = True

    def configure(self):
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("eigen/3.3.7-r2@sight/testing")
        self.requires("glog/0.4.0-r2@sight/testing")
        self.requires("cxsparse/3.1.1-r3@sight/testing")
        self.requires("common/1.0.1@sight/testing")

    def source(self):
        tools.get("http://ceres-solver.org/ceres-solver-{0}.tar.gz".format(self.upstream_version))
        os.rename("ceres-solver-" + self.upstream_version, self.source_subfolder)

    def build(self):
        # Retrieve common helpers
        import common

        cxsparse_source_dir = os.path.join(self.source_folder, self.source_subfolder)
        shutil.move("patches/CMakeProjectWrapper.txt", "CMakeLists.txt")
        tools.patch(cxsparse_source_dir, "patches/CMakeLists.patch")

        cmake = CMake(self)

        # Set common flags
        cmake.definitions["SIGHT_CMAKE_C_FLAGS"] = common.get_c_flags()
        cmake.definitions["SIGHT_CMAKE_CXX_FLAGS"] = common.get_cxx_flags()

        cmake.definitions["GLOG_PREFER_EXPORTED_GLOG_CMAKE_CONFIGURATION"] = "ON"
        cmake.definitions["LAPACK"] = "OFF"
        cmake.definitions["SUITESPARSE"] = "OFF"
        cmake.definitions["CXSPARSE"] = "ON"
        cmake.definitions["GFLAGS"] = "OFF"
        cmake.definitions["MINIGLOG"] = "OFF"
        cmake.definitions["SCHUR_SPECIALIZATIONS"] = "OFF"
        cmake.definitions["BUILD_DOCUMENTATION"] = "OFF"
        cmake.definitions["BUILD_TESTING"] = "OFF"
        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["CXX11"] = "ON"

        if not tools.os_info.is_windows:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = "ON"

        cmake.configure(build_folder=self.build_subfolder)
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

    def package(self):
        # Retrieve common helpers
        import common

        # Fix all hard coded path to conan package in all .cmake files
        common.fix_conan_path(self, self.package_folder, '*.cmake')
