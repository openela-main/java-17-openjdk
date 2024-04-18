# debug_package %%{nil} is portable-jdks specific
%define  debug_package %{nil}

# RPM conditionals so as to be able to dynamically produce
# slowdebug/release builds. See:
# http://rpm.org/user_doc/conditional_builds.html
#
# Examples:
#
# Produce release, fastdebug *and* slowdebug builds on x86_64 (default):
# $ rpmbuild -ba java-*-openjdk.spec
#
# Produce only release builds (no debug builds) on x86_64:
# $ rpmbuild -ba java-*-openjdk.spec --without slowdebug --without fastdebug
#
# Only produce a release build on x86_64:
# $ fedpkg mockbuild --without slowdebug --without fastdebug
# Enable fastdebug builds by default on relevant arches.
%bcond_without fastdebug
# Enable slowdebug builds by default on relevant arches.
%bcond_without slowdebug
# Enable release builds by default on relevant arches.
%bcond_without release
# Enable static library builds by default.
%bcond_without staticlibs
# Build a fresh libjvm.so for use in a copy of the bootstrap JDK
%bcond_without fresh_libjvm
# Build with system libraries
%bcond_with system_libs

# Workaround for stripping of debug symbols from static libraries
%if %{with staticlibs}
%define __brp_strip_static_archive %{nil}
%global include_staticlibs 1
%else
%global include_staticlibs 0
%endif

%if %{with system_libs}
%global system_libs 1
%global link_type system
%global freetype_lib %{nil}
%else
%global system_libs 0
%global link_type bundled
%global freetype_lib |libfreetype[.]so.*
%endif

# The -g flag says to use strip -g instead of full strip on DSOs or EXEs.
# This fixes detailed NMT and other tools which need minimal debug info.
# See: https://bugzilla.redhat.com/show_bug.cgi?id=1520879
%global _find_debuginfo_opts -g

# note: parametrized macros are order-sensitive (unlike not-parametrized) even with normal macros
# also necessary when passing it as parameter to other macros. If not macro, then it is considered a switch
# see the difference between global and define:
# See https://github.com/rpm-software-management/rpm/issues/127 to comments at  "pmatilai commented on Aug 18, 2017"
# (initiated in https://bugzilla.redhat.com/show_bug.cgi?id=1482192)
%global debug_suffix_unquoted -slowdebug
%global fastdebug_suffix_unquoted -fastdebug
%global main_suffix_unquoted -main
%global staticlibs_suffix_unquoted -staticlibs
# quoted one for shell operations
%global debug_suffix "%{debug_suffix_unquoted}"
%global fastdebug_suffix "%{fastdebug_suffix_unquoted}"
%global normal_suffix ""
%global main_suffix "%{main_suffix_unquoted}"
%global staticlibs_suffix "%{staticlibs_suffix_unquoted}"

%global debug_warning This package is unoptimised with full debugging. Install only as needed and remove ASAP.
%global fastdebug_warning This package is optimised with full debugging. Install only as needed and remove ASAP.
%global debug_on unoptimised with full debugging on
%global fastdebug_on optimised with full debugging on
%global for_fastdebug for packages with debugging on and optimisation
%global for_debug for packages with debugging on and no optimisation

%if %{with release}
%global include_normal_build 1
%else
%global include_normal_build 0
%endif

%if %{include_normal_build}
%global normal_build %{normal_suffix}
%else
%global normal_build %{nil}
%endif

# We have hardcoded list of files, which  is appearing in alternatives, and in files
# in alternatives those are slaves and master, very often triplicated by man pages
# in files all masters and slaves are ghosted
# the ghosts are here to allow installation via query like `dnf install /usr/bin/java`
# you can list those files, with appropriate sections: cat *.spec | grep -e --install -e --slave -e post_
# TODO - fix those hardcoded lists via single list
# Those files must *NOT* be ghosted for *slowdebug* packages
# FIXME - if you are moving jshell or jlink or similar, always modify all three sections
# you can check via headless and devels:
#    rpm -ql --noghost java-11-openjdk-headless-11.0.1.13-8.fc29.x86_64.rpm  | grep bin
# == rpm -ql           java-11-openjdk-headless-slowdebug-11.0.1.13-8.fc29.x86_64.rpm  | grep bin
# != rpm -ql           java-11-openjdk-headless-11.0.1.13-8.fc29.x86_64.rpm  | grep bin
# similarly for other %%{_jvmdir}/{jre,java} and %%{_javadocdir}/{java,java-zip}
%define is_release_build() %( if [ "%{?1}" == "%{debug_suffix_unquoted}" -o "%{?1}" == "%{fastdebug_suffix_unquoted}" ]; then echo "0" ; else echo "1"; fi )

# while JDK is a techpreview(is_system_jdk=0), some provides are turned off. Once jdk stops to be an techpreview, move it to 1
# as sytem JDK, we mean any JDK which can run whole system java stack without issues (like bytecode issues, module issues, dependencies...)
%global is_system_jdk 0

%global aarch64         aarch64 arm64 armv8
# we need to distinguish between big and little endian PPC64
%global ppc64le         ppc64le
%global ppc64be         ppc64 ppc64p7
# Set of architectures which support multiple ABIs
%global multilib_arches %{power64} sparc64 x86_64
# Set of architectures for which we build slowdebug builds
%global debug_arches    %{ix86} x86_64 sparcv9 sparc64 %{aarch64} %{power64} s390x
# Set of architectures for which we build fastdebug builds
%global fastdebug_arches x86_64 ppc64le aarch64
# Set of architectures with a Just-In-Time (JIT) compiler
%global jit_arches      %{arm} %{aarch64} %{ix86} %{power64} s390x sparcv9 sparc64 x86_64
# Set of architectures which use the Zero assembler port (!jit_arches)
%global zero_arches ppc s390
# Set of architectures which run a full bootstrap cycle
%global bootstrap_arches %{jit_arches}
# Set of architectures which support SystemTap tapsets
%global systemtap_arches %{jit_arches}
# Set of architectures with a Ahead-Of-Time (AOT) compiler
%global aot_arches      x86_64 %{aarch64}
# Set of architectures which support the serviceability agent
%global sa_arches       %{ix86} x86_64 sparcv9 sparc64 %{aarch64} %{power64} %{arm}
# Set of architectures which support class data sharing
# As of JDK-8005165 in OpenJDK 10, class sharing is not arch-specific
# However, it does segfault on the Zero assembler port, so currently JIT only
%global share_arches    %{jit_arches}
# Set of architectures for which we build the Shenandoah garbage collector
%global shenandoah_arches x86_64 %{aarch64}
# Set of architectures for which we build the Z garbage collector
%global zgc_arches x86_64
# Set of architectures for which alt-java has SSB mitigation
%global ssbd_arches x86_64
# Set of architectures for which java has short vector math library (libjsvml.so)
%global svml_arches x86_64
# Set of architectures where we verify backtraces with gdb
# s390x fails on RHEL 7 so we exclude it there
%if (0%{?rhel} > 0 && 0%{?rhel} < 8)
%global gdb_arches %{arm} %{aarch64} %{ix86} %{power64} sparcv9 sparc64 x86_64 %{zero_arches}
%else
%global gdb_arches %{jit_arches} %{zero_arches}
%endif

# By default, we build a slowdebug build during main build on JIT architectures
%if %{with slowdebug}
%ifarch %{debug_arches}
%global include_debug_build 1
%else
%global include_debug_build 0
%endif
%else
%global include_debug_build 0
%endif

# On certain architectures, we compile the Shenandoah GC
%ifarch %{shenandoah_arches}
%global use_shenandoah_hotspot 1
%else
%global use_shenandoah_hotspot 0
%endif

# By default, we build a fastdebug build during main build only on fastdebug architectures
%if %{with fastdebug}
%ifarch %{fastdebug_arches}
%global include_fastdebug_build 1
%else
%global include_fastdebug_build 0
%endif
%else
%global include_fastdebug_build 0
%endif

%if %{include_debug_build}
%global slowdebug_build %{debug_suffix}
%else
%global slowdebug_build %{nil}
%endif

%if %{include_fastdebug_build}
%global fastdebug_build %{fastdebug_suffix}
%else
%global fastdebug_build %{nil}
%endif

# If you disable all builds, then the build fails
# Build and test slowdebug first as it provides the best diagnostics
%global build_loop %{slowdebug_build} %{fastdebug_build} %{normal_build}

%if %{include_staticlibs}
%global staticlibs_loop %{staticlibs_suffix}
%else
%global staticlibs_loop %{nil}
%endif

%ifarch %{bootstrap_arches}
%global bootstrap_build true
%else
%global bootstrap_build false
%endif

%if %{include_staticlibs}
# Extra target for producing the static-libraries. Separate from
# other targets since this target is configured to use in-tree
# AWT dependencies: lcms, libjpeg, libpng, libharfbuzz, giflib
# and possibly others
%global static_libs_target static-libs-image
%else
%global static_libs_target %{nil}
%endif

# The static libraries are produced under the same configuration as the main
# build for portables, as we expect in-tree libraries to be used throughout.
# If system libraries are enabled, the static libraries will also use them
# which may cause issues.
%global bootstrap_targets images %{static_libs_target} legacy-jre-image
%global release_targets images docs-zip %{static_libs_target} legacy-jre-image
# No docs nor bootcycle for debug builds
%global debug_targets images %{static_libs_target} legacy-jre-image
# Target to use to just build HotSpot
%global hotspot_target hotspot

# Disable LTO as this causes build failures at the moment.
# See RHBZ#1861401
%define _lto_cflags %{nil}

# Filter out flags from the optflags macro that cause problems with the OpenJDK build
# We filter out -O flags so that the optimization of HotSpot is not lowered from O3 to O2
# We filter out -Wall which will otherwise cause HotSpot to produce hundreds of thousands of warnings (100+mb logs)
# We replace it with -Wformat (required by -Werror=format-security) and -Wno-cpp to avoid FORTIFY_SOURCE warnings
# We filter out -fexceptions as the HotSpot build explicitly does -fno-exceptions and it's otherwise the default for C++
%global ourflags %(echo %optflags | sed -e 's|-Wall|-Wformat -Wno-cpp|' | sed -r -e 's|-O[0-9]*||')
%global ourcppflags %(echo %ourflags | sed -e 's|-fexceptions||')
%global ourldflags %{__global_ldflags}

# With disabled nss is NSS deactivated, so NSS_LIBDIR can contain the wrong path
# the initialization must be here. Later the pkg-config have buggy behavior
# looks like openjdk RPM specific bug
# Always set this so the nss.cfg file is not broken
%global NSS_LIBDIR %(pkg-config --variable=libdir nss)

# In some cases, the arch used by the JDK does
# not match _arch.
# Also, in some cases, the machine name used by SystemTap
# does not match that given by _target_cpu
%ifarch x86_64
%global archinstall amd64
%global stapinstall x86_64
%endif
%ifarch ppc
%global archinstall ppc
%global stapinstall powerpc
%endif
%ifarch %{ppc64be}
%global archinstall ppc64
%global stapinstall powerpc
%endif
%ifarch %{ppc64le}
%global archinstall ppc64le
%global stapinstall powerpc
%endif
%ifarch %{ix86}
%global archinstall i686
%global stapinstall i386
%endif
%ifarch ia64
%global archinstall ia64
%global stapinstall ia64
%endif
%ifarch s390
%global archinstall s390
%global stapinstall s390
%endif
%ifarch s390x
%global archinstall s390x
%global stapinstall s390
%endif
%ifarch %{arm}
%global archinstall arm
%global stapinstall arm
%endif
%ifarch %{aarch64}
%global archinstall aarch64
%global stapinstall arm64
%endif
# 32 bit sparc, optimized for v9
%ifarch sparcv9
%global archinstall sparc
%global stapinstall %{_target_cpu}
%endif
# 64 bit sparc
%ifarch sparc64
%global archinstall sparcv9
%global stapinstall %{_target_cpu}
%endif
# Need to support noarch for srpm build
%ifarch noarch
%global archinstall %{nil}
%global stapinstall %{nil}
%endif

%ifarch %{systemtap_arches}
%global with_systemtap 1
%else
%global with_systemtap 0
%endif

# New Version-String scheme-style defines
%global featurever 17
%global interimver 0
%global updatever 11
%global patchver 0
# buildjdkver is usually same as %%{featurever},
# but in time of bootstrap of next jdk, it is featurever-1,
# and this it is better to change it here, on single place
%global buildjdkver %{featurever}
# We don't add any LTS designator for STS packages (Fedora and EPEL).
# We need to explicitly exclude EPEL as it would have the %%{rhel} macro defined.
%if 0%{?rhel} && !0%{?epel}
  %global lts_designator "LTS"
  %global lts_designator_zip -%{lts_designator}
%else
  %global lts_designator ""
  %global lts_designator_zip ""
