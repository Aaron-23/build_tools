#!/usr/bin/env python

import config
import base
import os

# make build.pro
def make():
  is_no_brandind_build = base.is_file("config")

  platforms = config.option("platform").split()
  for platform in platforms:
    if not platform in config.platforms:
      continue

    print("------------------------------------------")
    print("BUILD_PLATFORM: " + platform)
    print("------------------------------------------")
    old_env = os.environ.copy()

    isAndroid = False if (-1 == platform.find("android")) else True
    if isAndroid:
      toolchain_platform = "linux-x86_64"
      if ("mac" == base.host_platform()):
        toolchain_platform = "darwin-x86_64"
      base.set_env("ANDROID_NDK_HOST", toolchain_platform)
      old_path = base.get_env("PATH")
      new_path = base.qt_setup(platform) + "/bin:"
      new_path += (base.get_env("ANDROID_NDK_ROOT") + "/toolchains/llvm/prebuilt/" + toolchain_platform + "/bin:")
      new_path += old_path
      base.set_env("PATH", new_path)
      if ("android_arm64_v8a" == platform):
        base.set_env("ANDROID_NDK_PLATFORM", "android-21")
      else:
        base.set_env("ANDROID_NDK_PLATFORM", "android-16")

    # makefile suffix
    file_suff = platform
    if (config.check_option("config", "debug")):
      file_suff += "_debug_"
    file_suff += config.option("branding")

    # setup qt
    qt_dir = base.qt_setup(platform)
    base.set_env("OS_DEPLOY", platform)

    # qmake CONFIG+=...
    config_param = base.qt_config(platform)

    # qmake ADDON
    qmake_addon = []
    if ("" != config.option("qmake_addon")):
      qmake_addon.append(config.option("qmake_addon"))

    # non windows platform
    if not base.is_windows():
      if ("1" == config.option("clean")):
        base.cmd(base.app_make(), ["clean", "-f", "makefiles/build.makefile_" + file_suff], True)
        base.cmd(base.app_make(), ["distclean", "-f", "makefiles/build.makefile_" + file_suff], True)

      if base.is_file("makefiles/build.makefile_" + file_suff):
        base.delete_file("makefiles/build.makefile_" + file_suff)
      base.cmd(qt_dir + "/bin/qmake", ["-nocache", "build.pro", "CONFIG+=" + config_param] + qmake_addon)    
      base.cmd(base.app_make(), ["-f", "makefiles/build.makefile_" + file_suff])
    else:
      qmake_bat = []
      qmake_bat.append("call \"" + config.option("vs-path") + "/vcvarsall.bat\" " + ("x86" if base.platform_is_32(platform) else "x64"))
      if ("1" == config.option("clean")):
        qmake_bat.append("call nmake clean -f makefiles/build.makefile_" + file_suff)
        qmake_bat.append("call nmake distclean -f makefiles/build.makefile_" + file_suff)
      qmake_addon_string = ""
      if ("" != config.option("qmake_addon")):
        qmake_addon_string = " \"" + config.option("qmake_addon") + "\""
      qmake_bat.append("if exist ./makefiles/build.makefile_" + file_suff + " del /F ./makefiles/build.makefile_" + file_suff)
      qmake_bat.append("call \"" + qt_dir + "/bin/qmake\" -nocache build.pro \"CONFIG+=" + config_param + "\"" + qmake_addon_string)
      qmake_bat.append("call nmake -f makefiles/build.makefile_" + file_suff)
      base.run_as_bat(qmake_bat)
      
    os.environ = old_env.copy()

    base.delete_file(".qmake.stash")

  if config.check_option("module", "builder") and base.is_windows() and is_no_brandind_build:
    base.bash("../core/DesktopEditor/doctrenderer/docbuilder.com/build")

  return
