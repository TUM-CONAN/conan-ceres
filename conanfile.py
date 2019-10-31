import os
from conans import ConanFile, CMake, tools


class LibCeresConan(ConanFile):
    name = "ceres"
    upstream_version = "1.14.0"
    package_revision = "-r4"
    version = "{0}{1}".format(upstream_version, package_revision)

    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    exports = [
        "patches/CMakeLists.patch",
        "patches/c++17.patch"
    ]
    url = "https://git.ircad.fr/conan/conan-ceres"
    license = "New BSD license"
    description = ("Ceres Solver is an open source C++ library for modeling and solving large, "
                   "complicated optimization problems.")
    source_subfolder = "source_subfolder"
    short_paths = True

    def requirements(self):
        self.requires("eigen/3.3.7-r3@sight/testing")
        self.requires("glog/0.4.0-r3@sight/testing")
        self.requires("cxsparse/3.1.1-r4@sight/testing")
        self.requires("common/1.0.2@sight/testing")

    def source(self):
        tools.get("http://ceres-solver.org/ceres-solver-{0}.tar.gz".format(self.upstream_version))
        os.rename("ceres-solver-" + self.upstream_version, self.source_subfolder)

    def build(self):
        cxsparse_source_dir = os.path.join(self.source_folder, self.source_subfolder)
        tools.patch(cxsparse_source_dir, "patches/CMakeLists.patch")
        tools.patch(cxsparse_source_dir, "patches/c++17.patch")

        # Import common flags and defines
        import common

        # Generate Cmake wrapper
        common.generate_cmake_wrapper(
            cmakelists_path='CMakeLists.txt',
            source_subfolder=self.source_subfolder,
            build_type=self.settings.build_type
        )

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

        cmake.configure()
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

    def package(self):
        # Retrieve common helpers
        import common

        # Fix all hard coded path to conan package in all .cmake files
        common.fix_conan_path(self, self.package_folder, '*.cmake')