%endif
# JDK to use for bootstrapping
%global bootjdk /usr/lib/jvm/java-%{buildjdkver}-openjdk
# Define whether to use the bootstrap JDK directly or with a fresh libjvm.so
# This will only work where the bootstrap JDK is the same major version
# as the JDK being built
%if %{with fresh_libjvm} && %{buildjdkver} == %{featurever}
%global build_hotspot_first 1
%else
%global build_hotspot_first 0
%endif

# Define vendor information used by OpenJDK
%global oj_vendor Red Hat, Inc.
%global oj_vendor_url https://www.redhat.com/
# Define what url should JVM offer in case of a crash report
# order may be important, epel may have rhel declared
%if 0%{?epel}
%global oj_vendor_bug_url  https://bugzilla.redhat.com/enter_bug.cgi?product=Fedora%20EPEL&component=%{name}&version=epel%{epel}
%else
%if 0%{?fedora}
# Does not work for rawhide, keeps the version field empty
%global oj_vendor_bug_url  https://bugzilla.redhat.com/enter_bug.cgi?product=Fedora&component=%{name}&version=%{fedora}
%else
%if 0%{?rhel}
%global oj_vendor_bug_url https://access.redhat.com/support/cases/
%else
%global oj_vendor_bug_url  https://bugzilla.redhat.com/enter_bug.cgi
%endif
%endif
%endif
%global oj_vendor_version (Red_Hat-%{version}-%{rpmrelease})

# Define IcedTea version used for SystemTap tapsets and desktop file
%global icedteaver      6.0.0pre00-c848b93a8598
# Define current Git revision for the FIPS support patches
%global fipsver d63771ea660
# Define JDK versions
%global newjavaver %{featurever}.%{interimver}.%{updatever}.%{patchver}
%global javaver         %{featurever}
# Strip up to 6 trailing zeros in newjavaver, as the JDK does, to get the correct version used in filenames
%global filever %(svn=%{newjavaver}; for i in 1 2 3 4 5 6 ; do svn=${svn%%.0} ; done; echo ${svn})
# The tag used to create the OpenJDK tarball
%global vcstag jdk-%{filever}+%{buildver}%{?tagsuffix:-%{tagsuffix}}

# Standard JPackage naming and versioning defines
%global origin          openjdk
%global origin_nice     OpenJDK
%global top_level_dir_name   %{vcstag}
%global top_level_dir_name_backup %{top_level_dir_name}-backup
%global buildver        9
%global rpmrelease      3
#%%global tagsuffix     %%{nil}
# Priority must be 8 digits in total; up to openjdk 1.8, we were using 18..... so when we moved to 11, we had to add another digit
%if %is_system_jdk
# Using 10 digits may overflow the int used for priority, so we combine the patch and build versions
# It is very unlikely we will ever have a patch version > 4 or a build version > 20, so we combine as (patch * 20) + build.
# This means 11.0.9.0+11 would have had a priority of 11000911 as before
# A 11.0.9.1+1 would have had a priority of 11000921 (20 * 1 + 1), thus ensuring it is bigger than 11.0.9.0+11
%global combiver $( expr 20 '*' %{patchver} + %{buildver} )
%global priority %( printf '%02d%02d%02d%02d' %{featurever} %{interimver} %{updatever} %{combiver} )
%else
# for techpreview, using 1, so slowdebugs can have 0
%global priority %( printf '%08d' 1 )
%endif

# Define milestone (EA for pre-releases, GA for releases)
# Release will be (where N is usually a number starting at 1):
# - 0.N%%{?extraver}%%{?dist} for EA releases,
# - N%%{?extraver}{?dist} for GA releases
%global is_ga           1
%if %{is_ga}
%global build_type GA
%global ea_designator ""
%global ea_designator_zip %{nil}
%global extraver %{nil}
%global eaprefix %{nil}
%else
%global build_type EA
%global ea_designator ea
%global ea_designator_zip -%{ea_designator}
%global extraver .%{ea_designator}
%global eaprefix 0.
%endif

# parametrized macros are order-sensitive
%global compatiblename  java-%{featurever}-%{origin}
%global fullversion     %{compatiblename}-%{version}-%{release}
# images directories from upstream build
%global jdkimage                jdk
%global static_libs_image       static-libs
# output dir stub
%define buildoutputdir() %{expand:build/jdk%{featurever}.build%{?1}}
%define installoutputdir() %{expand:install/jdk%{featurever}.install%{?1}}
%define packageoutputdir() %{expand:packages/jdk%{featurever}.packages%{?1}}
# we can copy the javadoc to not arched dir, or make it not noarch
%define uniquejavadocdir()    %{expand:%{fullversion}.%{_arch}%{?1}}
# main id and dir of this jdk
%define uniquesuffix()        %{expand:%{fullversion}.%{_arch}%{?1}}
# portable only declarations
%global jreimage                jre
%define jreportablenameimpl() %(echo %{uniquesuffix ""} | sed "s;el%{rhel}\\(_[0-9]\\)*;portable%{1}.jre;g")
%define jdkportablenameimpl() %(echo %{uniquesuffix ""} | sed "s;el%{rhel}\\(_[0-9]\\)*;portable%{1}.jdk;g")
%define staticlibsportablenameimpl() %(echo %{uniquesuffix ""} | sed "s;el%{rhel}\\(_[0-9]\\)*;portable%{1}.static-libs;g")
%define jreportablearchive()  %{expand:%{jreportablenameimpl -- %%{1}}.tar.xz}
%define jdkportablearchive()  %{expand:%{jdkportablenameimpl -- %%{1}}.tar.xz}
%define staticlibsportablearchive()  %{expand:%{staticlibsportablenameimpl -- %%{1}}.tar.xz}
%define jreportablename()     %{expand:%{jreportablenameimpl -- %%{1}}}
%define jdkportablename()     %{expand:%{jdkportablenameimpl -- %%{1}}}
# Intentionally use jdkportablenameimpl here since we want to have static-libs files overlayed on
# top of the JDK archive
%define staticlibsportablename()     %{expand:%{jdkportablenameimpl -- %%{1}}}
%define docportablename() %(echo %{uniquesuffix ""} | sed "s;el%{rhel}\\(_[0-9]\\)*;portable.docs;g")
%define docportablearchive()  %{docportablename}.tar.xz
%define miscportablename() %(echo %{uniquesuffix ""} | sed "s;el%{rhel}\\(_[0-9]\\)*;portable.misc;g")
%define miscportablearchive()  %{miscportablename}.tar.xz

#################################################################
# fix for https://bugzilla.redhat.com/show_bug.cgi?id=1111349
#         https://bugzilla.redhat.com/show_bug.cgi?id=1590796#c14
#         https://bugzilla.redhat.com/show_bug.cgi?id=1655938
%global _privatelibs libsplashscreen[.]so.*|libawt_xawt[.]so.*|libjli[.]so.*|libattach[.]so.*|libawt[.]so.*|libextnet[.]so.*|libawt_headless[.]so.*|libdt_socket[.]so.*|libfontmanager[.]so.*|libinstrument[.]so.*|libj2gss[.]so.*|libj2pcsc[.]so.*|libj2pkcs11[.]so.*|libjaas[.]so.*|libjavajpeg[.]so.*|libjdwp[.]so.*|libjimage[.]so.*|libjsound[.]so.*|liblcms[.]so.*|libmanagement[.]so.*|libmanagement_agent[.]so.*|libmanagement_ext[.]so.*|libmlib_image[.]so.*|libnet[.]so.*|libnio[.]so.*|libprefs[.]so.*|librmi[.]so.*|libsaproc[.]so.*|libsctp[.]so.*|libsystemconf[.]so.*|libzip[.]so.*%{freetype_lib}
%global _publiclibs libjawt[.]so.*|libjava[.]so.*|libjvm[.]so.*|libverify[.]so.*|libjsig[.]so.*
%if %is_system_jdk
%global __provides_exclude ^(%{_privatelibs})$
%global __requires_exclude ^(%{_privatelibs})$
# Never generate lib-style provides/requires for slowdebug packages
%global __provides_exclude_from ^.*/%{uniquesuffix -- %{debug_suffix_unquoted}}/.*$
%global __requires_exclude_from ^.*/%{uniquesuffix -- %{debug_suffix_unquoted}}/.*$
%global __provides_exclude_from ^.*/%{uniquesuffix -- %{fastdebug_suffix_unquoted}}/.*$
%global __requires_exclude_from ^.*/%{uniquesuffix -- %{fastdebug_suffix_unquoted}}/.*$
%else
# Don't generate provides/requires for JDK provided shared libraries at all.
%global __provides_exclude ^(%{_privatelibs}|%{_publiclibs})$
%global __requires_exclude ^(%{_privatelibs}|%{_publiclibs})$
%endif

# VM variant being built
# This is always 'server' on 17u which doesn't have JDK-8273494
%global vm_variant server

%global etcjavasubdir     %{_sysconfdir}/java/java-%{javaver}-%{origin}
%define etcjavadir()      %{expand:%{etcjavasubdir}/%{uniquesuffix -- %{?1}}}
# Standard JPackage directories and symbolic links.
%define sdkdir()        %{expand:%{uniquesuffix -- %{?1}}}
%define jrelnk()        %{expand:jre-%{javaver}-%{origin}-%{version}-%{release}.%{_arch}%{?1}}

%define sdkbindir()     %{expand:%{_jvmdir}/%{sdkdir -- %{?1}}/bin}
%define jrebindir()     %{expand:%{_jvmdir}/%{sdkdir -- %{?1}}/bin}

%global alt_java_name     alt-java

%global rpm_state_dir %{_localstatedir}/lib/rpm-state/

# For flatpack builds hard-code /usr/sbin/alternatives,
# otherwise use %%{_sbindir} relative path.
%if 0%{?flatpak}
%global alternatives_requires /usr/sbin/alternatives
%else
%global alternatives_requires %{_sbindir}/alternatives
%endif

# x86 is not supported by OpenJDK 17
ExcludeArch: %{ix86}

# Portables have no repo (requires/provides), but these are awesome for orientation in spec
# Also scriptlets are happily missing and files are handled old fashion
# not-duplicated requires/provides/obsoletes for normal/debug packages
%define java_rpo() %{expand:
}

%define java_devel_rpo() %{expand:
}

%define java_static_libs_rpo() %{expand:
}

%define java_unstripped_rpo() %{expand:
}

%define java_docs_rpo() %{expand:
}

%define java_misc_rpo() %{expand:
}

# Prevent brp-java-repack-jars from being run
%global __jar_repack 0

# portables have grown out of its component, moving back to java-x-vendor
# this expression, when declared as global, filled component with java-x-vendor portable
%define component %(echo %{name} | sed "s;-portable;;g")

Name:    java-%{javaver}-%{origin}-portable
Version: %{newjavaver}.%{buildver}
Release: %{?eaprefix}%{rpmrelease}%{?extraver}%{?dist}
# java-1.5.0-ibm from jpackage.org set Epoch to 1 for unknown reasons
# and this change was brought into RHEL-4. java-1.5.0-ibm packages
# also included the epoch in their virtual provides. This created a
# situation where in-the-wild java-1.5.0-ibm packages provided "java =
# 1:1.5.0". In RPM terms, "1.6.0 < 1:1.5.0" since 1.6.0 is
# interpreted as 0:1.6.0. So the "java >= 1.6.0" requirement would be
# satisfied by the 1:1.5.0 packages. Thus we need to set the epoch in
# JDK package >= 1.6.0 to 1, and packages referring to JDK virtual
# provides >= 1.6.0 must specify the epoch, "java >= 1:1.6.0".

Epoch:   1
Summary: %{origin_nice} %{featurever} Runtime Environment portable edition
# Groups are only used up to RHEL 8 and on Fedora versions prior to F30
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

# HotSpot code is licensed under GPLv2
# JDK library code is licensed under GPLv2 with the Classpath exception
# The Apache license is used in code taken from Apache projects (primarily xalan & xerces)
# DOM levels 2 & 3 and the XML digital signature schemas are licensed under the W3C Software License
# The JSR166 concurrency code is in the public domain
# The BSD and MIT licenses are used for a number of third-party libraries (see ADDITIONAL_LICENSE_INFO)
# The OpenJDK source tree includes:
# - JPEG library (IJG), zlib & libpng (zlib), giflib (MIT), harfbuzz (ISC),
# - freetype (FTL), jline (BSD) and LCMS (MIT)
# - jquery (MIT), jdk.crypto.cryptoki PKCS 11 wrapper (RSA)
# - public_suffix_list.dat from publicsuffix.org (MPLv2.0)
# The test code includes copies of NSS under the Mozilla Public License v2.0
# The PCSClite headers are under a BSD with advertising license
# The elliptic curve cryptography (ECC) source code is licensed under the LGPLv2.1 or any later version
License:  ASL 1.1 and ASL 2.0 and BSD and BSD with advertising and GPL+ and GPLv2 and GPLv2 with exceptions and IJG and LGPLv2+ and MIT and MPLv2.0 and Public Domain and W3C and zlib and ISC and FTL and RSA
URL:      http://openjdk.java.net/

