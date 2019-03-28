import os
import shutil

from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
from conans.util import files


class LibCeresConan(ConanFile):
    name = "ceres"
    short_version = "1.14.0"
    version = "{0}-r1".format(short_version)
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
    short_paths = False

    def configure(self):
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("eigen/3.3.7@sight/testing")
        self.requires("glog/0.3.5-rev-8d7a107@sight/stable")
        self.requires("cxsparse/3.1.1@sight/stable")

    def source(self):
        tools.get("http://ceres-solver.org/ceres-solver-{0}.tar.gz".format(self.short_version))
        os.rename("ceres-solver-" + self.short_version, self.source_subfolder)

    def build(self):
        cxsparse_source_dir = os.path.join(self.source_folder, self.source_subfolder)
        shutil.move("patches/CMakeProjectWrapper.txt", "CMakeLists.txt")
        tools.patch(cxsparse_source_dir, "patches/CMakeLists.patch")

        cmake = CMake(self)
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

    def cmake_fix_path(self, file_path, package_name):
        tools.replace_in_file(
            file_path,
            self.deps_cpp_info[package_name].rootpath.replace('\\', '/'),
            "${CONAN_" + package_name.upper() + "_ROOT}"
        )

    def package(self):
        if not tools.os_info.is_windows:
            ceres_config_file = os.path.join(self.package_folder, "lib", "cmake", "Ceres", "CeresConfig.cmake")
            self.cmake_fix_path(ceres_config_file, "glog")
