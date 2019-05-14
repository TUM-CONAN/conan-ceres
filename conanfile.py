import os
import shutil

from conans import ConanFile, CMake, tools
from fnmatch import fnmatch


class LibCeresConan(ConanFile):
    name = "ceres"
    upstream_version = "1.14.0"
    package_revision = "-r1"
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
    short_paths = False

    def configure(self):
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("eigen/3.3.7@sight/stable")
        self.requires("glog/0.4.0@sight/stable")
        self.requires("cxsparse/3.1.1-r1@sight/stable")

    def source(self):
        tools.get("http://ceres-solver.org/ceres-solver-{0}.tar.gz".format(self.upstream_version))
        os.rename("ceres-solver-" + self.upstream_version, self.source_subfolder)

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
        try:
            tools.replace_in_file(
                file_path,
                self.deps_cpp_info[package_name].rootpath.replace('\\', '/'),
                "${CONAN_" + package_name.upper() + "_ROOT}",
                strict=False
            )
        except:
            self.output.info("Ignoring {0}...".format(package_name))

    def package(self):
        for path, subdirs, names in os.walk(self.package_folder):
            for name in names:
                if fnmatch(name, '*.cmake'):
                    cmake_file = os.path.join(path, name)
                    
                    tools.replace_in_file(
                        cmake_file, 
                        self.package_folder.replace('\\', '/'), 
                        '${CONAN_CERES_ROOT}', 
                        strict=False
                    )
                    
                    self.cmake_fix_path(cmake_file, "glog")
                    self.cmake_fix_path(cmake_file, "cxsparse")
                    self.cmake_fix_path(cmake_file, "eigen")