# The source tarball, generated using generate_source_tarball.sh
Source0: https://openjdk-sources.osci.io/openjdk%{featurever}/open%{vcstag}%{ea_designator_zip}.tar.xz

# Use 'icedtea_sync.sh' to update the following
# They are based on code contained in the IcedTea project (6.x).
# Systemtap tapsets. Zipped up to keep it small.
Source8: tapsets-icedtea-%{icedteaver}.tar.xz

# Desktop files. Adapted from IcedTea
# Disabled in portables
#Source9: jconsole.desktop.in

# Release notes
Source10: NEWS

# nss configuration file
Source11: nss.cfg.in

# Removed libraries that we link instead
Source12: remove-intree-libraries.sh

# Ensure we aren't using the limited crypto policy
Source13: TestCryptoLevel.java

# Ensure ECDSA is working
Source14: TestECDSA.java

# Verify system crypto (policy) can be disabled via a property
Source15: TestSecurityProperties.java

# Ensure vendor settings are correct
Source16: CheckVendor.java

# Ensure translations are available for new timezones
Source18: TestTranslations.java

############################################
#
# RPM/distribution specific patches
#
############################################

# This patch is probably not necessary anymore.  I will revisit
# removing it if I find that QE performs AWT testing on a per-release
# basis.
# Ignore AWTError when assistive technologies are loaded
Patch1:    rh1648242-accessible_toolkit_crash_do_not_break_jvm.patch
# This patch is almost certainly not needed, but I am keeping it
# forever because java.security has shipped to customers already, and
# is marked %config(noreplace).  I do not want to risk
# warnings/confusion/conflict by changing its default contents
# mid-lifecycle.
# NSS via SunPKCS11 Provider (commented out due to memory leak).
Patch1000: rh1648249-add_commented_out_nss_cfg_provider_to_java_security.patch
# RH1750419: enable build of speculative store bypass hardened alt-java (CVE-2018-3639)
Patch600: rh1750419-redhat_alt_java.patch
# gnu_andrew is working on backporting a fix for this patch to 17u.
# Depend on pcsc-lite-libs instead of pcsc-lite-devel as this is only in optional repo
Patch6: rh1684077-openjdk_should_depend_on_pcsc-lite-libs_instead_of_pcsc-lite-devel.patch

# Crypto policy and FIPS support patches
# Patch is generated from the fips-17u tree at https://github.com/rh-openjdk/jdk/tree/fips-17u
# as follows: git diff %%{vcstag} src make test > fips-17u-$(git show -s --format=%h HEAD).patch
# Diff is limited to src and make subdirectories to exclude .github changes
# The following list is generated by:
# git log %%{vcstag}.. --no-merges --format=%s --reverse
# Fixes currently included:
# PR3183, RH1340845: Support Fedora & RHEL system crypto policy
# PR3695: Allow system crypto policy enforcement to be toggled on/off
# RH1655466: Support global RHEL crypto policy
# RH1818909: Set default keystore type for PKCS11 provider in FIPS mode
# RH1860986: Disable TLSv1.3 in FIPS mode
# RH1915071: Always initialise configurator access.patch
# RH1929465: Improve system FIPS detection
# RH1995150: Disable non-FIPS crypto in the SUN and SunEC providers
# RH1996182: Login to the NSS Software Token in FIPS Mode
# RH1929465: Don't define unused throwIOException function when using NSS detection
# RH1996182: Extend default security policy to allow SunPKCS11 access to jdk.internal.access
# RH1991003: Enable the import of plain keys into the NSS software token.
# RH2021263: Return in C code after having generated Java exception
# RH2021263: Make sure java.security.Security is initialised when retrieving JavaSecuritySystemConfiguratorAccess instance
# RH2021263: Improve Security initialisation, now FIPS support no longer relies on crypto policy support
# RH2051605: Detect NSS at Runtime for FIPS detection
# RH2052070: Enable AlgorithmParameters and AlgorithmParameterGenerator services in FIPS mode
# RH2023467: Enable FIPS keys export (#1)
# Run workflows on pull request, as we are not using SKARA.
# RH2094027: SunEC runtime permission for FIPS (#5)
# RH2036462: sun.security.pkcs11.wrapper.PKCS11.getInstance breakage (#8)
# RH2090378: Revert to disabling system security properties and FIPS mode support together (#4)
# Use encoded space rather than quoting for JTReg JAVA_OPTIONS
# RH2104724: Avoid import/export of DH private keys (#14)
# RH2092507: P11Key.getEncoded does not work for DH keys in FIPS mode (#16)
# Build the systemconf library on all platforms (#7)
# RH2048582: Support PKCS#12 keystores (#2)
# RH2020290: Support TLS 1.3 in FIPS mode (#13)
# Add nss.fips.cfg support to OpenJDK tree (#22)
# RH2117972 - Extend the support for NSS DBs (PKCS11) in FIPS mode (#17)
# Remove forgotten dead code from #13 and #14 (#21)
# Fix issue on FIPS with a SecurityManager in place (#25)
# RH2134669: Add missing attributes when registering services in FIPS mode. (#19)
# test/jdk/sun/security/pkcs11/fips/VerifyMissingAttributes.java: fixed jtreg main class (#27)
# RH1940064: Enable XML Signature provider in FIPS mode (#24)
# RH2173781: Avoid calling C_GetInfo() too early, before cryptoki is initialized (#26)
Patch1001: fips-%{featurever}u-%{fipsver}.patch

#############################################
#
# OpenJDK patches in need of upstreaming
#
#############################################

# Currently empty

#############################################
#
# OpenJDK patches which missed last update
#
#############################################

#############################################
#
# Portable build specific patches
#
#############################################

# Currently empty

BuildRequires: autoconf
BuildRequires: automake
BuildRequires: alsa-lib-devel
BuildRequires: binutils
BuildRequires: cups-devel
BuildRequires: desktop-file-utils
# elfutils only are OK for build without AOT
BuildRequires: elfutils-devel
BuildRequires: file
BuildRequires: fontconfig-devel
BuildRequires: gcc-c++
BuildRequires: gdb
BuildRequires: libxslt
BuildRequires: libX11-devel
BuildRequires: libXi-devel
BuildRequires: libXinerama-devel
BuildRequires: libXrandr-devel
BuildRequires: libXrender-devel
BuildRequires: libXt-devel
BuildRequires: libXtst-devel
# Requirement for setting up nss.cfg
BuildRequires: nss-devel
# Requirement for system security property test
# N/A for portable. RHEL7 doesn't provide them
#BuildRequires: crypto-policies
BuildRequires: pkgconfig
BuildRequires: xorg-x11-proto-devel
BuildRequires: zip
# to pack portable tarballs
BuildRequires: tar
BuildRequires: unzip
# Define _jvmdir macro
BuildRequires: javapackages-filesystem
BuildRequires: java-%{buildjdkver}-openjdk-devel
# Zero-assembler build requirement
%ifarch %{zero_arches}
BuildRequires: libffi-devel
%endif
# Full documentation build requirements
BuildRequires: graphviz
BuildRequires: pandoc
# 2024a required as of JDK-8325150
BuildRequires: tzdata-java >= 2024a
# cacerts build requirement in portable mode
BuildRequires: ca-certificates
# Earlier versions have a bug in tree vectorization on PPC
BuildRequires: gcc >= 4.8.3-8

%if %{with_systemtap}
BuildRequires: systemtap-sdt-devel
%endif
BuildRequires: make

%if %{system_libs}
BuildRequires: freetype-devel
BuildRequires: giflib-devel
BuildRequires: harfbuzz-devel
BuildRequires: lcms2-devel
BuildRequires: libjpeg-devel
BuildRequires: libpng-devel
%else
# Version in src/java.desktop/share/legal/freetype.md
Provides: bundled(freetype) = 2.13.2
# Version in src/java.desktop/share/native/libsplashscreen/giflib/gif_lib.h
Provides: bundled(giflib) = 5.2.1
# Version in src/java.desktop/share/native/libharfbuzz/hb-version.h
Provides: bundled(harfbuzz) = 8.2.2
# Version in src/java.desktop/share/native/liblcms/lcms2.h
Provides: bundled(lcms2) = 2.15.0
# Version in src/java.desktop/share/native/libjavajpeg/jpeglib.h
Provides: bundled(libjpeg) = 6b
# Version in src/java.desktop/share/native/libsplashscreen/libpng/png.h
Provides: bundled(libpng) = 1.6.40
# We link statically against libstdc++ to increase portability
BuildRequires: libstdc++-static
%endif

# this is always built, also during debug-only build
# when it is built in debug-only this package is just placeholder
%{java_rpo %{nil}}

%description
The %{origin_nice} %{featurever} runtime environment - portable edition.

%if %{include_debug_build}
%package slowdebug
Summary: %{origin_nice} %{featurever} Runtime Environment portable edition %{debug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_rpo -- %{debug_suffix_unquoted}}
%description slowdebug
The %{origin_nice} %{featurever} runtime environment - portable edition.
%{debug_warning}
%endif

%if %{include_fastdebug_build}
%package fastdebug
Summary: %{origin_nice} %{featurever} Runtime Environment portable edition %{fastdebug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_rpo -- %{fastdebug_suffix_unquoted}}
%description fastdebug
The %{origin_nice} %{featurever} runtime environment - portable edition.
%{fastdebug_warning}
%endif

%if %{include_normal_build}
%package devel
Summary: %{origin_nice} %{featurever} Development Environment portable edition
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_devel_rpo %{nil}}

%description devel
The %{origin_nice} %{featurever} development tools - portable edition.
%endif

%if %{include_debug_build}
%package devel-slowdebug
Summary: %{origin_nice} %{featurever} Runtime and Development Environment portable edition %{debug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_devel_rpo -- %{debug_suffix_unquoted}}

%description devel-slowdebug
The %{origin_nice} %{featurever} development tools - portable edition.
%{debug_warning}
%endif

