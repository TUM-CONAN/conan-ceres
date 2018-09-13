from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
from conans.util import files
import os
import shutil

class LibCeresConan(ConanFile):
    name = "ceres"
    version = "1.14.0"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    exports = [
        "patches/CMakeProjectWrapper.txt"
    ]
    url = "https://gitlab.lan.local/conan/conan-ceres"
    license="New BSD license"
    description = "Ceres Solver is an open source C++ library for modeling and solving large, complicated optimization problems."
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    short_paths = False

    def requirements(self):
        self.requires("eigen/3.3.4@fw4spl/stable")
        self.requires("glog/0.3.5-rev-8d7a107@fw4spl/stable")
        self.requires("cxsparse/3.1.1@fw4spl/stable")
    
    def source(self):
        tools.get("http://ceres-solver.org/ceres-solver-{0}.tar.gz".format(self.version))
        os.rename("ceres-solver-" + self.version, self.source_subfolder)

    def build(self):
        cxsparse_source_dir = os.path.join(self.source_folder, self.source_subfolder)
        shutil.move("patches/CMakeProjectWrapper.txt", "CMakeLists.txt")

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
        cmake.configure(build_folder=self.build_subfolder)
        cmake.build()
        cmake.install()
        cmake.patch_config_paths()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