%if %{include_fastdebug_build}
%package devel-fastdebug
Summary: %{origin_nice} %{featurever} Runtime and Development Environment portable edition %{fastdebug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Tools
%endif

%{java_devel_rpo -- %{fastdebug_suffix_unquoted}}

%description devel-fastdebug
The %{origin_nice} %{featurever} runtime environment and development tools - portable edition
%{fastdebug_warning}
%endif

%if %{include_staticlibs}

%if %{include_normal_build}
%package static-libs
Summary: %{origin_nice} %{featurever} libraries for static linking - portable edition

%{java_static_libs_rpo %{nil}}

%description static-libs
The %{origin_nice} %{featurever} libraries for static linking - portable edition.
%endif

%if %{include_debug_build}
%package static-libs-slowdebug
Summary: %{origin_nice} %{featurever} libraries for static linking - portable edition %{debug_on}

%{java_static_libs_rpo -- %{debug_suffix_unquoted}}

%description static-libs-slowdebug
The %{origin_nice} %{featurever} libraries for static linking - portable edition
%{debug_warning}
%endif

%if %{include_fastdebug_build}
%package static-libs-fastdebug
Summary: %{origin_nice} %{featurever} libraries for static linking - portable edition %{fastdebug_on}

%{java_static_libs_rpo -- %{fastdebug_suffix_unquoted}}

%description static-libs-fastdebug
The %{origin_nice} %{featurever} libraries for static linking - portable edition
%{fastdebug_warning}
%endif

# staticlibs
%endif

%if %{include_normal_build}
%package unstripped
Summary: The %{origin_nice} %{featurever} runtime environment.

%{java_unstripped_rpo %{nil}}

%description unstripped
The %{origin_nice} %{featurever} runtime environment.

%endif

%package docs
Summary: %{origin_nice} %{featurever} API documentation

%{java_docs_rpo %{nil}}

%description docs
The %{origin_nice} %{featurever} API documentation.

%package misc
Summary: %{origin_nice} %{featurever} miscellany

%{java_misc_rpo %{nil}}

%description misc
The %{origin_nice} %{featurever} miscellany.

%prep

echo "Preparing %{oj_vendor_version}"

# Using the echo macro breaks rpmdev-bumpspec, as it parses the first line of stdout :-(
%if 0%{?stapinstall:1}
  echo "CPU: %{_target_cpu}, arch install directory: %{archinstall}, SystemTap install directory: %{stapinstall}"
%else
  %{error:Unrecognised architecture %{_target_cpu}}
%endif

if [ %{include_normal_build} -eq 0 -o  %{include_normal_build} -eq 1 ] ; then
  echo "include_normal_build is %{include_normal_build}"
else
  echo "include_normal_build is %{include_normal_build}, that is invalid. Use 1 for yes or 0 for no"
  exit 11
fi
if [ %{include_debug_build} -eq 0 -o  %{include_debug_build} -eq 1 ] ; then
  echo "include_debug_build is %{include_debug_build}"
else
  echo "include_debug_build is %{include_debug_build}, that is invalid. Use 1 for yes or 0 for no"
  exit 12
fi
if [ %{include_fastdebug_build} -eq 0 -o  %{include_fastdebug_build} -eq 1 ] ; then
  echo "include_fastdebug_build is %{include_fastdebug_build}"
else
  echo "include_fastdebug_build is %{include_fastdebug_build}, that is invalid. Use 1 for yes or 0 for no"
  exit 13
fi
if [ %{include_debug_build} -eq 0 -a  %{include_normal_build} -eq 0 -a  %{include_fastdebug_build} -eq 0 ] ; then
  echo "You have disabled all builds (normal,fastdebug,slowdebug). That is a no go."
  exit 14
fi

%if %{with fresh_libjvm} && ! %{build_hotspot_first}
echo "WARNING: The build of a fresh libjvm has been disabled due to a JDK version mismatch"
echo "Build JDK version is %{buildjdkver}, feature JDK version is %{featurever}"
%endif

export XZ_OPT="-T0"
%setup -q -c -n %{uniquesuffix ""} -T -a 0
# https://bugzilla.redhat.com/show_bug.cgi?id=1189084
prioritylength=`expr length %{priority}`
if [ $prioritylength -ne 8 ] ; then
 echo "priority must be 8 digits in total, violated"
 exit 14
fi

# OpenJDK patches

%if %{system_libs}
# Remove libraries that are linked by both static and dynamic builds
sh %{SOURCE12} %{top_level_dir_name}
%endif

# Patch the JDK
pushd %{top_level_dir_name}
# This syntax is deprecated:
#    %patchN [...]
# and should be replaced with:
#    %patch -PN [...]
# For example:
#    %patch1001 -p1
# becomes:
#    %patch -P1001 -p1
# The replacement format suggested by recent (circa Fedora 38) RPM
# deprecation messages:
#    %patch N [...]
# is not backward-compatible with prior (circa RHEL-8) versions of
# rpmbuild.
%patch -P1 -p1
%patch -P6 -p1
# Add crypto policy and FIPS support
%patch -P1001 -p1
# nss.cfg PKCS11 support; must come last as it also alters java.security
%patch -P1000 -p1
# alt-java support
%patch -P600 -p1
popd # openjdk


# The OpenJDK version file includes the current
# upstream version information. For some reason,
# configure does not automatically use the
# default pre-version supplied there (despite
# what the file claims), so we pass it manually
# to configure
VERSION_FILE=$(pwd)/%{top_level_dir_name}/make/conf/version-numbers.conf
if [ -f ${VERSION_FILE} ] ; then
    UPSTREAM_EA_DESIGNATOR=$(grep '^DEFAULT_PROMOTED_VERSION_PRE' ${VERSION_FILE} | cut -d '=' -f 2)
else
    echo "Could not find OpenJDK version file.";
    exit 16
fi
if [ "x${UPSTREAM_EA_DESIGNATOR}" != "x%{ea_designator}" ] ; then
    echo "WARNING: Designator mismatch";
    echo "Spec file is configured for a %{build_type} build with designator '%{ea_designator}'"
    echo "Upstream version-pre setting is '${UPSTREAM_EA_DESIGNATOR}'";
    exit 17
fi

# Extract systemtap tapsets
%if %{with_systemtap}
tar --strip-components=1 -x -I xz -f %{SOURCE8}
%if %{include_debug_build}
cp -r tapset tapset%{debug_suffix}
%endif
%if %{include_fastdebug_build}
cp -r tapset tapset%{fastdebug_suffix}
%endif

for suffix in %{build_loop} ; do
  for file in "tapset"$suffix/*.in; do
    sed -i -e "s:@JAVA_SPEC_VER@:%{javaver}:g" $file
    sed -i -e "s:@INSTALL_ARCH_DIR@:%{archinstall}:g" $file
  done
done
# systemtap tapsets ends
%endif

# Prepare desktop files
# Portables do not have desktop integration

# Setup nss.cfg
sed -e "s:@NSS_LIBDIR@:%{NSS_LIBDIR}:g" %{SOURCE11} > nss.cfg

%build

# How many CPU's do we have?
export NUM_PROC=%(/usr/bin/getconf _NPROCESSORS_ONLN 2> /dev/null || :)
export NUM_PROC=${NUM_PROC:-1}
%if 0%{?_smp_ncpus_max}
# Honor %%_smp_ncpus_max
[ ${NUM_PROC} -gt %{?_smp_ncpus_max} ] && export NUM_PROC=%{?_smp_ncpus_max}
%endif
export XZ_OPT="-T0"

%ifarch s390x sparc64 alpha %{power64} %{aarch64}
export ARCH_DATA_MODEL=64
%endif
%ifarch alpha
export CFLAGS="$CFLAGS -mieee"
%endif

# We use ourcppflags because the OpenJDK build seems to
# pass EXTRA_CFLAGS to the HotSpot C++ compiler...
# Explicitly set the C++ standard as the default has changed on GCC >= 6
EXTRA_CFLAGS="%ourcppflags"
EXTRA_CPP_FLAGS="%ourcppflags"

%ifarch %{power64} ppc
# fix rpmlint warnings
EXTRA_CFLAGS="$EXTRA_CFLAGS -fno-strict-aliasing"
%endif
%ifarch %{ix86}
# Align stack boundary on x86_32
EXTRA_CFLAGS="$(echo ${EXTRA_CFLAGS} | sed -e 's|-mstackrealign|-mincoming-stack-boundary=2 -mpreferred-stack-boundary=4|')"
EXTRA_CPP_FLAGS="$(echo ${EXTRA_CPP_FLAGS} | sed -e 's|-mstackrealign|-mincoming-stack-boundary=2 -mpreferred-stack-boundary=4|')"
%endif
export EXTRA_CFLAGS EXTRA_CPP_FLAGS

echo "Building %{newjavaver}-%{buildver}, pre=%{ea_designator}, opt=%{lts_designator}"

# Set modification times (mtimes) of files within JAR files generated
# by the OpenJDK build to a timestamp that is constant across RPM
# rebuilds.  OpenJDK provides the --with-source-date configure option
# for this purpose.  Potential arguments in the RPM build context are:
#
# A) --with-source-date="${SOURCE_DATE_EPOCH}"
# B) --with-source-date=version
# C) --with-source-date="${OPENJDK_UPSTREAM_TAG_EPOCH}"
#
# Consider Option A.  Fedora 38 (rpm-4.18.2) and RHEL-8 (rpm-4.14.3)
# have different support for SOURCE_DATE_EPOCH.  To keep
# SOURCE_DATE_EPOCH constant across RPM rebuilds, one could set the
# source_date_epoch_from_changelog macro to 1 on both Fedora 38 and
# RHEL-8.  However, on RHEL-8, this results in the RPM build times
# being set to the timestamp of the most recent changelog.  This is
# bad for tracing when RPMs were actually built.  Fedora 38 supports a
# better behaviour via the introduction of the
# use_source_date_epoch_as_buildtime macro, set to 0 by default.
# There is no way to make this work on RHEL-8 as well though, so
# option A is suboptimal.
#
# Option B uses the value of the DEFAULT_VERSION_DATE field from
# make/conf/version-numbers.conf.  DEFAULT_VERSION_DATE represents the
# aspirational eventual JDK general availability (GA) release date.
# When the RPM build occurs prior to GA, generated JAR files will have
# payload mtimes in the future relative to the RPM build time.
# Whereas for tarballs some tools will issue warnings about future
# mtimes, per OPENJDK-2583 apparently this is no problem for Java and
# JAR files.
#
# Option C uses the modification timestamp of files in the source
# tarball. The reproducibility logic in generate_source_tarball.sh
# sets them all to the commit time of the release-tagged OpenJDK
# commit, as archived in the tarball.  This timestamp is deterministic
# across RPM rebuilds and is reliably in the past.  Any file's mtime
# will do, so use version-numbers.conf's.
#
# Use option B for JAR files, based on the discussion in OPENJDK-2583.
#
# For portable tarballs, use option C (OPENJDK_UPSTREAM_TAG_EPOCH) for
# the modification times of all files in the portable tarballs.  Doing
# so eliminates one source of variability across RPM rebuilds.
VERSION_FILE="$(pwd)"/"%{top_level_dir_name}"/make/conf/version-numbers.conf
OPENJDK_UPSTREAM_TAG_EPOCH="$(stat --format=%Y "${VERSION_FILE}")"

function buildjdk() {
    local outputdir=${1}
    local buildjdk=${2}
    local maketargets="${3}"
    local debuglevel=${4}
    local link_opt=${5}
    local debug_symbols=${6}

    local top_dir_abs_src_path=$(pwd)/%{top_level_dir_name}
    local top_dir_abs_build_path=$(pwd)/${outputdir}

    # This must be set using the global, so that the
    # static libraries still use a dynamic stdc++lib
    if [ "x%{link_type}" = "xbundled" ] ; then
        libc_link_opt="static";
    else
        libc_link_opt="dynamic";
    fi

    echo "Using output directory: ${outputdir}";
    echo "Checking build JDK ${buildjdk} is operational..."
    ${buildjdk}/bin/java -version
    echo "Using make targets: ${maketargets}"
    echo "Using debuglevel: ${debuglevel}"
    echo "Using link_opt: ${link_opt}"
    echo "Using debug_symbols: ${debug_symbols}"
    echo "Building %{newjavaver}-%{buildver}, pre=%{ea_designator}, opt=%{lts_designator}"

    mkdir -p ${outputdir}
    pushd ${outputdir}

    # Note: zlib and freetype use %{link_type}
    # rather than ${link_opt} as the system versions
    # are always used in a system_libs build, even
    # for the static library build
    bash ${top_dir_abs_src_path}/configure \
%ifarch %{zero_arches}
    --with-jvm-variants=zero \
%endif
    --with-cacerts-file=$(readlink -f %{_sysconfdir}/pki/java/cacerts)  \
    --with-version-build=%{buildver} \
    --with-version-pre="%{ea_designator}" \
    --with-version-opt="%{lts_designator}" \
    --with-vendor-version-string="%{oj_vendor_version}" \
    --with-vendor-name="%{oj_vendor}" \
    --with-vendor-url="%{oj_vendor_url}" \
    --with-vendor-bug-url="%{oj_vendor_bug_url}" \
    --with-vendor-vm-bug-url="%{oj_vendor_bug_url}" \
    --with-boot-jdk=${buildjdk} \
    --with-debug-level=${debuglevel} \
    --with-native-debug-symbols="${debug_symbols}" \
    --disable-sysconf-nss \
    --enable-unlimited-crypto \
    --with-zlib=%{link_type} \
    --with-freetype=%{link_type} \
    --with-libjpeg=${link_opt} \
    --with-giflib=${link_opt} \
    --with-libpng=${link_opt} \
    --with-lcms=${link_opt} \
    --with-harfbuzz=${link_opt} \
    --with-stdc++lib=${libc_link_opt} \
    --with-extra-cxxflags="$EXTRA_CPP_FLAGS" \
    --with-extra-cflags="$EXTRA_CFLAGS" \
    --with-extra-ldflags="%{ourldflags}" \
    --with-num-cores="$NUM_PROC" \
    --with-source-date=version \
    --disable-javac-server \
%ifarch %{zgc_arches}
    --with-jvm-features=zgc \
%endif
    --disable-warnings-as-errors

    cat spec.gmk
    make LOG=trace $maketargets || \
        ( pwd; find ${top_dir_abs_src_path} ${top_dir_abs_build_path} -name "hs_err_pid*.log" | xargs cat && false )

    popd
}

function stripjdk() {
    local outputdir=${1}
    local jdkimagepath=${outputdir}/images/%{jdkimage}
    local jreimagepath=${outputdir}/images/%{jreimage}
    local jmodimagepath=${outputdir}/images/jmods
    local supportdir=${outputdir}/support

    if [ "x$suffix" = "x" ] ; then
        # Keep the unstripped version for consumption by RHEL RPMs
        cp -a ${jdkimagepath}{,.unstripped}

        # Strip the files
        for file in $(find ${jdkimagepath} ${jreimagepath} ${supportdir} -type f) ; do
            if file ${file} | grep -q 'ELF'; then
                noextfile=${file/.so/};
                objcopy --only-keep-debug ${file} ${noextfile}.debuginfo;
                objcopy --add-gnu-debuglink=${noextfile}.debuginfo ${file};
                strip -g ${file};
            fi
        done

        # Rebuild jmod files against the stripped binaries
        if [ ! -d ${supportdir} ] ; then
            echo "Support directory missing.";
            exit 15
        fi
        for cmd in $(find ${supportdir} -name '*.jmod_exec.cmdline') ; do
            pre=${cmd/_exec/_pre};
            post=${cmd/_exec/_post};
            jmod=$(echo ${cmd}|sed 's#.*_create_##'|sed 's#_exec.cmdline##')
            echo "Rebuilding ${jmod} against stripped binaries...";
            if [ -e ${pre} ] ; then
                echo "Executing ${pre}...";
                cat ${pre} | sh -s ;
            fi
            echo "Executing ${cmd}...";
            cat ${cmd} | sh -s ;
            if [ -e ${post} ] ; then
                echo "Executing ${post}...";
                cat ${post} | sh -s ;
            fi
        done
        rm -rf ${jdkimagepath}/jmods
        cp -a ${jmodimagepath} ${jdkimagepath}
    fi
}

function installjdk() {
    local outputdir=${1}
    local installdir=${2}
    local jdkimagepath=${installdir}/images/%{jdkimage}
    local jreimagepath=${installdir}/images/%{jreimage}
    local unstripped=${jdkimagepath}.unstripped

    echo "Installing build from ${outputdir} to ${installdir}..."
    mkdir -p ${installdir}
    echo "Installing images..."
    mv ${outputdir}/images ${installdir}
    if [ -d ${outputdir}/bundles ] ; then
        echo "Installing bundles...";
        mv ${outputdir}/bundles ${installdir} ;
    fi

%if !%{with artifacts}
    echo "Removing output directory...";
    rm -rf ${outputdir}
%endif

    # legacy-jre-image target does not install any man pages for the JRE
    # We copy the jdk man directory and then remove pages for binaries that
    # don't exist in the JRE
    cp -a ${jdkimagepath}/man ${jreimagepath}
    for manpage in $(find ${jreimagepath}/man -name '*.1'); do
        filename=$(basename ${manpage});
        binary=${filename/.1/};
        if [ ! -f ${jreimagepath}/bin/${binary} ] ; then
            echo "Removing ${manpage} from JRE for which no binary ${binary} exists";
            rm -f ${manpage};
        fi;
    done

    for imagepath in ${jdkimagepath} ${jreimagepath} ${unstripped}; do

        if [ -d ${imagepath} ] ; then
            # the build (erroneously) removes read permissions from some jars
            # this is a regression in OpenJDK 7 (our compiler):
            # http://icedtea.classpath.org/bugzilla/show_bug.cgi?id=1437
            find ${imagepath} -iname '*.jar' -exec chmod ugo+r {} \;

            # Build screws up permissions on binaries
            # https://bugs.openjdk.java.net/browse/JDK-8173610
            find ${imagepath} -iname '*.so' -exec chmod +x {} \;
            find ${imagepath}/bin/ -exec chmod +x {} \;

            # Install local files which are distributed with the JDK
            install -m 644 %{SOURCE10} ${imagepath}
            install -m 644 nss.cfg ${imagepath}/conf/security/

            # Create fake alt-java as a placeholder for future alt-java
            pushd ${imagepath}
            # add alt-java man page
            echo "Hardened java binary recommended for launching untrusted code from the Web e.g. javaws" > man/man1/%{alt_java_name}.1
            cat man/man1/java.1 >> man/man1/%{alt_java_name}.1
            popd

            # Print release information
            cat ${imagepath}/release
        fi
    done
}

function genchecksum() {
    local checkedfile=${1}

    checkdir=$(dirname ${1})
    checkfile=$(basename ${1})

    echo "Generating checksum for ${checkfile} in ${checkdir}..."
    pushd ${checkdir}
    sha256sum ${checkfile} > ${checkfile}.sha256sum
    sha256sum --check ${checkfile}.sha256sum
    popd
}

function packagejdk() {
    local imagesdir=$(pwd)/${1}/images
    local docdir=$(pwd)/${1}/images/docs
    local bundledir=$(pwd)/${1}/bundles
    local packagesdir=$(pwd)/${2}
    local srcdir=$(pwd)/%{top_level_dir_name}
    local tapsetdir=$(pwd)/tapset
    # See https://reproducible-builds.org/docs/archives/
    # RHEL-7 has tar 1.26 which does not support --sort=name, so use
    # find-piped-through-sort instead.  Omit --pax-option since it
    # made the docs package not reproducible due to PaxHeaders
    # timestamp differences.
    local tar_opts="--mtime=@${OPENJDK_UPSTREAM_TAG_EPOCH} \
                    --owner=0 \
                    --group=0 \
                    --numeric-owner \
                    --no-recursion \
                    --null \
                    --files-from - \
                    --create \
                    --xz \
                    --file"

    echo "Packaging build from ${imagesdir} to ${packagesdir}..."
    mkdir -p ${packagesdir}
    pushd ${imagesdir}

    if [ "x$suffix" = "x" ] ; then
        nameSuffix=""
    else
        nameSuffix=`echo "$suffix"| sed s/-/./`
    fi

    jdkname=%{jdkportablename -- "$nameSuffix"}
    jdkarchive=${packagesdir}/%{jdkportablearchive -- "$nameSuffix"}
    jrename=%{jreportablename -- "$nameSuffix"}
    jrearchive=${packagesdir}/%{jreportablearchive -- "$nameSuffix"}
    staticname=%{staticlibsportablename -- "$nameSuffix"}
    staticarchive=${packagesdir}/%{staticlibsportablearchive -- "$nameSuffix"}
    debugarchive=${packagesdir}/%{jdkportablearchive -- "${nameSuffix}.debuginfo"}
    unstrippedarchive=${packagesdir}/%{jdkportablearchive -- "${nameSuffix}.unstripped"}
    # We only use docs for the release build
    docname=%{docportablename}
    docarchive=${packagesdir}/%{docportablearchive}
    built_doc_archive=jdk-%{filever}%{ea_designator_zip}+%{buildver}%{lts_designator_zip}-docs.zip
    # These are from the source tree so no debug variants
    miscname=%{miscportablename}
    miscarchive=${packagesdir}/%{miscportablearchive}

    if [ "x$suffix" = "x" ] ; then
        # Keep the unstripped version for consumption by RHEL RPMs
        mv %{jdkimage}.unstripped ${jdkname}
        find ${jdkname} -print0 | LC_ALL=C sort -z | tar ${tar_opts} ${unstrippedarchive}
        genchecksum ${unstrippedarchive}
        mv ${jdkname} %{jdkimage}.unstripped
    fi

    # Rename directories for packaging
    mv %{jdkimage} ${jdkname}
    mv %{jreimage} ${jrename}

    # Release images have external debug symbols
    if [ "x$suffix" = "x" ] ; then
        find ${jdkname} -name \*.debuginfo -print0 | LC_ALL=C sort -z | tar ${tar_opts} ${debugarchive}
        genchecksum ${debugarchive}

        mkdir ${docname}
        mv ${docdir} ${docname}
        mv ${bundledir}/${built_doc_archive} ${docname}
        find ${docname} -print0 | LC_ALL=C sort -z | tar ${tar_opts} ${docarchive}
        genchecksum ${docarchive}

        mkdir ${miscname}
        for s in 16 24 32 48 ; do
            cp -av ${srcdir}/src/java.desktop/unix/classes/sun/awt/X11/java-icon${s}.png ${miscname}
        done
        cp -a ${srcdir}/src/sample ${miscname}
%if %{with_systemtap}
        cp -a ${tapsetdir}* ${miscname}
%endif
        find ${miscname} -print0 | LC_ALL=C sort -z | tar ${tar_opts} ${miscarchive}
        genchecksum ${miscarchive}
    fi

    find ${jdkname} -print0 | LC_ALL=C sort -z | tar --exclude='**.debuginfo' ${tar_opts} ${jdkarchive}
    genchecksum ${jdkarchive}

    find ${jrename} -print0 | LC_ALL=C sort -z | tar --exclude='**.debuginfo' ${tar_opts} ${jrearchive}
    genchecksum ${jrearchive}

%if %{include_staticlibs}
    # Static libraries (needed for building graal vm with native image)
    # Tar as overlay. Transform to the JDK name, since we just want to "add"
    # static libraries to that folder
    find "%{static_libs_image}/lib" -print0 | LC_ALL=C sort -z \
        | tar --transform "s|^%{static_libs_image}/lib/*|${staticname}/lib/static/linux-%{archinstall}/glibc/|" ${tar_opts} ${staticarchive}
    genchecksum ${staticarchive}
%endif

    # Revert directory renaming so testing will run
    # TODO: testing should run on the packaged JDK
    mv ${jdkname} %{jdkimage}
    mv ${jrename} %{jreimage}

    popd #images

}

%if %{build_hotspot_first}
  # Build a fresh libjvm.so first and use it to bootstrap
  cp -LR --preserve=mode,timestamps %{bootjdk} newboot
  systemjdk=$(pwd)/newboot
  buildjdk build/newboot ${systemjdk} %{hotspot_target} "release" "bundled" "internal"
  mv build/newboot/jdk/lib/%{vm_variant}/libjvm.so newboot/lib/%{vm_variant}
%else
  systemjdk=%{bootjdk}
%endif

for suffix in %{build_loop} ; do

  if [ "x$suffix" = "x" ] ; then
      debugbuild=release
  else
      # change --something to something
      debugbuild=`echo $suffix  | sed "s/-//g"`
  fi
  # We build with internal debug symbols and do
  # our own stripping for one version of the
  # release build
  debug_symbols=internal

  builddir=%{buildoutputdir -- ${suffix}}
  bootbuilddir=boot${builddir}
  installdir=%{installoutputdir -- ${suffix}}
  bootinstalldir=boot${installdir}
  packagesdir=%{packageoutputdir -- ${suffix}}

  link_opt="%{link_type}"
%if %{system_libs}
  # Copy the source tree so we can remove all in-tree libraries
  cp -a %{top_level_dir_name} %{top_level_dir_name_backup}
  # Remove all libraries that are linked
  sh %{SOURCE12} %{top_level_dir_name} full
%endif
  # Debug builds don't need same targets as release for
  # build speed-up. We also avoid bootstrapping these
  # slower builds.
  if echo $debugbuild | grep -q "debug" ; then
      maketargets="%{debug_targets}"
      run_bootstrap=false
  else
      maketargets="%{release_targets}"
      run_bootstrap=%{bootstrap_build}
  fi
  if ${run_bootstrap} ; then
      buildjdk ${bootbuilddir} ${systemjdk} "%{bootstrap_targets}" ${debugbuild} ${link_opt} ${debug_symbols}
      installjdk ${bootbuilddir} ${bootinstalldir}
      buildjdk ${builddir} $(pwd)/${bootinstalldir}/images/%{jdkimage} "${maketargets}" ${debugbuild} ${link_opt} ${debug_symbols}
      stripjdk ${builddir}
      installjdk ${builddir} ${installdir}
      %{!?with_artifacts:rm -rf ${bootinstalldir}}
  else
      buildjdk ${builddir} ${systemjdk} "${maketargets}" ${debugbuild} ${link_opt} ${debug_symbols}
      stripjdk ${builddir}
      installjdk ${builddir} ${installdir}
  fi
  packagejdk ${installdir} ${packagesdir}

%if %{system_libs}
  # Restore original source tree we modified by removing full in-tree sources
  rm -rf %{top_level_dir_name}
  mv %{top_level_dir_name_backup} %{top_level_dir_name}
%endif

# build cycles
done # end of release / debug cycle loop

%check

# We test debug first as it will give better diagnostics on a crash
for suffix in %{build_loop} ; do

# portable builds have static_libs embedded, thus top_dir_abs_main_build_path is same as  top_dir_abs_staticlibs_build_path
top_dir_abs_main_build_path=$(pwd)/%{installoutputdir -- ${suffix}}
%if %{include_staticlibs}
top_dir_abs_staticlibs_build_path=${top_dir_abs_main_build_path}
%endif

export JAVA_HOME=${top_dir_abs_main_build_path}/images/%{jdkimage}

# Pre-test setup

# System security properties are disabled by default on portable.
# Turn on system security properties
#sed -i -e "s:^security.useSystemPropertiesFile=.*:security.useSystemPropertiesFile=true:" \
#${JAVA_HOME}/conf/security/java.security

# Check Shenandoah is enabled
%if %{use_shenandoah_hotspot}
$JAVA_HOME/bin/java -XX:+UnlockExperimentalVMOptions -XX:+UseShenandoahGC -version
%endif

# Check unlimited policy has been used
$JAVA_HOME/bin/javac -d . %{SOURCE13}
$JAVA_HOME/bin/java --add-opens java.base/javax.crypto=ALL-UNNAMED TestCryptoLevel

# Check ECC is working
$JAVA_HOME/bin/javac -d . %{SOURCE14}
$JAVA_HOME/bin/java $(echo $(basename %{SOURCE14})|sed "s|\.java||")

# Check system crypto (policy) is active and can be disabled
# Test takes a single argument - true or false - to state whether system
# security properties are enabled or not.
$JAVA_HOME/bin/javac -d . %{SOURCE15}
export PROG=$(echo $(basename %{SOURCE15})|sed "s|\.java||")
export SEC_DEBUG="-Djava.security.debug=properties"
# Specific to portable:System security properties to be off by default
$JAVA_HOME/bin/java ${SEC_DEBUG} ${PROG} false
$JAVA_HOME/bin/java ${SEC_DEBUG} -Djava.security.disableSystemPropertiesFile=true ${PROG} false

# Check correct vendor values have been set
$JAVA_HOME/bin/javac -d . %{SOURCE16}
$JAVA_HOME/bin/java $(echo $(basename %{SOURCE16})|sed "s|\.java||") "%{oj_vendor}" "%{oj_vendor_url}" "%{oj_vendor_bug_url}" "%{oj_vendor_version}"

# Check java launcher has no SSB mitigation
if ! nm $JAVA_HOME/bin/java | grep set_speculation ; then true ; else false; fi

# Check alt-java launcher has SSB mitigation on supported architectures
%ifarch %{ssbd_arches}
nm $JAVA_HOME/bin/%{alt_java_name} | grep set_speculation
%else
if ! nm $JAVA_HOME/bin/%{alt_java_name} | grep set_speculation ; then true ; else false; fi
%endif

%if ! 0%{?flatpak}
# Check translations are available for new timezones (during flatpak builds, the
# tzdb.dat used by this test is not where the test expects it, so this is
# disabled for flatpak builds)
# Disable test until we are on the latest JDK
$JAVA_HOME/bin/javac -d . %{SOURCE18}
$JAVA_HOME/bin/java $(echo $(basename %{SOURCE18})|sed "s|\.java||") JRE
$JAVA_HOME/bin/java -Djava.locale.providers=CLDR $(echo $(basename %{SOURCE18})|sed "s|\.java||") CLDR
%endif

%if %{include_staticlibs}
# Check debug symbols in static libraries (smoke test)
export STATIC_LIBS_HOME=${top_dir_abs_staticlibs_build_path}/images/%{static_libs_image}
ls -l $STATIC_LIBS_HOME
ls -l $STATIC_LIBS_HOME/lib
readelf --debug-dump $STATIC_LIBS_HOME/lib/libnet.a | grep Inet4AddressImpl.c
readelf --debug-dump $STATIC_LIBS_HOME/lib/libnet.a | grep Inet6AddressImpl.c
%endif

# Release builds strip the debug symbols into external .debuginfo files
if [ "x$suffix" = "x" ] ; then
  so_suffix="debuginfo"
else
  so_suffix="so"
fi
# Check debug symbols are present and can identify code
find "$JAVA_HOME" -iname "*.$so_suffix" -print0 | while read -d $'\0' lib
do
  if [ -f "$lib" ] ; then
    echo "Testing $lib for debug symbols"
    # All these tests rely on RPM failing the build if the exit code of any set
    # of piped commands is non-zero.

    # Test for .debug_* sections in the shared object. This is the main test
    # Stripped objects will not contain these
    eu-readelf -S "$lib" | grep "] .debug_"
    test $(eu-readelf -S "$lib" | grep -E "\]\ .debug_(info|abbrev)" | wc --lines) == 2

    # Test FILE symbols. These will most likely be removed by anything that
    # manipulates symbol tables because it's generally useless. So a nice test
    # that nothing has messed with symbols
    old_IFS="$IFS"
    IFS=$'\n'
    for line in $(eu-readelf -s "$lib" | grep "00000000      0 FILE    LOCAL  DEFAULT")
    do
     # We expect to see .cpp and .S files, except for architectures like aarch64 and
     # s390 where we expect .o and .oS files
      echo "$line" | grep -E "ABS ((.*/)?[-_a-zA-Z0-9]+\.(c|cc|cpp|cxx|o|S|oS))?$"
    done
    IFS="$old_IFS"

    # If this is the JVM, look for javaCalls.(cpp|o) in FILEs, for extra sanity checking
    if [ "`basename $lib`" = "libjvm.so" ]; then
      eu-readelf -s "$lib" | \
        grep -E "00000000      0 FILE    LOCAL  DEFAULT      ABS javaCalls.(cpp|o)$"
    fi

    # Test that there are no .gnu_debuglink sections pointing to another
    # debuginfo file. There shouldn't be any debuginfo files, so the link makes
    # no sense either
    eu-readelf -S "$lib" | grep 'gnu'
    if eu-readelf -S "$lib" | grep '] .gnu_debuglink' | grep PROGBITS; then
      echo "bad .gnu_debuglink section."
      eu-readelf -x .gnu_debuglink "$lib"
      false
    fi
  fi
done

# Make sure gdb can do a backtrace based on line numbers on libjvm.so
# javaCalls.cpp:58 should map to:
# http://hg.openjdk.java.net/jdk8u/jdk8u/hotspot/file/ff3b27e6bcc2/src/share/vm/runtime/javaCalls.cpp#l58
# Using line number 1 might cause build problems. See:
# https://bugzilla.redhat.com/show_bug.cgi?id=1539664
# https://bugzilla.redhat.com/show_bug.cgi?id=1538767
gdb -q "$JAVA_HOME/bin/java" <<EOF | tee gdb.out
handle SIGSEGV pass nostop noprint
handle SIGILL pass nostop noprint
set breakpoint pending on
break javaCalls.cpp:58
commands 1
backtrace
quit
end
run -version
EOF
%ifarch %{gdb_arches}
grep 'JavaCallWrapper::JavaCallWrapper' gdb.out
%endif

# Check src.zip has all sources. See RHBZ#1130490
unzip -l $JAVA_HOME/lib/src.zip | grep 'sun.misc.Unsafe'

# Check class files include useful debugging information
$JAVA_HOME/bin/javap -l java.lang.Object | grep "Compiled from"
$JAVA_HOME/bin/javap -l java.lang.Object | grep LineNumberTable
$JAVA_HOME/bin/javap -l java.lang.Object | grep LocalVariableTable

# Check generated class files include useful debugging information
$JAVA_HOME/bin/javap -l java.nio.ByteBuffer | grep "Compiled from"
$JAVA_HOME/bin/javap -l java.nio.ByteBuffer | grep LineNumberTable
$JAVA_HOME/bin/javap -l java.nio.ByteBuffer | grep LocalVariableTable

# build cycles check
done

%install

for suffix in %{build_loop} ; do

    packagesdir=%{packageoutputdir -- ${suffix}}

    if [ "x$suffix" == "x" ] ; then
        nameSuffix=""
    else
        nameSuffix=`echo "$suffix"| sed s/-/./`
    fi

    # These definitions should match those in installjdk
    jdkarchive=${packagesdir}/%{jdkportablearchive -- "$nameSuffix"}
    jrearchive=${packagesdir}/%{jreportablearchive -- "$nameSuffix"}
    staticarchive=${packagesdir}/%{staticlibsportablearchive -- "$nameSuffix"}
    debugarchive=${packagesdir}/%{jdkportablearchive -- "${nameSuffix}.debuginfo"}
    unstrippedarchive=${packagesdir}/%{jdkportablearchive -- "${nameSuffix}.unstripped"}

    mkdir -p $RPM_BUILD_ROOT%{_jvmdir}

    mv ${jdkarchive} $RPM_BUILD_ROOT%{_jvmdir}/
    mv ${jdkarchive}.sha256sum $RPM_BUILD_ROOT%{_jvmdir}/
    mv ${jrearchive} $RPM_BUILD_ROOT%{_jvmdir}/
    mv ${jrearchive}.sha256sum $RPM_BUILD_ROOT%{_jvmdir}/

%if %{include_staticlibs}
    mv ${staticarchive} $RPM_BUILD_ROOT%{_jvmdir}/
    mv ${staticarchive}.sha256sum $RPM_BUILD_ROOT%{_jvmdir}/
%endif

    if [ "x$suffix" = "x" ] ; then
        mv ${debugarchive} $RPM_BUILD_ROOT%{_jvmdir}/
        mv ${debugarchive}.sha256sum $RPM_BUILD_ROOT%{_jvmdir}/
        mv ${unstrippedarchive} $RPM_BUILD_ROOT%{_jvmdir}/
        mv ${unstrippedarchive}.sha256sum $RPM_BUILD_ROOT%{_jvmdir}/
    fi
done

# These definitions should match those in installjdk
# Install outside the loop as there are no debug variants
docarchive=${packagesdir}/%{docportablearchive}
miscarchive=${packagesdir}/%{miscportablearchive}

mv ${docarchive} $RPM_BUILD_ROOT%{_jvmdir}/
mv ${docarchive}.sha256sum $RPM_BUILD_ROOT%{_jvmdir}/
mv ${miscarchive} $RPM_BUILD_ROOT%{_jvmdir}/
mv ${miscarchive}.sha256sum $RPM_BUILD_ROOT%{_jvmdir}/

# To show sha in the build log
for file in `ls $RPM_BUILD_ROOT%{_jvmdir}/*.sha256sum` ; do
    ls -l $file ;
    cat $file ;
done

%if %{include_normal_build}

%files
# main package builds always
%{_jvmdir}/%{jreportablearchive -- %%{nil}}
%{_jvmdir}/%{jreportablearchive -- %%{nil}}.sha256sum
%else
%files
# placeholder
%endif

%files devel
%{_jvmdir}/%{jdkportablearchive -- %%{nil}}
%{_jvmdir}/%{jdkportablearchive -- .debuginfo}
%{_jvmdir}/%{jdkportablearchive -- %%{nil}}.sha256sum
%{_jvmdir}/%{jdkportablearchive -- .debuginfo}.sha256sum

%if %{include_staticlibs}
%files static-libs
%{_jvmdir}/%{staticlibsportablearchive -- %%{nil}}
%{_jvmdir}/%{staticlibsportablearchive -- %%{nil}}.sha256sum
%endif

%files unstripped
%{_jvmdir}/%{jdkportablearchive -- .unstripped}
%{_jvmdir}/%{jdkportablearchive -- .unstripped}.sha256sum

%if %{include_debug_build}

%files slowdebug
%{_jvmdir}/%{jreportablearchive -- .slowdebug}
%{_jvmdir}/%{jreportablearchive -- .slowdebug}.sha256sum

%files devel-slowdebug
%{_jvmdir}/%{jdkportablearchive -- .slowdebug}
%{_jvmdir}/%{jdkportablearchive -- .slowdebug}.sha256sum

%if %{include_staticlibs}
%files static-libs-slowdebug
%{_jvmdir}/%{staticlibsportablearchive -- .slowdebug}
%{_jvmdir}/%{staticlibsportablearchive -- .slowdebug}.sha256sum
%endif

%endif

%if %{include_fastdebug_build}

%files fastdebug
%{_jvmdir}/%{jreportablearchive -- .fastdebug}
%{_jvmdir}/%{jreportablearchive -- .fastdebug}.sha256sum

%files devel-fastdebug
%{_jvmdir}/%{jdkportablearchive -- .fastdebug}
%{_jvmdir}/%{jdkportablearchive -- .fastdebug}.sha256sum

%if %{include_staticlibs}
%files static-libs-fastdebug
%{_jvmdir}/%{staticlibsportablearchive -- .fastdebug}
%{_jvmdir}/%{staticlibsportablearchive -- .fastdebug}.sha256sum
%endif

%endif

%files docs
%{_jvmdir}/%{docportablearchive}
%{_jvmdir}/%{docportablearchive}.sha256sum

%files misc
%{_jvmdir}/%{miscportablearchive}
%{_jvmdir}/%{miscportablearchive}.sha256sum

%changelog
* Wed Apr 10 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.9-3
- BuildRequires tzdata-java >= 2024a (JDK-8325150)

* Wed Apr 10 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.9-2
- NEWS: Add CVEs
- NEWS: Remove backed out items from changes section
- NEWS: Remove release note for JDK-8225377, which was backed out

* Tue Apr  9 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.9-1
- Update to jdk-17.0.11+9 (GA)
- Update NEWS for 17.0.11+9
- Switch to GA mode for release
- ** This tarball is embargoed until 2024-04-16 @ 1pm PT. **

* Thu Apr  4 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.7-0.1.ea
- Import like NEWS entries verbatim from 21.0.3

* Thu Mar 28 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.7-0.1.ea
- Update to jdk-17.0.11+7 (EA)

* Mon Mar 11 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.6-0.1.ea
- Update to jdk-17.0.11+6 (EA)

* Fri Mar  8 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.5-0.1.ea
- Update to jdk-17.0.11+5 (EA)

* Mon Feb 26 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.4-0.1.ea
- Revert: Remove ExcludeArch to match java-21-openjdk

* Wed Feb 21 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.4-0.1.ea
- Update to jdk-17.0.11+4 (EA)

* Wed Feb 14 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.3-0.1.ea
- Update to jdk-17.0.11+3 (EA)

* Fri Feb  9 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.2-0.1.ea
- Remove RH1649512 patch for libjpeg-turbo FAR macro
- Add some patch commentary

* Thu Feb  8 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.2-0.1.ea
- Update to jdk-17.0.11+2 (EA)

* Thu Feb  8 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.1-0.2.ea
- generate_source_tarball.sh: Add license
- openjdk_news.sh: Use grep -E instead of egrep

* Wed Feb  7 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.1-0.2.ea
- Fix the quoting of hs_err_pid

* Tue Feb  6 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.1-0.2.ea
- Use RHEL-7 tar-1.26-compatible invocations for reproducible tarballs
- On RHEL-7 default to building without a fresh libjvm.so

* Mon Feb  5 2024 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.11.0.1-0.2.ea
- Require tzdata 2023d due to local inclusion of JDK-8322725

* Mon Feb  5 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.1-0.2.ea
- Bump rpmrelease to 2
- Move _lto_cflags setting to match its java-21-openjdk location
- Remove ExcludeArch to match java-21-openjdk
- Update comment and whitespace to match java-21-openjdk
- Update NEWS
- Remove -T0 argument from systemtap tar invocation
- Indent a line in buildjdk
- Remove extra stripjdk from merge

* Fri Feb  2 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.1-0.1.ea
- Use --with-source-date=version (OPENJDK-2583, OPENJDK-2730)
- Update freetype bundled provides version from 2.13.0 to 2.13.2
- Update harfbuzz bundled provides version from 7.2.0 to 8.2.2
- Update libpng bundled provides version from 1.6.39 to 1.6.40
- Related: OPENJDK-2730

* Thu Feb  1 2024 Jiri Vanek <jvanek@redhat.com> - 1:17.0.11.0.1-0.1.ea
- generate_source_tarball.sh: Update version in comment
- generate_source_tarball.sh: Remove trailing period in echo

* Thu Feb  1 2024 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.11.0.1-0.1.ea
- BuildRequires javapackages-filesystem for _jvmdir macro
- Automatically turn off building a fresh HotSpot first, if the bootstrap JDK is not the same major version as that being built
- Update buildjdkver to match the featurever
- Use featurever macro to specify fips patch
- Check debug symbols in libnet.a static library as a smoke test
- Introduce vm_variant global for consistency with future JDK builds
- Related: rhbz#2203412
- Introduce tar_opts to shorten tarball creation lines

* Thu Feb  1 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.1-0.1.ea
- NEWS: Add initial changes for 17.0.11
- Sync whitespace and comments from java-21-openjdk.spec
- Sync macro definition ordering from java-21-openjdk.spec
- Correct rh1649512 patch name
- Fix comment to match RHEL 9.2.0 branch
- Fix icedteaver macro reference syntax
- Remove extra slash in use_shenandoah_hotspot JAVA_HOME expansion
- Explain patchN syntax situation in a comment
- generate_source_tarball.sh: Fix whitespace
- generate_source_tarball.sh: Skip -ga tags
- generate_source_tarball.sh: Get -ea suffix from version-numbers.conf
- generate_source_tarball.sh: Use git archive to generate tarball
- generate_source_tarball.sh: Add indentation instructions for Emacs
- Default to without fresh_libjvm now that 17.0.9.0.9-1 is staged
- double-build.bash: New file
- Parallelize xz across all available cores
- Remove ppc64le --with-jobs=1 workaround
- Make JAR file and portable tarball modification times reproducible

* Wed Jan 31 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.1-0.1.ea
- Update to jdk-17.0.11+1 (EA)

* Thu Jan 11 2024 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.10.0.7-1
- Update to jdk-17.0.10+7 (GA)
- Update release notes to 17.0.10+7
- Move to -P<n> usage for patch macro which works on all RPM versions
- Re-enable DEFAULT_PROMOTED_VERSION_PRE check disabled for the July 2023 release
- Switch to GA mode for release
- ** This tarball is embargoed until 2024-01-16 @ 1pm PT. **

* Thu Jan 11 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.10.0.6-0.1.ea
- generate_source_tarball.sh: Add note on network usage of OPENJDK_LATEST
- generate_source_tarball.sh: Remove unneeded fix-me

* Thu Jan 11 2024 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.10.0.6-0.1.ea
- Update release notes to 17.0.10+6
- Revert change to patch macro due to failure on RHEL 8
- generate_source_tarball.sh: Add --sort=name to tar invocation for reproducibility

* Tue Jan  9 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.10.0.6-0.1.ea
- Update to jdk-17.0.10+6 (EA)
- fips-17u-d63771ea660.patch: Regenerate from gnu-andrew branch
- generate_source_tarball.sh: Add WITH_TEMP environment variable
- generate_source_tarball.sh: Multithread xz on all available cores
- generate_source_tarball.sh: Add OPENJDK_LATEST environment variable
- generate_source_tarball.sh: Update comment about tarball naming
- generate_source_tarball.sh: Remove REPO_NAME from FILE_NAME_ROOT
- generate_source_tarball.sh: Set compile-command in Emacs
- generate_source_tarball.sh: Reformat comment header
- generate_source_tarball.sh: Reformat and update help output
- generate_source_tarball.sh: Move PROJECT_NAME and REPO_NAME checks
- generate_source_tarball.sh: Do a shallow clone, for speed
- generate_source_tarball.sh: Append -ea designator when required
- generate_source_tarball.sh: Eliminate some removal prompting
- generate_source_tarball.sh: Make tarball reproducible
- generate_source_tarball.sh: Prefix temporary directory with temp-
- generate_source_tarball.sh: shellcheck: Remove x-prefixes since we use Bash
- generate_source_tarball.sh: shellcheck: Double-quote variable references
- generate_source_tarball.sh: shellcheck: Do not use -a
- generate_source_tarball.sh: shellcheck: Do not use $ in expression
- generate_source_tarball.sh: Remove temporary directory exit conditions

* Sat Oct 28 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.9.0.9-2
- Add missing CVE and release note to sync local NEWS with upstream release announcements

* Thu Oct 12 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.9.0.9-1
- Update to jdk-17.0.9+9 (GA)
- Update release notes to 17.0.9+9
- Re-generate FIPS patch against 17.0.9+1 following backport of JDK-8209398
- Bump libpng version to 1.6.39 following JDK-8305815
- Bump HarfBuzz version to 7.2.0 following JDK-8307301
- Bump freetype version to 2.13.0 following JDK-8306881
- Update generate_tarball.sh to be closer to upstream vanilla script inc. no more ECC removal
- Sync generate_tarball.sh with 11u version
- Update bug URL for RHEL to point to the Red Hat customer portal
- Change top_level_dir_name to use the VCS tag, matching new upstream release style tarball
- Use upstream release URL for OpenJDK source
- Apply all patches using -p1
- Temporarily turn off 'fresh_libjvm' due to removal of JVM_IsThreadAlive (JDK-8305425)
- ** This tarball is embargoed until 2023-10-17 @ 1pm PT. **

* Sat Sep 02 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.8.1.1-1
- Update to jdk-17.0.8.1+1 (GA)
- Update release notes to 17.0.8.1+1
- Add backport of JDK-8312489 already upstream in 17.0.10 (see OPENJDK-2095)
- Update openjdk_news script to specify subdirectory last
- Add missing discover_trees script required by openjdk_news

* Fri Jul 14 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.8.0.7-1
- Update to jdk-17.0.8+7 (GA)
- Update release notes to 17.0.8+7
- Switch to GA mode for final release.
- * This tarball is embargoed until 2023-07-18 @ 1pm PT. *

* Thu Jul 13 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.8.0.6-0.1.ea
- Update to jdk-17.0.8+6 (EA)
- Update release notes to 17.0.8+6

* Thu Jul 13 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.8.0.1-0.3.ea
- Make sure the unstripped JDK is customised by the installjdk function

* Wed Jul 12 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.8.0.1-0.2.ea
- Rebuild jmods using the stripped binaries in release builds
- Resolves: OPENJDK-1974

* Tue Jul 04 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.8.0.1-0.1.ea
- Use absolute path to tapset directory
- Drop unused globals for tapset installation

* Tue Jul 04 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.8.0.1-0.1.ea
- Re-enable SystemTap support and perform only substitutions possible without final NVR available
- Depend on graphviz & pandoc for full documentation support
- Fix typo which stops the EA designator being included in the build
- Include tapsets in the miscellaneous tarball

* Mon Jul 03 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.8.0.1-0.1.ea
- Update to jdk-17.0.8+1 (EA)
- Update release notes to 17.0.8+1
- Switch to EA mode
- Drop local inclusion of JDK-8274864 & JDK-8305113 as they are included in 17.0.8+1
- Bump bundled LCMS version to 2.15 as in jdk-17.0.8+1.
- Bump bundled HarfBuzz version to 7.0.1 as in jdk-17.0.8+1

* Tue Apr 25 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.7.0.7-2
- Update to jdk-17.0.7.0+7
- Update release notes to 17.0.7.0+7
- Require tzdata 2023c due to local inclusion of JDK-8274864 & JDK-8305113
- Reintroduce generate_source_tarball.sh from RHEL 9
- Update generate_tarball.sh to add support for passing a boot JDK to the configure run
- Add POSIX-friendly error codes to generate_tarball.sh and fix whitespace
- Remove .jcheck and GitHub support when generating tarballs, as done in upstream release tarballs
- Update FIPS support against 17.0.7+6 and bring in latest changes:
- * RH2134669: Add missing attributes when registering services in FIPS mode.
- * test/jdk/sun/security/pkcs11/fips/VerifyMissingAttributes.java: fixed jtreg main class
- * RH1940064: Enable XML Signature provider in FIPS mode
- * RH2173781: Avoid calling C_GetInfo() too early, before cryptoki is initialized
- Fix trailing '.' in tarball name
- Use rpmrelease in vendor version to avoid inclusion of dist tag
- ** This tarball is embargoed until 2023-04-18 @ 1pm PT. **
- Resolves: rhbz#2185182
- Resolves: rhbz#2134669
- Resolves: rhbz#1940064
- Resolves: rhbz#2173781

* Thu Apr 20 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.6.0.10-7
- Sync with existing RHEL 8 build, in order to start building portables on RHEL 8
- Restore system bootstrap JDK (RHEL 8 has java-17-openjdk)
- Remove use of devtoolset (RHEL 8 native compilers should be sufficient)
- Explicitly exclude x86, as on RHEL RPMs

* Tue Feb 21 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.6.0.10-6
- Add docs, icons and samples to the portable output
- Make sure generated checksums work and don't include full path
- The docs directory is a subdirectory of images, so remove confusing separate copying

* Wed Feb 15 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.6.0.10-5
- Build with internal debuginfo as in RHEL and then create a stripped variant ourselves for the portable release build
- Restore compiler flags to those used in RHEL
- Drop unused static library patch
- Drop syslookup workaround which was fixed by JDK-8276572 over a year ago

* Tue Feb 14 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.6.0.10-4
- Separate JDK packaging into a separate function
- Use variables to make it clearer what is going on
- Use a package output directory as we do for building and installing
- Workaround missing manpage directory in the JRE image

* Sun Feb 12 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.6.0.10-3
- Adapt the portable build to use the same system library handling as RHEL builds

* Sat Jan 14 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.6.0.10-3
- Add missing release note for JDK-8295687
- Resolves: rhbz#2160111

* Fri Jan 13 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.6.0.10-2
- Update FIPS support to bring in latest changes
- * Add nss.fips.cfg support to OpenJDK tree
- * RH2117972: Extend the support for NSS DBs (PKCS11) in FIPS mode
- * Remove forgotten dead code from RH2020290 and RH2104724
- * OJ1357: Fix issue on FIPS with a SecurityManager in place
- Drop local nss.fips.cfg.in handling now this is handled in the patched OpenJDK build
- Resolves: rhbz#2118493

* Fri Jan 13 2023 Stephan Bergmann <sbergman@redhat.com> - 1:17.0.6.0.10-2
- Fix flatpak builds by disabling TestTranslations test due to missing tzdb.dat
- Related: rhbz#2160111

* Wed Jan 11 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.6.0.10-1
- Update to jdk-17.0.6.0+10
- Update release notes to 17.0.6.0+10
- Re-enable EA upstream status check now it is being actively maintained.
- Drop JDK-8294357 (tzdata2022d) & JDK-8295173 (tzdata2022e) local patches which are now upstream
- Drop JDK-8275535 local patch now this has been accepted and backported upstream
- Drop local copy of JDK-8293834 now this is upstream
- Require tzdata 2022g due to inclusion of JDK-8296108, JDK-8296715 & JDK-8297804
- Update TestTranslations.java to test the new America/Ciudad_Juarez zone
- ** This tarball is embargoed until 2023-01-17 @ 1pm PT. **
- Resolves: rhbz#2160111

* Sat Oct 15 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.5.0.8-2
- Update in-tree tzdata to 2022e with JDK-8294357 & JDK-8295173
- Update CLDR data with Europe/Kyiv (JDK-8293834)
- Drop JDK-8292223 patch which we found to be unnecessary
- Update TestTranslations.java to use public API based on TimeZoneNamesTest upstream
- Related: rhbz#2160111

* Thu Oct 13 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.5.0.8-1
- Update to jdk-17.0.5+8 (GA)
- Update release notes to 17.0.5+8 (GA)
- Switch to GA mode for final release.
- * This tarball is embargoed until 2022-10-18 @ 1pm PT. *
- Resolves: rhbz#2133695

* Fri Sep 02 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.4.1.1-2
- Update FIPS support to bring in latest changes
- * RH2023467: Enable FIPS keys export
- * RH2104724: Avoid import/export of DH private keys
- * RH2092507: P11Key.getEncoded does not work for DH keys in FIPS mode
- * Build the systemconf library on all platforms
- * RH2048582: Support PKCS#12 keystores
- * RH2020290: Support TLS 1.3 in FIPS mode
- Resolves: rhbz#2123579
- Resolves: rhbz#2123580
- Resolves: rhbz#2123581
- Resolves: rhbz#2123583
- Resolves: rhbz#2123584

* Sun Aug 21 2022 Jayashree Huttanagoudar <jhuttana@redhat.com> - 1:17.0.4.1.1-1
- Added a missing change to portable NEWS file from upstream.

* Sun Aug 21 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.4.1.1-1
- Update to jdk-17.0.4.1+1
- Update release notes to 17.0.4.1+1
- Add patch to provide translations for Europe/Kyiv added in tzdata2022b
- Add test to ensure timezones can be translated
- Resolves: rhbz#2119532

* Mon Jul 18 2022 Jayashree Huttanagoudar <jhuttana@redhat.com> - 1:17.0.4.0.8-1
- Commented out: fipsver f8142a23d0a which was from rhel-9-main
- Picked 17.0.4+8 GA tag from rhel-9.0.0
- For Jul 2022 CPU fipsver is 765f970aef1 on rhel-9.0.0

* Mon Jul 18 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.4.0.8-1
- Update to jdk-17.0.4.0+8 (GA)
- Update release notes to 17.0.4.0+8
- Need to include the '.S' suffix in debuginfo checks after JDK-8284661
- Switch to GA mode for release
- ** This tarball is embargoed until 2022-07-19 @ 1pm PT. **

* Thu Jul 14 2022 Jayashree Huttanagoudar <jhuttana@redhat.com> - 1:17.0.4.0.1-0.2.ea
- Fix issue where CheckVendor.java test erroneously passes when it should fail.
- Add proper quoting so '&' is not treated as a special character by the shell.
- Related: rhbz#2084779

* Tue Jul 12 2022 Jayashree Huttanagoudar <jhuttana@redhat.com> - 1:17.0.4.0.1-0.1.ea
- Tweaked line to print release information for portable

* Tue Jul 12 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.4.0.1-0.1.ea
- Update to jdk-17.0.4.0+1
- Update release notes to 17.0.4.0+1
- Switch to EA mode for 17.0.4 pre-release builds.
- Print release file during build, which should now include a correct SOURCE value from .src-rev
- Update tarball script with IcedTea GitHub URL and .src-rev generation
- Include script to generate bug list for release notes
- Update tzdata requirement to 2022a to match JDK-8283350
- Move EA designator check to prep so failures can be caught earlier
- Make EA designator check non-fatal while upstream is not maintaining it
- Related: rhbz#2084218

* Thu Jun 30 2022 Jayashree Huttanagoudar <jhuttana@redhat.com> - 1:17.0.3.0.7-8
- Comment line for portable: System security properties to be off by default

* Thu Jun 30 2022 Francisco Ferrari Bihurriet <fferrari@redhat.com> - 1:17.0.3.0.7-8
- RH2007331: SecretKey generate/import operations don't add the CKA_SIGN attribute in FIPS mode
- Resolves: rhbz#2102433

* Wed Jun 29 2022 Jayashree Huttanagoudar <jhuttana@redhat.com> - 1:17.0.3.0.7-7
- System security properties are disabled by default on portable.
- Commented out lines which are not applicable for portable.

* Wed Jun 29 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.3.0.7-7
- Update FIPS support to bring in latest changes
- * RH2036462: sun.security.pkcs11.wrapper.PKCS11.getInstance breakage
- * RH2090378: Revert to disabling system security properties and FIPS mode support together
- Rebase RH1648249 nss.cfg patch so it applies after the FIPS patch
- Enable system security properties in the RPM (now disabled by default in the FIPS repo)
- Improve security properties test to check both enabled and disabled behaviour
- Run security properties test with property debugging on
- Resolves: rhbz#2099844
- Resolves: rhbz#2100677

* Tue Jun 28 2022 Jayashree Huttanagoudar <jhuttana@redhat.com> - 1:17.0.3.0.7-6
- Removed upstreamed patch2001: aqaCheckSecurityAndProviderFileSocketPermissions.patch

* Sun Jun 12 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.3.0.7-6
- Rebase FIPS patches from fips-17u branch and simplify by using a single patch from that repository
- Rebase RH1648249 nss.cfg patch so it applies after the FIPS patch
- RH2023467: Enable FIPS keys export
- RH2094027: SunEC runtime permission for FIPS
- Resolves: rhbz#2029657
- Resolves: rhbz#2096117

* Wed May 25 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.3.0.7-5
- Exclude s390x from the gdb test on RHEL 7 where we see failures with the portable build

* Tue May 24 2022 Jiri Vanek <jvanek@redhat.com> - 1:17.0.3.0.7-4
- to pass aqa, fixing genuie failure in :
- java/lang/SecurityManager/CheckAccessClassInPackagePermissions.java#CheckAccessClassInPackagePermissions
- javax/xml/crypto/dsig/FileSocketPermissions.java#FileSocketPermissions
- added and applied patch2001: aqaCheckSecurityAndProviderFileSocketPermissions.patch
- this, properly named, patch must go to all our jdk17 builds, and to the fips repo

* Thu May 19 2022 Jiri Vanek <jvanek@redhat.com> - 1:17.0.3.0.7-3
- to pass aqa:
- removed copy system tzdb in favour of in-tree
- removed Patch2: rh1648644-java_access_bridge_privileged_security.patch
- This is not intended to release untill we decide proper steps

* Thu May 19 2022 Jayashree Huttanagoudar <jhuttana@redhat.com> - 1:17.0.3.0.7-2
- Include BOOT_JDK for s390x for portable
- BOOT_JDK downlaoded form hydra as
  java-17-temurin-17.0.3.7-0.private.ojdk17~upstream.hotspot.release.sdk.el7.s390x.tarxz
  and renamed
- Added cosmetic changes to bypass a failure for s390x

* Wed Apr 20 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.3.0.7-1
- April 2022 security update to jdk 17.0.3+7
- Remove JDK-8284548 and JDK-8284920 they are upstreamed now
- Resolves: rhbz#2073579

* Sat Apr 16 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.3.0.6-3
- Add JDK-8284920 fix for XPath regression
- Related: rhbz#2073575

* Fri Apr 15 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.3.0.6-2
- Remove the patch jdk8283911-default_promoted_version_pre.patch which missed in previous commit
- JDK-8275082 should be listed as also resolving JDK-8278008 & CVE-2022-21476
- Related: rhbz#2073575

* Mon Apr 11 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.3.0.6-1
- April 2022 security update to jdk 17.0.3+6
- Update to jdk-17.0.3.0+6 pre-release tarball (17usec.17.0.3+5-220408)
- Add JDK-8284548 regression fix missing from pre-release tarball but in jdk-17.0.3+6/jdk-17.0.3-ga
- Update release notes to 17.0.3.0+6
- Add missing README.md and generate_source_tarball.sh
- Introduce tests/tests.yml, based on the one in java-11-openjdk
- JDK-8283911 patch no longer needed now we're GA...
- Switch to GA mode for release
- ** This tarball is embargoed until 2022-04-19 @ 1pm PT. **
- Resolves: rhbz#2073575

* Wed Apr 06 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.3.0.5-0.1.ea
- Update to jdk-17.0.3.0+5
- Update release notes to 17.0.3.0+5
- Resolves: rhbz#2050460

* Tue Mar 29 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.3.0.1-0.1.ea
- Update to jdk-17.0.3.0+1
- Update release notes to 17.0.3.0+1
- Switch to EA mode for 17.0.3 pre-release builds.
- Add JDK-8283911 to fix bad DEFAULT_PROMOTED_VERSION_PRE value
- Related: rhbz#2050456

* Mon Feb 28 2022 Jayashree Huttanagoudar <jhuttana@redhat.com> - 1:17.0.2.0.8-10
- Update icedtea_sync.sh with suitable message for portable

* Mon Feb 28 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.2.0.8-10
- Restructure the build so a minimal initial build is then used for the final build (with docs)
- This reduces pressure on the system JDK and ensures the JDK being built can do a full build
- Turn off bootstrapping for slow debug builds, which are particularly slow on ppc64le.
- Handle Fedora in distro conditionals that currently only pertain to RHEL.
- Run OpenJDK normalizer script on the spec file to fix further rogue whitespace
- Sync gdb test with java-1.8.0-openjdk and improve architecture restrictions.
- Introduce stapinstall variable to set SystemTap arch directory correctly (e.g. arm64 on aarch64)
- Need to support noarch for creating source RPMs for non-scratch builds.
- Replace -mstackrealign with -mincoming-stack-boundary=2 -mpreferred-stack-boundary=4 on x86_32 for stack alignment
- Support a HotSpot-only build so a freshly built libjvm.so can then be used in the bootstrap JDK.
- Explicitly list JIT architectures rather than relying on those with slowdebug builds
- Disable the serviceability agent on Zero architectures even when the architecture itself is supported
- Resolves: rhbz#2022822

* Mon Feb 28 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.2.0.8-9
- Enable AlgorithmParameters and AlgorithmParameterGenerator services in FIPS mode
- Correction to previous changelog entry
- Resolves: rhbz#2052070

* Sun Feb 27 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.2.0.8-8
- Detect NSS at runtime for FIPS detection
- Resolves: rhbz#2051605

* Wed Feb 23 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.2.0.8-7
- Add JDK-8275535 patch to fix LDAP authentication issue.
- Resolves: rhbz#2053521

* Tue Feb 08 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.2.0.8-6
- Minor cosmetic improvements to make spec more comparable between variants
- Related: rhbz#2022822

* Thu Feb 03 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.2.0.8-5
- Update tapsets from IcedTea 6.x repository with fix for JDK-8015774 changes (_heap->_heaps) and @JAVA_SPEC_VER@
- Related: rhbz#2022822

* Thu Feb 03 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.2.0.8-4
- Extend LTS check to exclude EPEL.
- Related: rhbz#2022822

* Tue Jan 18 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.2.0.8-3
- Separate crypto policy initialisation from FIPS initialisation, now they are no longer interdependent

* Mon Jan 17 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.2.0.8-2
- Fix FIPS issues in native code and with initialisation of java.security.Security
- Related: rhbz#2039366

* Wed Jan 12 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.2.0.8-1
- January 2022 security update to jdk 17.0.2+8
- Rebase RH1995150 & RH1996182 patches following JDK-8275863 addition to module-info.java
- Resolves: rhbz#2039366
- Minor change to the OUTPUT_FILE value to separate the name from the version with '-'

* Mon Nov 29 2021 Severin Gehwolf <sgehwolf@redhat.com> - 1:17.0.1.0.12-3
- Use 'sql:' prefix in nss.fips.cfg as F35+ no longer ship the legacy
  secmod.db file as part of nss
- Resolves: rhbz#2023537

* Tue Oct 26 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.1.0.12-2
- Drop JDK-8272332/RH2004078 patch which is upstream in 17.0.1
- October CPU update to jdk 17.0.1+12
- Allow plain key import to be disabled with -Dcom.redhat.fips.plainKeySupport=false
- Add patch to allow plain key import.

* Mon Oct 25 2021 Jiri Vanek <jvanek@redhat.com> - 1:17.0.0.0.35-5
- cacerts symlink is resolved before passed to configure
- https://issues.redhat.com/browse/OPENJDK-487
- Disable FIPS mode detection using NSS in favour of using /proc/sys/crypto/fips_enabled for now, so we don't link against NSS
-- effectively disabled Patch1008: rh1929465-improve_system_FIPS_detection.patch by settng --enable-sysconf-nss to --disable-sysconf-nss
-- the enable-sysconf-nss was bringing in hard depndence on nss. Without nss, even in non fips, jvm had not even started

* Thu Sep 30 2021 Jiri Vanek <jvanek@redhat.com> - 1:17.0.0.0.35-4
- initial import, based on jdk11 portbale, merged with jdk17 rpms and java-latest-openjdk for epel7
