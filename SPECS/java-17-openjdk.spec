# To rebuild this RPM, you must first rebuild the portable
# RPM using the java-17-openjdk-portable.specfile, install
# it and then adjust portablerelease and portablesuffix
# to match the new portable.

# RPM conditionals so as to be able to dynamically produce
# slowdebug/release builds. See:
# http://rpm.org/user_doc/conditional_builds.html
#
# Examples:
#
# Produce release, fastdebug *and* slowdebug builds on x86_64 (default):
# $ rpmbuild -ba java-17-openjdk.spec
#
# Produce only release builds (no debug builds) on x86_64:
# $ rpmbuild -ba java-17-openjdk.spec --without slowdebug --without fastdebug
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
%bcond_with fresh_libjvm
# Build with system libraries
%bcond_with system_libs

# Workaround for stripping of debug symbols from static libraries
%if %{with staticlibs}
%define __brp_strip_static_archive %{nil}
%global include_staticlibs 1
%else
%global include_staticlibs 0
%endif

# Define whether to use the bootstrap JDK directly or with a fresh libjvm.so
%if %{with fresh_libjvm}
%global build_hotspot_first 1
%else
%global build_hotspot_first 0
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

# With LTO flags enabled, debuginfo checks fail for some reason. Disable
# LTO for a passing build. This really needs to be looked at.
%define _lto_cflags %{nil}

# note: parametrized macros are order-sensitive (unlike not-parametrized) even with normal macros
# also necessary when passing it as parameter to other macros. If not macro, then it is considered a switch
# see the difference between global and define:
# See https://github.com/rpm-software-management/rpm/issues/127 to comments at  "pmatilai commented on Aug 18, 2017"
# (initiated in https://bugzilla.redhat.com/show_bug.cgi?id=1482192)
%global debug_suffix_unquoted -slowdebug
%global fastdebug_suffix_unquoted -fastdebug
# quoted one for shell operations
%global debug_suffix "%{debug_suffix_unquoted}"
%global fastdebug_suffix "%{fastdebug_suffix_unquoted}"
%global normal_suffix ""

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
# you can list those files, with appropriate sections: cat *.spec | grep -e --install -e --slave -e post_ -e alternatives
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
%global gdb_arches %{jit_arches} %{zero_arches}

# By default, we build a debug build during main build on JIT architectures
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

%if 0%{?flatpak}
%global bootstrap_build false
%else
%ifarch %{bootstrap_arches}
%global bootstrap_build true
%else
%global bootstrap_build false
%endif
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

# RPM JDK builds keep the debug symbols internal, to be later stripped by RPM
%global debug_symbols internal

# unlike portables,the rpms have to use static_libs_target very dynamically
%global bootstrap_targets images
%global release_targets images docs-zip
# No docs nor bootcycle for debug builds
%global debug_targets images
# Target to use to just build HotSpot
%global hotspot_target hotspot

# JDK to use for bootstrapping
%global bootjdk /usr/lib/jvm/java-%{buildjdkver}-openjdk

# VM variant being built
# This is always 'server' on 17u which doesn't have JDK-8273494
%global vm_variant server

# debugedit tool for rewriting ELF file paths
%global debugedit %{_rpmconfigdir}/debugedit

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
%global oj_vendor_version (Red_Hat-%{version}-%{portablerelease})

# Define IcedTea version used for SystemTap tapsets and desktop file
%global icedteaver      6.0.0pre00-c848b93a8598
# Define current Git revision for the FIPS support patches
%global fipsver d63771ea660
%global javaver         %{featurever}
%global newjavaver %{featurever}.%{interimver}.%{updatever}.%{patchver}

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
# rpmrelease numbering must start at 2 to be later than the 8.6 RPM
%global rpmrelease      2
# Settings used by the portable build
%global portablerelease 3
%global portablesuffix el8
%global portablebuilddir /builddir/build/BUILD

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
%define installoutputdir() %{expand:install/jdk%{featurever}.install%{?1}}
# we can copy the javadoc to not arched dir, or make it not noarch
%define uniquejavadocdir()    %{expand:%{fullversion}.%{_arch}%{?1}}
# main id and dir of this jdk
%define uniquesuffix()        %{expand:%{fullversion}.%{_arch}%{?1}}

#################################################################
# fix for https://bugzilla.redhat.com/show_bug.cgi?id=1111349
#         https://bugzilla.redhat.com/show_bug.cgi?id=1590796#c14
#         https://bugzilla.redhat.com/show_bug.cgi?id=1655938
%global _privatelibs libsplashscreen[.]so.*|libawt_xawt[.]so.*|libjli[.]so.*|libattach[.]so.*|libawt[.]so.*|libextnet[.]so.*|libawt_headless[.]so.*|libdt_socket[.]so.*|libfontmanager[.]so.*|libinstrument[.]so.*|libj2gss[.]so.*|libj2pcsc[.]so.*|libj2pkcs11[.]so.*|libjaas[.]so.*|libjavajpeg[.]so.*|libjdwp[.]so.*|libjimage[.]so.*|libjsound[.]so.*|liblcms[.]so.*|libmanagement[.]so.*|libmanagement_agent[.]so.*|libmanagement_ext[.]so.*|libmlib_image[.]so.*|libnet[.]so.*|libnio[.]so.*|libprefs[.]so.*|librmi[.]so.*|libsaproc[.]so.*|libsctp[.]so.*|libsystemconf[.]so.*|libzip[.]so.*%{freetype_lib}
%global _publiclibs libjawt[.]so.*|libjava[.]so.*|libjvm[.]so.*|libverify[.]so.*|libjsig[.]so.*
%if %is_system_jdk
%global __provides_exclude ^(%{_privatelibs})$
%global __requires_exclude ^(%{_privatelibs})$
# Never generate lib-style provides/requires for any debug packages
%global __provides_exclude_from ^.*/%{uniquesuffix -- %{debug_suffix_unquoted}}/.*$
%global __requires_exclude_from ^.*/%{uniquesuffix -- %{debug_suffix_unquoted}}/.*$
%global __provides_exclude_from ^.*/%{uniquesuffix -- %{fastdebug_suffix_unquoted}}/.*$
%global __requires_exclude_from ^.*/%{uniquesuffix -- %{fastdebug_suffix_unquoted}}/.*$
%else
# Don't generate provides/requires for JDK provided shared libraries at all.
%global __provides_exclude ^(%{_privatelibs}|%{_publiclibs})$
%global __requires_exclude ^(%{_privatelibs}|%{_publiclibs})$
%endif


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

%global family %{name}.%{_arch}
%global family_noarch  %{name}

%if %{with_systemtap}
# Where to install systemtap tapset (links)
# We would like these to be in a package specific sub-dir,
# but currently systemtap doesn't support that, so we have to
# use the root tapset dir for now. To distinguish between 64
# and 32 bit architectures we place the tapsets under the arch
# specific dir (note that systemtap will only pickup the tapset
# for the primary arch for now). Systemtap uses the machine name
# aka target_cpu as architecture specific directory name.
%global tapsetroot /usr/share/systemtap
%global tapsetdirttapset %{tapsetroot}/tapset/
%global tapsetdir %{tapsetdirttapset}/%{stapinstall}
%endif

# not-duplicated scriptlets for normal/debug packages
%global update_desktop_icons /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%define save_alternatives() %{expand:
  # warning! alternatives are localised!
  # LANG=cs_CZ.UTF-8  alternatives --display java | head
  # LANG=en_US.UTF-8  alternatives --display java | head
  function nonLocalisedAlternativesDisplayOfMaster() {
    LANG=en_US.UTF-8 alternatives --display "$MASTER"
  }
  function headOfAbove() {
    nonLocalisedAlternativesDisplayOfMaster | head -n $1
  }
  MASTER="%{?1}"
  LOCAL_LINK="%{?2}"
  FAMILY="%{?3}"
  rm -f %{_localstatedir}/lib/rpm-state/"$MASTER"_$FAMILY > /dev/null
  if nonLocalisedAlternativesDisplayOfMaster > /dev/null ; then
      if headOfAbove 1 | grep -q manual ; then
        if headOfAbove 2 | tail -n 1 | grep -q %{compatiblename} ; then
           headOfAbove 2  > %{_localstatedir}/lib/rpm-state/"$MASTER"_"$FAMILY"
        fi
      fi
  fi
}

%define save_and_remove_alternatives() %{expand:
  if [ "x$debug"  == "xtrue" ] ; then
    set -x
  fi
  upgrade1_uninstal0=%{?3}
  if [ "0$upgrade1_uninstal0" -gt 0 ] ; then # removal of this condition will cause persistence between uninstall
    %{save_alternatives %{?1} %{?2} %{?4}}
  fi
  alternatives --remove  "%{?1}" "%{?2}"
}

%define set_if_needed_alternatives() %{expand:
  MASTER="%{?1}"
  FAMILY="%{?2}"
  ALTERNATIVES_FILE="%{_localstatedir}/lib/rpm-state/$MASTER"_"$FAMILY"
  if [ -e  "$ALTERNATIVES_FILE" ] ; then
    rm "$ALTERNATIVES_FILE"
    alternatives --set $MASTER $FAMILY
  fi
}


%define post_script() %{expand:
update-desktop-database %{_datadir}/applications &> /dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
exit 0
}

%define alternatives_java_install() %{expand:
if [ "x$debug"  == "xtrue" ] ; then
  set -x
fi
PRIORITY=%{priority}
if [ "%{?1}" == %{debug_suffix} ]; then
  let PRIORITY=PRIORITY-1
fi

ext=.gz
key=java
alternatives \\
  --install %{_bindir}/java $key %{jrebindir -- %{?1}}/java $PRIORITY  --family %{family} \\
  --slave %{_jvmdir}/jre jre %{_jvmdir}/%{sdkdir -- %{?1}} \\
  --slave %{_bindir}/%{alt_java_name} %{alt_java_name} %{jrebindir -- %{?1}}/%{alt_java_name} \\
  --slave %{_bindir}/jcmd jcmd %{sdkbindir -- %{?1}}/jcmd \\
  --slave %{_bindir}/keytool keytool %{jrebindir -- %{?1}}/keytool \\
  --slave %{_bindir}/rmiregistry rmiregistry %{jrebindir -- %{?1}}/rmiregistry \\
  --slave %{_mandir}/man1/java.1$ext java.1$ext \\
  %{_mandir}/man1/java-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/%{alt_java_name}.1$ext %{alt_java_name}.1$ext \\
  %{_mandir}/man1/%{alt_java_name}-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jcmd.1$ext jcmd.1$ext \\
  %{_mandir}/man1/jcmd-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/keytool.1$ext keytool.1$ext \\
  %{_mandir}/man1/keytool-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/rmiregistry.1$ext rmiregistry.1$ext \\
  %{_mandir}/man1/rmiregistry-%{uniquesuffix -- %{?1}}.1$ext

%{set_if_needed_alternatives $key %{family}}

for X in %{origin} %{javaver} ; do
  key=jre_"$X"
  alternatives --install %{_jvmdir}/jre-"$X" $key %{_jvmdir}/%{sdkdir -- %{?1}} $PRIORITY --family %{family}
  %{set_if_needed_alternatives $key %{family}}
done

key=jre_%{javaver}_%{origin}
alternatives --install %{_jvmdir}/jre-%{javaver}-%{origin} $key %{_jvmdir}/%{jrelnk -- %{?1}} $PRIORITY  --family %{family}
%{set_if_needed_alternatives $key %{family}}
}

%define post_headless() %{expand:
update-desktop-database %{_datadir}/applications &> /dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

# see pretrans where this file is declared
# also see that pretrans is only for non-debug
if [ ! "%{?1}" == %{debug_suffix} ]; then
  if [ -f %{_libexecdir}/copy_jdk_configs_fixFiles.sh ] ; then
    sh  %{_libexecdir}/copy_jdk_configs_fixFiles.sh %{rpm_state_dir}/%{name}.%{_arch}  %{_jvmdir}/%{sdkdir -- %{?1}}
  fi
fi

exit 0
}

%define postun_script() %{expand:
update-desktop-database %{_datadir}/applications &> /dev/null || :
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    %{update_desktop_icons}
fi
exit 0
}


%define postun_headless() %{expand:
  if [ "x$debug"  == "xtrue" ] ; then
    set -x
  fi
  post_state=$1 # from postun, https://docs.fedoraproject.org/en-US/packaging-guidelines/Scriptlets/#_syntax
  %{save_and_remove_alternatives  java  %{jrebindir -- %{?1}}/java $post_state %{family}}
  %{save_and_remove_alternatives  jre_%{origin} %{_jvmdir}/%{sdkdir -- %{?1}} $post_state %{family}}
  %{save_and_remove_alternatives  jre_%{javaver} %{_jvmdir}/%{sdkdir -- %{?1}} $post_state %{family}}
  %{save_and_remove_alternatives  jre_%{javaver}_%{origin} %{_jvmdir}/%{jrelnk -- %{?1}} $post_state %{family}}
}

%define posttrans_script() %{expand:
%{update_desktop_icons}
}


%define alternatives_javac_install() %{expand:
if [ "x$debug"  == "xtrue" ] ; then
  set -x
fi
PRIORITY=%{priority}
if [ "%{?1}" == %{debug_suffix} ]; then
  let PRIORITY=PRIORITY-1
fi

ext=.gz
key=javac
alternatives \\
  --install %{_bindir}/javac $key %{sdkbindir -- %{?1}}/javac $PRIORITY  --family %{family} \\
  --slave %{_jvmdir}/java java_sdk %{_jvmdir}/%{sdkdir -- %{?1}} \\
  --slave %{_bindir}/jlink jlink %{sdkbindir -- %{?1}}/jlink \\
  --slave %{_bindir}/jmod jmod %{sdkbindir -- %{?1}}/jmod \\
%ifarch %{sa_arches}
%ifnarch %{zero_arches}
  --slave %{_bindir}/jhsdb jhsdb %{sdkbindir -- %{?1}}/jhsdb \\
%endif
%endif
  --slave %{_bindir}/jar jar %{sdkbindir -- %{?1}}/jar \\
  --slave %{_bindir}/jarsigner jarsigner %{sdkbindir -- %{?1}}/jarsigner \\
  --slave %{_bindir}/javadoc javadoc %{sdkbindir -- %{?1}}/javadoc \\
  --slave %{_bindir}/javap javap %{sdkbindir -- %{?1}}/javap \\
  --slave %{_bindir}/jconsole jconsole %{sdkbindir -- %{?1}}/jconsole \\
  --slave %{_bindir}/jdb jdb %{sdkbindir -- %{?1}}/jdb \\
  --slave %{_bindir}/jdeps jdeps %{sdkbindir -- %{?1}}/jdeps \\
  --slave %{_bindir}/jdeprscan jdeprscan %{sdkbindir -- %{?1}}/jdeprscan \\
  --slave %{_bindir}/jfr jfr %{sdkbindir -- %{?1}}/jfr \\
  --slave %{_bindir}/jimage jimage %{sdkbindir -- %{?1}}/jimage \\
  --slave %{_bindir}/jinfo jinfo %{sdkbindir -- %{?1}}/jinfo \\
  --slave %{_bindir}/jmap jmap %{sdkbindir -- %{?1}}/jmap \\
  --slave %{_bindir}/jps jps %{sdkbindir -- %{?1}}/jps \\
  --slave %{_bindir}/jpackage jpackage %{sdkbindir -- %{?1}}/jpackage \\
  --slave %{_bindir}/jrunscript jrunscript %{sdkbindir -- %{?1}}/jrunscript \\
  --slave %{_bindir}/jshell jshell %{sdkbindir -- %{?1}}/jshell \\
  --slave %{_bindir}/jstack jstack %{sdkbindir -- %{?1}}/jstack \\
  --slave %{_bindir}/jstat jstat %{sdkbindir -- %{?1}}/jstat \\
  --slave %{_bindir}/jstatd jstatd %{sdkbindir -- %{?1}}/jstatd \\
  --slave %{_bindir}/serialver serialver %{sdkbindir -- %{?1}}/serialver \\
  --slave %{_mandir}/man1/jar.1$ext jar.1$ext \\
  %{_mandir}/man1/jar-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jarsigner.1$ext jarsigner.1$ext \\
  %{_mandir}/man1/jarsigner-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/javac.1$ext javac.1$ext \\
  %{_mandir}/man1/javac-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/javadoc.1$ext javadoc.1$ext \\
  %{_mandir}/man1/javadoc-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/javap.1$ext javap.1$ext \\
  %{_mandir}/man1/javap-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jconsole.1$ext jconsole.1$ext \\
  %{_mandir}/man1/jconsole-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jdb.1$ext jdb.1$ext \\
  %{_mandir}/man1/jdb-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jdeps.1$ext jdeps.1$ext \\
  %{_mandir}/man1/jdeps-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jinfo.1$ext jinfo.1$ext \\
  %{_mandir}/man1/jinfo-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jmap.1$ext jmap.1$ext \\
  %{_mandir}/man1/jmap-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jps.1$ext jps.1$ext \\
  %{_mandir}/man1/jps-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jpackage.1$ext jpackage.1$ext \\
  %{_mandir}/man1/jpackage-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jrunscript.1$ext jrunscript.1$ext \\
  %{_mandir}/man1/jrunscript-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jstack.1$ext jstack.1$ext \\
  %{_mandir}/man1/jstack-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jstat.1$ext jstat.1$ext \\
  %{_mandir}/man1/jstat-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/jstatd.1$ext jstatd.1$ext \\
  %{_mandir}/man1/jstatd-%{uniquesuffix -- %{?1}}.1$ext \\
  --slave %{_mandir}/man1/serialver.1$ext serialver.1$ext \\
  %{_mandir}/man1/serialver-%{uniquesuffix -- %{?1}}.1$ext

%{set_if_needed_alternatives  $key %{family}}

for X in %{origin} %{javaver} ; do
  key=java_sdk_"$X"
  alternatives --install %{_jvmdir}/java-"$X" $key %{_jvmdir}/%{sdkdir -- %{?1}} $PRIORITY  --family %{family}
  %{set_if_needed_alternatives  $key %{family}}
done

key=java_sdk_%{javaver}_%{origin}
alternatives --install %{_jvmdir}/java-%{javaver}-%{origin} $key %{_jvmdir}/%{sdkdir -- %{?1}} $PRIORITY  --family %{family}
%{set_if_needed_alternatives  $key %{family}}
}

%define post_devel() %{expand:
update-desktop-database %{_datadir}/applications &> /dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

exit 0
}

%define postun_devel() %{expand:
  if [ "x$debug"  == "xtrue" ] ; then
    set -x
  fi
  post_state=$1 # from postun, https://docs.fedoraproject.org/en-US/packaging-guidelines/Scriptlets/#_syntax
  %{save_and_remove_alternatives  javac %{sdkbindir -- %{?1}}/javac $post_state %{family}}
  %{save_and_remove_alternatives  java_sdk_%{origin} %{_jvmdir}/%{sdkdir -- %{?1}} $post_state %{family}}
  %{save_and_remove_alternatives  java_sdk_%{javaver} %{_jvmdir}/%{sdkdir -- %{?1}} $post_state %{family}}
  %{save_and_remove_alternatives  java_sdk_%{javaver}_%{origin} %{_jvmdir}/%{sdkdir -- %{?1}} $post_state %{family}}

update-desktop-database %{_datadir}/applications &> /dev/null || :

if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    %{update_desktop_icons}
fi
exit 0
}

%define posttrans_devel() %{expand:
%{alternatives_javac_install --  %{?1}}
%{update_desktop_icons}
}

%define alternatives_javadoc_install() %{expand:
if [ "x$debug"  == "xtrue" ] ; then
  set -x
fi
PRIORITY=%{priority}
if [ "%{?1}" == %{debug_suffix} ]; then
  let PRIORITY=PRIORITY-1
fi

key=javadocdir
alternatives --install %{_javadocdir}/java $key %{_javadocdir}/%{uniquejavadocdir -- %{?1}}/api $PRIORITY  --family %{family_noarch}
%{set_if_needed_alternatives  $key %{family_noarch}}
exit 0
}

%define postun_javadoc() %{expand:
if [ "x$debug"  == "xtrue" ] ; then
  set -x
fi
  post_state=$1 # from postun, https://docs.fedoraproject.org/en-US/packaging-guidelines/Scriptlets/#_syntax
  %{save_and_remove_alternatives  javadocdir  %{_javadocdir}/%{uniquejavadocdir -- %{?1}}/api $post_state %{family_noarch}}
exit 0
}

%define alternatives_javadoczip_install() %{expand:
if [ "x$debug"  == "xtrue" ] ; then
  set -x
fi
PRIORITY=%{priority}
if [ "%{?1}" == %{debug_suffix} ]; then
  let PRIORITY=PRIORITY-1
fi
key=javadoczip
alternatives --install %{_javadocdir}/java-zip $key %{_javadocdir}/%{uniquejavadocdir -- %{?1}}.zip $PRIORITY  --family %{family_noarch}
%{set_if_needed_alternatives  $key %{family_noarch}}
exit 0
}

%define postun_javadoc_zip() %{expand:
  if [ "x$debug"  == "xtrue" ] ; then
    set -x
  fi
  post_state=$1 # from postun, https://docs.fedoraproject.org/en-US/packaging-guidelines/Scriptlets/#_syntax
  %{save_and_remove_alternatives  javadoczip  %{_javadocdir}/%{uniquejavadocdir -- %{?1}}.zip $post_state %{family_noarch}}
exit 0
}

%define files_jre() %{expand:
%{_datadir}/icons/hicolor/*x*/apps/java-%{javaver}-%{origin}.png
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libsplashscreen.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libawt_xawt.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libjawt.so
}


%define files_jre_headless() %{expand:
%license %{_jvmdir}/%{sdkdir -- %{?1}}/legal
%doc %{_defaultdocdir}/%{uniquejavadocdir -- %{?1}}/NEWS
%doc %{_defaultdocdir}/%{uniquejavadocdir -- %{?1}}/README.md
%doc %{_defaultdocdir}/%{uniquejavadocdir -- %{?1}}/java-%{featurever}-openjdk-portable.specfile
%dir %{_sysconfdir}/.java/.systemPrefs
%dir %{_sysconfdir}/.java
%dir %{_jvmdir}/%{sdkdir -- %{?1}}
%{_jvmdir}/%{sdkdir -- %{?1}}/release
%{_jvmdir}/%{jrelnk -- %{?1}}
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/bin
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/java
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/%{alt_java_name}
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jcmd
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/keytool
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/rmiregistry
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/lib
%ifarch %{jit_arches}
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/classlist
%endif
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/jexec
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/jspawnhelper
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/jrt-fs.jar
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/modules
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/psfont.properties.ja
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/psfontj2d.properties
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/tzdb.dat
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libjli.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/jvm.cfg
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libattach.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libawt.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libextnet.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libjsig.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libawt_headless.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libdt_socket.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libfontmanager.so
%if ! %{system_libs}
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libfreetype.so
%endif
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libinstrument.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libj2gss.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libj2pcsc.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libj2pkcs11.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libjaas.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libjava.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libjavajpeg.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libjdwp.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libjimage.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libjsound.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/liblcms.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libmanagement.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libmanagement_agent.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libmanagement_ext.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libmlib_image.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libnet.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libnio.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libprefs.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/librmi.so
# Some architectures don't have the serviceability agent
%ifarch %{sa_arches}
%ifnarch %{zero_arches}
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libsaproc.so
%endif
%endif
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libsctp.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libsystemconf.so
%ifarch %{svml_arches}
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libjsvml.so
%endif
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libsyslookup.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libverify.so
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/libzip.so
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/lib/jfr
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/jfr/default.jfc
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/jfr/profile.jfc
%{_mandir}/man1/java-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/%{alt_java_name}-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jcmd-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/keytool-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/rmiregistry-%{uniquesuffix -- %{?1}}.1*
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/%{vm_variant}/
%ifarch %{share_arches}
%attr(444, root, root) %{_jvmdir}/%{sdkdir -- %{?1}}/lib/%{vm_variant}/classes.jsa
%ifnarch %{ix86} %{arm32}
%attr(444, root, root) %{_jvmdir}/%{sdkdir -- %{?1}}/lib/%{vm_variant}/classes_nocoops.jsa
%endif
%endif
%dir %{etcjavasubdir}
%dir %{etcjavadir -- %{?1}}
%dir %{etcjavadir -- %{?1}}/lib
%dir %{etcjavadir -- %{?1}}/lib/security
%{etcjavadir -- %{?1}}/lib/security/cacerts
%dir %{etcjavadir -- %{?1}}/conf
%dir %{etcjavadir -- %{?1}}/conf/sdp
%dir %{etcjavadir -- %{?1}}/conf/management
%dir %{etcjavadir -- %{?1}}/conf/security
%dir %{etcjavadir -- %{?1}}/conf/security/policy
%dir %{etcjavadir -- %{?1}}/conf/security/policy/limited
%dir %{etcjavadir -- %{?1}}/conf/security/policy/unlimited
%config(noreplace) %{etcjavadir -- %{?1}}/lib/security/default.policy
%config(noreplace) %{etcjavadir -- %{?1}}/lib/security/blocked.certs
%config(noreplace) %{etcjavadir -- %{?1}}/lib/security/public_suffix_list.dat
%config(noreplace) %{etcjavadir -- %{?1}}/conf/security/policy/limited/exempt_local.policy
%config(noreplace) %{etcjavadir -- %{?1}}/conf/security/policy/limited/default_local.policy
%config(noreplace) %{etcjavadir -- %{?1}}/conf/security/policy/limited/default_US_export.policy
%config(noreplace) %{etcjavadir -- %{?1}}/conf/security/policy/unlimited/default_local.policy
%config(noreplace) %{etcjavadir -- %{?1}}/conf/security/policy/unlimited/default_US_export.policy
 %{etcjavadir -- %{?1}}/conf/security/policy/README.txt
%config(noreplace) %{etcjavadir -- %{?1}}/conf/security/java.policy
%config(noreplace) %{etcjavadir -- %{?1}}/conf/security/java.security
%config(noreplace) %{etcjavadir -- %{?1}}/conf/logging.properties
%config(noreplace) %{etcjavadir -- %{?1}}/conf/security/nss.cfg
%config(noreplace) %{etcjavadir -- %{?1}}/conf/security/nss.fips.cfg
%config(noreplace) %{etcjavadir -- %{?1}}/conf/management/jmxremote.access
# This is a config template, thus not config-noreplace
%config  %{etcjavadir -- %{?1}}/conf/management/jmxremote.password.template
%config  %{etcjavadir -- %{?1}}/conf/sdp/sdp.conf.template
%config(noreplace) %{etcjavadir -- %{?1}}/conf/management/management.properties
%config(noreplace) %{etcjavadir -- %{?1}}/conf/net.properties
%config(noreplace) %{etcjavadir -- %{?1}}/conf/sound.properties
%{_jvmdir}/%{sdkdir -- %{?1}}/conf
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/security
%if %is_system_jdk
%if %{is_release_build -- %{?1}}
%ghost %{_bindir}/java
%ghost %{_jvmdir}/jre
%ghost %{_bindir}/%{alt_java_name}
%ghost %{_bindir}/jcmd
%ghost %{_bindir}/keytool
%ghost %{_bindir}/rmiregistry
%ghost %{_jvmdir}/jre-%{origin}
%ghost %{_jvmdir}/jre-%{javaver}
%ghost %{_jvmdir}/jre-%{javaver}-%{origin}
%endif
%endif
# https://bugzilla.redhat.com/show_bug.cgi?id=1820172
# https://docs.fedoraproject.org/en-US/packaging-guidelines/Directory_Replacement/
%ghost %{_jvmdir}/%{sdkdir -- %{?1}}/conf.rpmmoved
%ghost %{_jvmdir}/%{sdkdir -- %{?1}}/lib/security.rpmmoved
}

%define files_devel() %{expand:
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/bin
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jar
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jarsigner
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/javac
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/javadoc
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/javap
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jconsole
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jdb
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jdeps
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jdeprscan
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jfr
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jimage
# Some architectures don't have the serviceability agent
%ifarch %{sa_arches}
%ifnarch %{zero_arches}
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jhsdb
%{_mandir}/man1/jhsdb-%{uniquesuffix -- %{?1}}.1*
%endif
%endif
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jinfo
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jlink
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jmap
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jmod
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jps
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jpackage
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jrunscript
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jshell
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jstack
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jstat
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/jstatd
%{_jvmdir}/%{sdkdir -- %{?1}}/bin/serialver
%{_jvmdir}/%{sdkdir -- %{?1}}/include
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/ct.sym
%if %{with_systemtap}
%{_jvmdir}/%{sdkdir -- %{?1}}/tapset
%endif
%{_datadir}/applications/*jconsole%{?1}.desktop
%{_mandir}/man1/jar-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jarsigner-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/javac-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/javadoc-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/javap-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jconsole-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jdb-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jdeps-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jinfo-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jmap-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jps-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jpackage-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jrunscript-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jstack-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jstat-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jstatd-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/serialver-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jdeprscan-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jlink-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jmod-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jshell-%{uniquesuffix -- %{?1}}.1*
%{_mandir}/man1/jfr-%{uniquesuffix -- %{?1}}.1*

%if %{with_systemtap}
%dir %{tapsetroot}
%dir %{tapsetdirttapset}
%dir %{tapsetdir}
%{tapsetdir}/*%{_arch}%{?1}.stp
%endif
%if %is_system_jdk
%if %{is_release_build -- %{?1}}
%ghost %{_bindir}/javac
%ghost %{_jvmdir}/java
%ghost %{_bindir}/jlink
%ghost %{_bindir}/jmod
%ghost %{_bindir}/jhsdb
%ghost %{_bindir}/jar
%ghost %{_bindir}/jarsigner
%ghost %{_bindir}/javadoc
%ghost %{_bindir}/javap
%ghost %{_bindir}/jconsole
%ghost %{_bindir}/jdb
%ghost %{_bindir}/jdeps
%ghost %{_bindir}/jdeprscan
%ghost %{_bindir}/jfr
%ghost %{_bindir}/jimage
%ghost %{_bindir}/jinfo
%ghost %{_bindir}/jmap
%ghost %{_bindir}/jps
%ghost %{_bindir}/jpackage
%ghost %{_bindir}/jrunscript
%ghost %{_bindir}/jshell
%ghost %{_bindir}/jstack
%ghost %{_bindir}/jstat
%ghost %{_bindir}/jstatd
%ghost %{_bindir}/serialver
%ghost %{_jvmdir}/java-%{origin}
%ghost %{_jvmdir}/java-%{javaver}
%ghost %{_jvmdir}/java-%{javaver}-%{origin}
%endif
%endif
}

%define files_jmods() %{expand:
%{_jvmdir}/%{sdkdir -- %{?1}}/jmods
}

%define files_demo() %{expand:
%license %{_jvmdir}/%{sdkdir -- %{?1}}/legal
%{_jvmdir}/%{sdkdir -- %{?1}}/demo
%{_jvmdir}/%{sdkdir -- %{?1}}/sample
}

%define files_src() %{expand:
%license %{_jvmdir}/%{sdkdir -- %{?1}}/legal
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/src.zip
}

%define files_static_libs() %{expand:
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/lib/static
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/lib/static/linux-%{archinstall}
%dir %{_jvmdir}/%{sdkdir -- %{?1}}/lib/static/linux-%{archinstall}/glibc
%{_jvmdir}/%{sdkdir -- %{?1}}/lib/static/linux-%{archinstall}/glibc/lib*.a
}

%define files_javadoc() %{expand:
%doc %{_javadocdir}/%{uniquejavadocdir -- %{?1}}
%license %{_jvmdir}/%{sdkdir -- %{?1}}/legal
%if %is_system_jdk
%if %{is_release_build -- %{?1}}
%ghost %{_javadocdir}/java
%endif
%endif
}

%define files_javadoc_zip() %{expand:
%doc %{_javadocdir}/%{uniquejavadocdir -- %{?1}}.zip
%license %{_jvmdir}/%{sdkdir -- %{?1}}/legal
%if %is_system_jdk
%if %{is_release_build -- %{?1}}
%ghost %{_javadocdir}/java-zip
%endif
%endif
}

# x86 is not supported by OpenJDK 17
ExcludeArch: %{ix86}

# not-duplicated requires/provides/obsoletes for normal/debug packages
%define java_rpo() %{expand:
Requires: fontconfig%{?_isa}
Requires: xorg-x11-fonts-Type1
# Require libXcomposite explicitly since it's only dynamically loaded
# at runtime. Fixes screenshot issues. See JDK-8150954.
Requires: libXcomposite%{?_isa}
# Requires rest of java
Requires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
OrderWithRequires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
# for java-X-openjdk package's desktop binding
# Where recommendations are available, recommend Gtk+ for the Swing look and feel
%if 0%{?rhel} >= 8 || 0%{?fedora} > 0
Recommends: gtk3%{?_isa}
%endif

Provides: java-%{javaver}-%{origin}%{?1} = %{epoch}:%{version}-%{release}

# Standard JPackage base provides
Provides: jre-%{javaver}%{?1} = %{epoch}:%{version}-%{release}
Provides: jre-%{javaver}-%{origin}%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}%{?1} = %{epoch}:%{version}-%{release}
%if %is_system_jdk
Provides: java-%{origin}%{?1} = %{epoch}:%{version}-%{release}
Provides: jre-%{origin}%{?1} = %{epoch}:%{version}-%{release}
Provides: java%{?1} = %{epoch}:%{version}-%{release}
Provides: jre%{?1} = %{epoch}:%{version}-%{release}
%endif
}

%define java_headless_rpo() %{expand:
# Require /etc/pki/java/cacerts
Requires: ca-certificates
# Require javapackages-filesystem for ownership of /usr/lib/jvm/ and macros
Requires: javapackages-filesystem
# Require zone-info data provided by tzdata-java sub-package
# 2024a required as of JDK-8325150
# Use 2023d until 2024a is in the buildroot
Requires: tzdata-java >= 2023d
# for support of kernel stream control
# libsctp.so.1 is being `dlopen`ed on demand
Requires: lksctp-tools%{?_isa}
%if ! 0%{?flatpak}
# tool to copy jdk's configs - should be Recommends only, but then only dnf/yum enforce it,
# not rpm transaction and so no configs are persisted when pure rpm -u is run. It may be
# considered as regression
Requires: copy-jdk-configs >= 3.3
OrderWithRequires: copy-jdk-configs
%endif
# for printing support
Requires: cups-libs
# for system security properties
Requires: crypto-policies
# for FIPS PKCS11 provider
Requires: nss
# Post requires alternatives to install tool alternatives
Requires(post):   %{alternatives_requires}
# Postun requires alternatives to uninstall tool alternatives
Requires(postun): %{alternatives_requires}
# Where suggestions are available, recommend the sctp and pcsc libraries
# for optional support of kernel stream control and card reader
%if 0%{?rhel} >= 8 || 0%{?fedora} > 0
Suggests: lksctp-tools%{?_isa}, pcsc-lite-libs%{?_isa}
%endif

# Standard JPackage base provides
Provides: jre-%{javaver}-%{origin}-headless%{?1} = %{epoch}:%{version}-%{release}
Provides: jre-%{javaver}-headless%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-%{origin}-headless%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-headless%{?1} = %{epoch}:%{version}-%{release}
%if %is_system_jdk
Provides: java-%{origin}-headless%{?1} = %{epoch}:%{version}-%{release}
Provides: jre-%{origin}-headless%{?1} = %{epoch}:%{version}-%{release}
Provides: jre-headless%{?1} = %{epoch}:%{version}-%{release}
Provides: java-headless%{?1} = %{epoch}:%{version}-%{release}
%endif
}

%define java_devel_rpo() %{expand:
# Requires base package
Requires:         %{name}%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
OrderWithRequires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
# Post requires alternatives to install tool alternatives
Requires(post):   %{alternatives_requires}
# Postun requires alternatives to uninstall tool alternatives
Requires(postun): %{alternatives_requires}

# Standard JPackage devel provides
Provides: java-sdk-%{javaver}-%{origin}%{?1} = %{epoch}:%{version}-%{release}
Provides: java-sdk-%{javaver}%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-devel%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-%{origin}-devel%{?1} = %{epoch}:%{version}-%{release}
%if %is_system_jdk
Provides: java-devel-%{origin}%{?1} = %{epoch}:%{version}-%{release}
Provides: java-sdk-%{origin}%{?1} = %{epoch}:%{version}-%{release}
Provides: java-devel%{?1} = %{epoch}:%{version}-%{release}
Provides: java-sdk%{?1} = %{epoch}:%{version}-%{release}
%endif
}

%define java_static_libs_rpo() %{expand:
Requires:         %{name}-devel%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
OrderWithRequires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
}

%define java_jmods_rpo() %{expand:
# Requires devel package
# as jmods are bytecode, they should be OK without any _isa
Requires:         %{name}-devel%{?1} = %{epoch}:%{version}-%{release}
OrderWithRequires: %{name}-headless%{?1} = %{epoch}:%{version}-%{release}

Provides: java-%{javaver}-jmods%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-%{origin}-jmods%{?1} = %{epoch}:%{version}-%{release}
%if %is_system_jdk
Provides: java-jmods%{?1} = %{epoch}:%{version}-%{release}
%endif
}

%define java_demo_rpo() %{expand:
Requires: %{name}%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
OrderWithRequires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}

Provides: java-%{javaver}-demo%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-%{origin}-demo%{?1} = %{epoch}:%{version}-%{release}
%if %is_system_jdk
Provides: java-demo%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{origin}-demo%{?1} = %{epoch}:%{version}-%{release}
%endif
}

%define java_javadoc_rpo() %{expand:
OrderWithRequires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}
# Post requires alternatives to install javadoc alternative
Requires(post):   %{alternatives_requires}
# Postun requires alternatives to uninstall javadoc alternative
Requires(postun): %{alternatives_requires}

# Standard JPackage javadoc provides
Provides: java-%{javaver}-javadoc%{?1}%{?2} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-%{origin}-javadoc%{?1}%{?2} = %{epoch}:%{version}-%{release}
%if %is_system_jdk
Provides: java-javadoc%{?1}%{?2} = %{epoch}:%{version}-%{release}
%endif
}

%define java_src_rpo() %{expand:
Requires: %{name}-headless%{?1}%{?_isa} = %{epoch}:%{version}-%{release}

# Standard JPackage sources provides
Provides: java-%{javaver}-src%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-%{origin}-src%{?1} = %{epoch}:%{version}-%{release}
%if %is_system_jdk
Provides: java-src%{?1} = %{epoch}:%{version}-%{release}
Provides: java-%{origin}-src%{?1} = %{epoch}:%{version}-%{release}
%endif
}

# Prevent brp-java-repack-jars from being run
%global __jar_repack 0

Name:    java-%{javaver}-%{origin}
Version: %{newjavaver}.%{buildver}
Release: %{?eaprefix}%{rpmrelease}%{?extraver}%{?dist}
# Equivalent for the portable build
%global prelease %{?eaprefix}%{portablerelease}%{?extraver}
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
Summary: %{origin_nice} %{featurever} Runtime Environment
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
Source9: jconsole.desktop.in

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

# Include portable spec and instructions on how to rebuild
Source19: README.md
Source20: java-%{featurever}-openjdk-portable.specfile

# Setup variables to reference correct sources
%global releasezip %{_jvmdir}/%{name}-%{version}-%{prelease}.portable.unstripped.jdk.%{_arch}.tar.xz
%global staticlibzip %{_jvmdir}/%{name}-%{version}-%{prelease}.portable.static-libs.%{_arch}.tar.xz
%global docszip %{_jvmdir}/%{name}-%{version}-%{prelease}.portable.docs.%{_arch}.tar.xz
%global misczip %{_jvmdir}/%{name}-%{version}-%{prelease}.portable.misc.%{_arch}.tar.xz
%global slowdebugzip %{_jvmdir}/%{name}-%{version}-%{prelease}.portable.slowdebug.jdk.%{_arch}.tar.xz
%global slowdebugstaticlibzip %{_jvmdir}/%{name}-%{version}-%{prelease}.portable.slowdebug.static-libs.%{_arch}.tar.xz
%global fastdebugzip %{_jvmdir}/%{name}-%{version}-%{prelease}.portable.fastdebug.jdk.%{_arch}.tar.xz
%global fastdebugstaticlibzip %{_jvmdir}/%{name}-%{version}-%{prelease}.portable.fastdebug.static-libs.%{_arch}.tar.xz

############################################
#
# RPM/distribution specific patches
#
############################################

# NSS via SunPKCS11 Provider (disabled comment
# due to memory leak).
Patch1000: rh1648249-add_commented_out_nss_cfg_provider_to_java_security.patch
# RH1750419: enable build of speculative store bypass hardened alt-java (CVE-2018-3639)
Patch600: rh1750419-redhat_alt_java.patch

# Ignore AWTError when assistive technologies are loaded
Patch1:    rh1648242-accessible_toolkit_crash_do_not_break_jvm.patch

# Crypto policy and FIPS support patches
# Patch is generated from the fips-17u tree at https://github.com/rh-openjdk/jdk/tree/fips-17u
# as follows: git diff %%{vcstag} src make test > fips-17u-$(git show -s --format=%h HEAD).patch
# Diff is limited to src and make subdirectories to exclude .github changes
# The following list is generated by:
# git log %%{vcstag}.. --no-merges --format=%s --reverse:
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

# Depend on pcsc-lite-libs instead of pcsc-lite-devel as this is only in optional repo
Patch6: rh1684077-openjdk_should_depend_on_pcsc-lite-libs_instead_of_pcsc-lite-devel.patch

#############################################
#
# OpenJDK patches appearing in 17.0.10
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
# Requirement for setting up nss.cfg and nss.fips.cfg
BuildRequires: nss-devel
# Requirement for system security property test
BuildRequires: crypto-policies
BuildRequires: pkgconfig
BuildRequires: xorg-x11-proto-devel
BuildRequires: zip
BuildRequires: javapackages-filesystem
%if %{include_normal_build}
BuildRequires: java-%{featurever}-openjdk-portable-unstripped = %{epoch}:%{version}-%{prelease}.%{portablesuffix}
BuildRequires: java-%{featurever}-openjdk-portable-static-libs = %{epoch}:%{version}-%{prelease}.%{portablesuffix}
%endif
%if %{include_fastdebug_build}
BuildRequires: java-%{featurever}-openjdk-portable-devel-fastdebug = %{epoch}:%{version}-%{prelease}.%{portablesuffix}
BuildRequires: java-%{featurever}-openjdk-portable-static-libs-fastdebug = %{epoch}:%{version}-%{prelease}.%{portablesuffix}
%endif
%if %{include_debug_build}
BuildRequires: java-%{featurever}-openjdk-portable-devel-slowdebug = %{epoch}:%{version}-%{prelease}.%{portablesuffix}
BuildRequires: java-%{featurever}-openjdk-portable-static-libs-slowdebug = %{epoch}:%{version}-%{prelease}.%{portablesuffix}
%endif
BuildRequires: java-%{featurever}-openjdk-portable-docs = %{epoch}:%{version}-%{prelease}.%{portablesuffix}
BuildRequires: java-%{featurever}-openjdk-portable-misc = %{epoch}:%{version}-%{prelease}.%{portablesuffix}
# Zero-assembler build requirement
%ifarch %{zero_arches}
BuildRequires: libffi-devel
%endif
# 2024a required as of JDK-8325150
# Use 2023d until 2024a is in the buildroot
BuildRequires: tzdata-java >= 2023d
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
# Version in src/java.desktop/share/native/libfreetype/include/freetype/freetype.h
Provides: bundled(freetype) = 2.13.0
# Version in src/java.desktop/share/native/libsplashscreen/giflib/gif_lib.h
Provides: bundled(giflib) = 5.2.1
# Version in src/java.desktop/share/native/libharfbuzz/hb-version.h
Provides: bundled(harfbuzz) = 7.2.0
# Version in src/java.desktop/share/native/liblcms/lcms2.h
Provides: bundled(lcms2) = 2.15.0
# Version in src/java.desktop/share/native/libjavajpeg/jpeglib.h
Provides: bundled(libjpeg) = 6b
# Version in src/java.desktop/share/native/libsplashscreen/libpng/png.h
Provides: bundled(libpng) = 1.6.39
%endif

# this is always built, also during debug-only build
# when it is built in debug-only this package is just placeholder
%{java_rpo %{nil}}

%description
The %{origin_nice} %{featurever} runtime environment.

%if %{include_debug_build}
%package slowdebug
Summary: %{origin_nice} %{featurever} Runtime Environment %{debug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_rpo -- %{debug_suffix_unquoted}}
%description slowdebug
The %{origin_nice} %{featurever} runtime environment.
%{debug_warning}
%endif

%if %{include_fastdebug_build}
%package fastdebug
Summary: %{origin_nice} %{featurever} Runtime Environment %{fastdebug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_rpo -- %{fastdebug_suffix_unquoted}}
%description fastdebug
The %{origin_nice} %{featurever} runtime environment.
%{fastdebug_warning}
%endif

%if %{include_normal_build}
%package headless
Summary: %{origin_nice} %{featurever} Headless Runtime Environment
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_headless_rpo %{nil}}

%description headless
The %{origin_nice} %{featurever} runtime environment without audio and video support.
%endif

%if %{include_debug_build}
%package headless-slowdebug
Summary: %{origin_nice} %{featurever} Runtime Environment %{debug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_headless_rpo -- %{debug_suffix_unquoted}}

%description headless-slowdebug
The %{origin_nice} %{featurever} runtime environment without audio and video support.
%{debug_warning}
%endif

%if %{include_fastdebug_build}
%package headless-fastdebug
Summary: %{origin_nice} %{featurever} Runtime Environment %{fastdebug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_headless_rpo -- %{fastdebug_suffix_unquoted}}

%description headless-fastdebug
The %{origin_nice} %{featurever} runtime environment without audio and video support.
%{fastdebug_warning}
%endif

%if %{include_normal_build}
%package devel
Summary: %{origin_nice} %{featurever} Development Environment
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_devel_rpo %{nil}}

%description devel
The %{origin_nice} %{featurever} development tools.
%endif

%if %{include_debug_build}
%package devel-slowdebug
Summary: %{origin_nice} %{featurever} Development Environment %{debug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_devel_rpo -- %{debug_suffix_unquoted}}

%description devel-slowdebug
The %{origin_nice} %{featurever} development tools.
%{debug_warning}
%endif

%if %{include_fastdebug_build}
%package devel-fastdebug
Summary: %{origin_nice} %{featurever} Development Environment %{fastdebug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Tools
%endif

%{java_devel_rpo -- %{fastdebug_suffix_unquoted}}

%description devel-fastdebug
The %{origin_nice} %{featurever} development tools              .
%{fastdebug_warning}
%endif

%if %{include_staticlibs}

%if %{include_normal_build}
%package static-libs
Summary: %{origin_nice} %{featurever} libraries for static linking

%{java_static_libs_rpo %{nil}}

%description static-libs
The %{origin_nice} %{featurever} libraries for static linking.
%endif

%if %{include_debug_build}
%package static-libs-slowdebug
Summary: %{origin_nice} %{featurever} libraries for static linking %{debug_on}

%{java_static_libs_rpo -- %{debug_suffix_unquoted}}

%description static-libs-slowdebug
The %{origin_nice} %{featurever} libraries for static linking.
%{debug_warning}
%endif

%if %{include_fastdebug_build}
%package static-libs-fastdebug
Summary: %{origin_nice} %{featurever} libraries for static linking %{fastdebug_on}

%{java_static_libs_rpo -- %{fastdebug_suffix_unquoted}}

%description static-libs-fastdebug
The %{origin_nice} %{featurever} libraries for static linking.
%{fastdebug_warning}
%endif

# staticlibs
%endif

%if %{include_normal_build}
%package jmods
Summary: JMods for %{origin_nice} %{featurever}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_jmods_rpo %{nil}}

%description jmods
The JMods for %{origin_nice} %{featurever}.
%endif

%if %{include_debug_build}
%package jmods-slowdebug
Summary: JMods for %{origin_nice} %{featurever} %{debug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_jmods_rpo -- %{debug_suffix_unquoted}}

%description jmods-slowdebug
The JMods for %{origin_nice} %{featurever}.
%{debug_warning}
%endif

%if %{include_fastdebug_build}
%package jmods-fastdebug
Summary: JMods for %{origin_nice} %{featurever} %{fastdebug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Tools
%endif

%{java_jmods_rpo -- %{fastdebug_suffix_unquoted}}

%description jmods-fastdebug
The JMods for %{origin_nice} %{featurever}.
%{fastdebug_warning}
%endif

%if %{include_normal_build}
%package demo
Summary: %{origin_nice} %{featurever} Demos
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_demo_rpo %{nil}}

%description demo
The %{origin_nice} %{featurever} demos.
%endif

%if %{include_debug_build}
%package demo-slowdebug
Summary: %{origin_nice} %{featurever} Demos %{debug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_demo_rpo -- %{debug_suffix_unquoted}}

%description demo-slowdebug
The %{origin_nice} %{featurever} demos.
%{debug_warning}
%endif

%if %{include_fastdebug_build}
%package demo-fastdebug
Summary: %{origin_nice} %{featurever} Demos %{fastdebug_on}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_demo_rpo -- %{fastdebug_suffix_unquoted}}

%description demo-fastdebug
The %{origin_nice} %{featurever} demos.
%{fastdebug_warning}
%endif

%if %{include_normal_build}
%package src
Summary: %{origin_nice} %{featurever} Source Bundle
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_src_rpo %{nil}}

%description src
The %{compatiblename}-src sub-package contains the complete %{origin_nice} %{featurever}
class library source code for use by IDE indexers and debuggers.
%endif

%if %{include_debug_build}
%package src-slowdebug
Summary: %{origin_nice} %{featurever} Source Bundle %{for_debug}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_src_rpo -- %{debug_suffix_unquoted}}

%description src-slowdebug
The %{compatiblename}-src-slowdebug sub-package contains the complete %{origin_nice} %{featurever}
 class library source code for use by IDE indexers and debuggers, %{for_debug}.
%endif

%if %{include_fastdebug_build}
%package src-fastdebug
Summary: %{origin_nice} %{featurever} Source Bundle %{for_fastdebug}
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Development/Languages
%endif

%{java_src_rpo -- %{fastdebug_suffix_unquoted}}

%description src-fastdebug
The %{compatiblename}-src-fastdebug sub-package contains the complete %{origin_nice} %{featurever}
 class library source code for use by IDE indexers and debuggers, %{for_fastdebug}.
%endif

%if %{include_normal_build}
%package javadoc
Summary: %{origin_nice} %{featurever} API documentation
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Documentation
%endif
Requires: javapackages-filesystem
Obsoletes: javadoc-slowdebug < 1:13.0.0.33-1.rolling

%{java_javadoc_rpo -- %{nil} %{nil}}

%description javadoc
The %{origin_nice} %{featurever} API documentation.
%endif

%if %{include_normal_build}
%package javadoc-zip
Summary: %{origin_nice} %{featurever} API documentation compressed in a single archive
%if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
Group:   Documentation
%endif
Requires: javapackages-filesystem
Obsoletes: javadoc-zip-slowdebug < 1:13.0.0.33-1.rolling

%{java_javadoc_rpo -- %{nil} -zip}
%{java_javadoc_rpo -- %{nil} %{nil}}

%description javadoc-zip
The %{origin_nice} %{featurever} API documentation compressed in a single archive.
%endif

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

# Prepare desktop files
# The _X_ syntax indicates variables that are replaced by make upstream
# The @X@ syntax indicates variables that are replaced by configure upstream
for suffix in %{build_loop} ; do
for file in %{SOURCE9}; do
    FILE=`basename $file | sed -e s:\.in$::g`
    EXT="${FILE##*.}"
    NAME="${FILE%.*}"
    OUTPUT_FILE=$NAME$suffix.$EXT
    sed    -e  "s:_SDKBINDIR_:%{sdkbindir -- $suffix}:g" $file > $OUTPUT_FILE
    sed -i -e  "s:@target_cpu@:%{_arch}:g" $OUTPUT_FILE
    sed -i -e  "s:@OPENJDK_VER@:%{version}-%{release}.%{_arch}$suffix:g" $OUTPUT_FILE
    sed -i -e  "s:@JAVA_VER@:%{javaver}:g" $OUTPUT_FILE
    sed -i -e  "s:@JAVA_VENDOR@:%{origin}:g" $OUTPUT_FILE
done
done

# Setup nss.cfg
sed -e "s:@NSS_LIBDIR@:%{NSS_LIBDIR}:g" %{SOURCE11} > nss.cfg

%build

function customisejdk() {
    local imagepath=${1}

    if [ -d ${imagepath} ] ; then
        # Turn on system security properties
        sed -i -e "s:^security.useSystemPropertiesFile=.*:security.useSystemPropertiesFile=true:" \
            ${imagepath}/conf/security/java.security

        # Use system-wide tzdata
        rm ${imagepath}/lib/tzdb.dat
        ln -s %{_datadir}/javazi-1.8/tzdb.dat ${imagepath}/lib/tzdb.dat
    fi
}

mkdir -p $(dirname %{installoutputdir})

docdir=%{installoutputdir -- "-docs"}
tar -xJf %{docszip}
mv java-%{featurever}-openjdk*.docs.* ${docdir}

miscdir=%{installoutputdir -- "-misc"}
tar -xJf %{misczip}
mv java-%{featurever}-openjdk*.misc.* ${miscdir}

for suffix in %{build_loop} ; do

  if [ "x$suffix" = "x" ] ; then
      jdkzip=%{releasezip}
      staticlibzip=%{staticlibzip}
  elif [ "x$suffix" = "x%{fastdebug_suffix_unquoted}" ] ; then
      jdkzip=%{fastdebugzip}
      staticlibzip=%{fastdebugstaticlibzip}
  else # slowdebug
      jdkzip=%{slowdebugzip}
      staticlibzip=%{slowdebugstaticlibzip}
  fi

  installdir=%{installoutputdir -- ${suffix}}

  # TODO: should verify checksums when using packages from buildroot
  tar -xJf ${jdkzip}
  tar -xJf ${staticlibzip}
  mv java-%{featurever}-openjdk* ${installdir}

  # Fix build paths in ELF files so it looks like we built them
  portablenvr="%{name}-%{VERSION}-%{prelease}.%{portablesuffix}.%{_arch}"
  for file in $(find ${installdir} -type f) ; do
      if file ${file} | grep -q 'ELF'; then
	  %{debugedit} -b %{portablebuilddir}/${portablenvr} -d $(pwd) -n ${file}
      fi
  done

  # Set tapset variables to match this build
%if %{with_systemtap}
  for file in ${miscdir}/tapset${suffix}/*.in; do
    OUTPUT_FILE=`echo $file | sed -e "s:\.stp\.in$:-%{version}-%{release}.%{_arch}.stp:g"`
    sed -e "s:@ABS_SERVER_LIBJVM_SO@:%{_jvmdir}/%{sdkdir -- $suffix}/lib/server/libjvm.so:g" $file > ${OUTPUT_FILE}
# TODO find out which architectures other than i686 have a client vm
%ifarch %{ix86}
    sed -i -e "s:@ABS_CLIENT_LIBJVM_SO@:%{_jvmdir}/%{sdkdir -- $suffix}/lib/client/libjvm.so:g" ${OUTPUT_FILE}
%else
    sed -i -e "/@ABS_CLIENT_LIBJVM_SO@/d" ${OUTPUT_FILE}
%endif
    sed -i -e "s:@ABS_JAVA_HOME_DIR@:%{_jvmdir}/%{sdkdir -- $suffix}:g" $OUTPUT_FILE
    sed -i -e "s:@prefix@:%{_jvmdir}/%{sdkdir -- $suffix}/:g" $OUTPUT_FILE
  done
%endif

  # Final setup on the main image
  customisejdk ${installdir}

  # Print release information
  cat ${installdir}/release

# build cycles
done # end of release / debug cycle loop

%check

# We test debug first as it will give better diagnostics on a crash
for suffix in %{build_loop} ; do

export JAVA_HOME=$(pwd)/%{installoutputdir -- ${suffix}}

# Pre-test setup

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
$JAVA_HOME/bin/java ${SEC_DEBUG} ${PROG} true
$JAVA_HOME/bin/java ${SEC_DEBUG} -Djava.security.disableSystemPropertiesFile=true ${PROG} false

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
$JAVA_HOME/bin/javac -d . %{SOURCE18}
$JAVA_HOME/bin/java $(echo $(basename %{SOURCE18})|sed "s|\.java||") JRE
$JAVA_HOME/bin/java -Djava.locale.providers=CLDR $(echo $(basename %{SOURCE18})|sed "s|\.java||") CLDR
%endif

%if %{include_staticlibs}
# Check debug symbols in static libraries (smoke test)
export STATIC_LIBS_HOME=${JAVA_HOME}/lib/static/linux-%{archinstall}/glibc
readelf --debug-dump $STATIC_LIBS_HOME/libfdlibm.a | grep w_remainder.c
readelf --debug-dump $STATIC_LIBS_HOME/libfdlibm.a | grep e_remainder.c
%endif

so_suffix="so"
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
     # We expect to see .cpp files, except for architectures like aarch64 and
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
STRIP_KEEP_SYMTAB=libjvm*

for suffix in %{build_loop} ; do

jdk_image=$(pwd)/%{installoutputdir -- ${suffix}}
# Should match same definitions in build section
docdir=$(pwd)/%{installoutputdir -- "-docs"}
miscdir=$(pwd)/%{installoutputdir -- "-misc"}

# Install release notes and rebuild instructions
commondocdir=${RPM_BUILD_ROOT}%{_defaultdocdir}/%{uniquejavadocdir -- $suffix}
install -d -m 755 ${commondocdir}
mv ${jdk_image}/NEWS ${commondocdir}
cp -a %{SOURCE19} %{SOURCE20} ${commondocdir}

# Install the jdk
mkdir -p $RPM_BUILD_ROOT%{_jvmdir}
cp -a ${jdk_image} $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}

%if %{with_systemtap}
  # Install systemtap support files
  install -dm 755 $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/tapset
  cp -a ${miscdir}/tapset$suffix/*.stp $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/tapset/
  pushd  $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/tapset/
   tapsetFiles=`ls *.stp`
  popd
  install -d -m 755 $RPM_BUILD_ROOT%{tapsetdir}
  for name in $tapsetFiles ; do
    targetName=`echo $name | sed "s/.stp/$suffix.stp/"`
    ln -sf %{_jvmdir}/%{sdkdir -- $suffix}/tapset/$name $RPM_BUILD_ROOT%{tapsetdir}/$targetName
  done
%endif

  # Remove empty cacerts database
  rm -f $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/lib/security/cacerts
  # Install cacerts symlink needed by some apps which hard-code the path
  pushd $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/lib/security
      ln -sf /etc/pki/java/cacerts .
  popd

  # Install version-ed symlinks
  pushd $RPM_BUILD_ROOT%{_jvmdir}
    ln -sf %{sdkdir -- $suffix} %{jrelnk -- $suffix}
  popd

  # Install man pages
  install -d -m 755 $RPM_BUILD_ROOT%{_mandir}/man1
  pushd ${jdk_image}
  for manpage in man/man1/*
  do
    # Convert man pages to UTF8 encoding
    iconv -f ISO_8859-1 -t UTF8 $manpage -o $manpage.tmp
    mv -f $manpage.tmp $manpage
    install -m 644 -p $manpage $RPM_BUILD_ROOT%{_mandir}/man1/$(basename \
      $manpage .1)-%{uniquesuffix -- $suffix}.1
  done
  # Remove man pages from jdk image
  rm -rf $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir -- $suffix}/man
  popd

if ! echo $suffix | grep -q "debug" ; then
    # Install Javadoc documentation
    install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}
    cp -a ${docdir}/docs $RPM_BUILD_ROOT%{_javadocdir}/%{uniquejavadocdir -- $suffix}
    built_doc_archive=jdk-%{filever}%{ea_designator_zip}+%{buildver}%{lts_designator_zip}-docs.zip
    cp -a ${docdir}/${built_doc_archive} \
        $RPM_BUILD_ROOT%{_javadocdir}/%{uniquejavadocdir -- $suffix}.zip || ls -l ${top_dir_abs_main_build_path}/bundles/
    touch $RPM_BUILD_ROOT%{_javadocdir}/%{uniquejavadocdir -- $suffix}.zip
fi

# Install icons and menu entries
for s in 16 24 32 48 ; do
  install -D -p -m 644 \
    ${miscdir}/java-icon${s}.png \
    $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${s}x${s}/apps/java-%{javaver}-%{origin}.png
done

# Install desktop files
# TODO: provide desktop files via portable
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/{applications,pixmaps}
for e in jconsole$suffix ; do
    desktop-file-install --vendor=%{uniquesuffix -- $suffix} --mode=644 \
        --dir=$RPM_BUILD_ROOT%{_datadir}/applications $e.desktop
done

# Install /etc/.java/.systemPrefs/ directory
# See https://bugzilla.redhat.com/show_bug.cgi?id=741821
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/.java/.systemPrefs

# copy samples next to demos; samples are mostly js files
cp -r ${miscdir}/sample  $RPM_BUILD_ROOT/%{_jvmdir}/%{sdkdir -- $suffix}/

# moving config files to /etc
mkdir -p $RPM_BUILD_ROOT/%{etcjavadir -- $suffix}
mkdir -p $RPM_BUILD_ROOT/%{etcjavadir -- $suffix}/lib
mv $RPM_BUILD_ROOT/%{_jvmdir}/%{sdkdir -- $suffix}/conf/  $RPM_BUILD_ROOT/%{etcjavadir -- $suffix}
mv $RPM_BUILD_ROOT/%{_jvmdir}/%{sdkdir -- $suffix}/lib/security  $RPM_BUILD_ROOT/%{etcjavadir -- $suffix}/lib
pushd $RPM_BUILD_ROOT/%{_jvmdir}/%{sdkdir -- $suffix}
  ln -s %{etcjavadir -- $suffix}/conf  ./conf
popd
pushd $RPM_BUILD_ROOT/%{_jvmdir}/%{sdkdir -- $suffix}/lib
  ln -s %{etcjavadir -- $suffix}/lib/security  ./security
popd
# end moving files to /etc

# stabilize permissions
find $RPM_BUILD_ROOT/%{_jvmdir}/%{sdkdir -- $suffix}/ -name "*.so" -exec chmod 755 {} \; ;
find $RPM_BUILD_ROOT/%{_jvmdir}/%{sdkdir -- $suffix}/ -type d -exec chmod 755 {} \; ;
find $RPM_BUILD_ROOT/%{_jvmdir}/%{sdkdir -- $suffix}/legal -type f -exec chmod 644 {} \; ;

# end, dual install
done

%if %{include_normal_build}
# intentionally only for non-debug
%pretrans headless -p <lua>
-- see https://bugzilla.redhat.com/show_bug.cgi?id=1038092 for whole issue
-- see https://bugzilla.redhat.com/show_bug.cgi?id=1290388 for pretrans over pre
-- if copy-jdk-configs is in transaction, it installs in pretrans to temp
-- if copy_jdk_configs is in temp, then it means that copy-jdk-configs is in transaction  and so is
-- preferred over one in %%{_libexecdir}. If it is not in transaction, then depends
-- whether copy-jdk-configs is installed or not. If so, then configs are copied
-- (copy_jdk_configs from %%{_libexecdir} used) or not copied at all
local posix = require "posix"

if (os.getenv("debug") == "true") then
  debug = true;
  print("cjc: in spec debug is on")
else
  debug = false;
end

SOURCE1 = "%{rpm_state_dir}/copy_jdk_configs.lua"
SOURCE2 = "%{_libexecdir}/copy_jdk_configs.lua"

local stat1 = posix.stat(SOURCE1, "type");
local stat2 = posix.stat(SOURCE2, "type");

  if (stat1 ~= nil) then
  if (debug) then
    print(SOURCE1 .." exists - copy-jdk-configs in transaction, using this one.")
  end;
  package.path = package.path .. ";" .. SOURCE1
else
  if (stat2 ~= nil) then
  if (debug) then
    print(SOURCE2 .." exists - copy-jdk-configs already installed and NOT in transaction. Using.")
  end;
  package.path = package.path .. ";" .. SOURCE2
  else
    if (debug) then
      print(SOURCE1 .." does NOT exists")
      print(SOURCE2 .." does NOT exists")
      print("No config files will be copied")
    end
  return
  end
end
-- run content of included file with fake args
arg = {"--currentjvm", "%{uniquesuffix %{nil}}", "--jvmdir", "%{_jvmdir %{nil}}", "--origname", "%{name}", "--origjavaver", "%{javaver}", "--arch", "%{_arch}", "--temp", "%{rpm_state_dir}/%{name}.%{_arch}"}
require "copy_jdk_configs.lua"

%post
%{post_script %{nil}}

%post headless
%{post_headless %{nil}}

%postun
%{postun_script %{nil}}

%postun headless
%{postun_headless %{nil}}

%posttrans
%{posttrans_script %{nil}}

%posttrans headless
%{alternatives_java_install %{nil}}

%post devel
%{post_devel %{nil}}

%postun devel
%{postun_devel %{nil}}

%posttrans  devel
%{posttrans_devel %{nil}}

%posttrans javadoc
%{alternatives_javadoc_install %{nil}}

%postun javadoc
%{postun_javadoc %{nil}}

%posttrans javadoc-zip
%{alternatives_javadoczip_install %{nil}}

%postun javadoc-zip
%{postun_javadoc_zip %{nil}}
%endif

%if %{include_debug_build}
%post slowdebug
%{post_script -- %{debug_suffix_unquoted}}

%post headless-slowdebug
%{post_headless -- %{debug_suffix_unquoted}}

%posttrans headless-slowdebug
%{alternatives_java_install -- %{debug_suffix_unquoted}}

%postun slowdebug
%{postun_script -- %{debug_suffix_unquoted}}

%postun headless-slowdebug
%{postun_headless -- %{debug_suffix_unquoted}}

%posttrans slowdebug
%{posttrans_script -- %{debug_suffix_unquoted}}

%post devel-slowdebug
%{post_devel -- %{debug_suffix_unquoted}}

%postun devel-slowdebug
%{postun_devel -- %{debug_suffix_unquoted}}

%posttrans  devel-slowdebug
%{posttrans_devel -- %{debug_suffix_unquoted}}
%endif

%if %{include_fastdebug_build}
%post fastdebug
%{post_script -- %{fastdebug_suffix_unquoted}}

%post headless-fastdebug
%{post_headless -- %{fastdebug_suffix_unquoted}}

%postun fastdebug
%{postun_script -- %{fastdebug_suffix_unquoted}}

%postun headless-fastdebug
%{postun_headless -- %{fastdebug_suffix_unquoted}}

%posttrans fastdebug
%{posttrans_script -- %{fastdebug_suffix_unquoted}}

%posttrans headless-fastdebug
%{alternatives_java_install -- %{fastdebug_suffix_unquoted}}

%post devel-fastdebug
%{post_devel -- %{fastdebug_suffix_unquoted}}

%postun devel-fastdebug
%{postun_devel -- %{fastdebug_suffix_unquoted}}

%posttrans  devel-fastdebug
%{posttrans_devel -- %{fastdebug_suffix_unquoted}}

%endif

%if %{include_normal_build}
%files
# main package builds always
%{files_jre %{nil}}
%else
%files
# placeholder
%endif


%if %{include_normal_build}
%files headless
# important note, see https://bugzilla.redhat.com/show_bug.cgi?id=1038092 for whole issue
# all config/noreplace files (and more) have to be declared in pretrans. See pretrans
%{files_jre_headless %{nil}}

%files devel
%{files_devel %{nil}}

%if %{include_staticlibs}
%files static-libs
%{files_static_libs %{nil}}
%endif

%files jmods
%{files_jmods %{nil}}

%files demo
%{files_demo %{nil}}

%files src
%{files_src %{nil}}

%files javadoc
%{files_javadoc %{nil}}

# This puts a huge documentation file in /usr/share
# It is now architecture-dependent, as eg. AOT and Graal are now x86_64 only
# same for debug variant
%files javadoc-zip
%{files_javadoc_zip %{nil}}
%endif

%if %{include_debug_build}
%files slowdebug
%{files_jre -- %{debug_suffix_unquoted}}

%files headless-slowdebug
%{files_jre_headless -- %{debug_suffix_unquoted}}

%files devel-slowdebug
%{files_devel -- %{debug_suffix_unquoted}}

%if %{include_staticlibs}
%files static-libs-slowdebug
%{files_static_libs -- %{debug_suffix_unquoted}}
%endif

%files jmods-slowdebug
%{files_jmods -- %{debug_suffix_unquoted}}

%files demo-slowdebug
%{files_demo -- %{debug_suffix_unquoted}}

%files src-slowdebug
%{files_src -- %{debug_suffix_unquoted}}
%endif

%if %{include_fastdebug_build}
%files fastdebug
%{files_jre -- %{fastdebug_suffix_unquoted}}

%files headless-fastdebug
%{files_jre_headless -- %{fastdebug_suffix_unquoted}}

%files devel-fastdebug
%{files_devel -- %{fastdebug_suffix_unquoted}}

%if %{include_staticlibs}
%files static-libs-fastdebug
%{files_static_libs -- %{fastdebug_suffix_unquoted}}
%endif

%files jmods-fastdebug
%{files_jmods -- %{fastdebug_suffix_unquoted}}

%files demo-fastdebug
%{files_demo -- %{fastdebug_suffix_unquoted}}

%files src-fastdebug
%{files_src -- %{fastdebug_suffix_unquoted}}

%endif

%changelog
* Wed Apr 10 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.9-2
- Update to jdk-17.0.11+9 (GA)
- Add openjdk-17.0.11+9.tar.xz to .gitignore
- Sync java-17-openjdk-portable.specfile from openjdk-portable-rhel-8
- Update buildver from 7 to 9
- Update portablerelease from 1 to 3
- Change is_ga from 0 to 1 to enable GA mode for release
- Update tzdata Requires comment to mention that 2024a is not yet in the buildroot
- Update tzdata BuildRequires comment to mention that 2024a is not yet in the buildroot
- Update tzdata BuildRequires fro 2023c to 2023d
- Update sources from openjdk-17.0.11+7-ea.tar.xz to openjdk-17.0.11+9.tar.xz
- Resolves: RHEL-27137
- ** This tarball is embargoed until 2024-04-16 @ 1pm PT. **

* Thu Mar 28 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.7-0.2.ea
- Update to jdk-17.0.11+7 (EA)
- Sync java-17-openjdk-portable.specfile
- Sync java-17-openjdk-portable.specfile again to mention OPENJDK-2730
- Related: RHEL-27137

* Thu Mar 14 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.11.0.6-0.2.ea
- Update to jdk-17.0.11+6 (EA)
- Sync java-17-openjdk-portable.specfile
- Update buildjdkver to match the featurever
- Use featurever macro to specify fips patch
- Explain patchN syntax situation in a comment
- generate_source_tarball.sh: Fix whitespace
- generate_source_tarball.sh: Skip -ga tags
- generate_source_tarball.sh: Get -ea suffix from version-numbers.conf
- generate_source_tarball.sh: Use git archive to generate tarball
- generate_source_tarball.sh: Update version in comment
- generate_source_tarball.sh: Remove trailing period in echo
- generate_source_tarball.sh: Add indentation instructions for Emacs
- Require tzdata 2023d (JDK-8322725)
- generate_source_tarball.sh: Add license
- openjdk_news.sh: Use grep -E instead of egrep
- Remove RH1649512 patch for libjpeg-turbo FAR macro
- Move pcsc-lite-libs patch to in-need-of-upstreaming section
- Related: RHEL-27137

* Thu Jan 11 2024 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.10.0.7-1
- Update to jdk-17.0.10+7 (GA)
- Sync the copy of the portable specfile with the latest update
- Move to -P<n> usage for patch macro which works on all RPM versions
- Remove RH1648644 patch not in portable build (and so not applied to binary used)
- Re-enable DEFAULT_PROMOTED_VERSION_PRE check disabled for the July 2023 release
- generate_source_tarball.sh: Add --sort=name to tar invocation for reproducibility
- ** This tarball is embargoed until 2024-01-16 @ 1pm PT. **
- Resolves: RHEL-20969

* Thu Jan 11 2024 Thomas Fitzsimmons <fitzsim@redhat.com> - 1:17.0.10.0.7-1
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
- generate_source_tarball.sh: Add note on network usage of OPENJDK_LATEST
- Related: RHEL-20969

* Thu Oct 12 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.9.0.9-1
- Update to jdk-17.0.9+9 (GA)
- Sync the copy of the portable specfile with the latest update
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
- Add missing JFR and jpackage alternative ghosts
- Move jcmd to the headless package
- ** This tarball is embargoed until 2023-10-17 @ 1pm PT. **
- Resolves: RHEL-12204
- Resolves: RHEL-13670
- Resolves: RHEL-13680
- Resolves: RHEL-13689
- Resolves: RHEL-13708
- Resolves: RHEL-13658

* Mon Sep 04 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.8.1.1-2
- Bump release number so we are newer than 9.0
- Related: rhbz#2236591

* Sat Sep 02 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.8.1.1-1
- Update to jdk-17.0.8.1+1 (GA)
- Update release notes to 17.0.8.1+1
- Add backport of JDK-8312489 already upstream in 17.0.10 (see OPENJDK-2095)
- Update openjdk_news script to specify subdirectory last
- Add missing discover_trees script required by openjdk_news
- Synchronise runtime and buildtime tzdata requirements
- Resolves: rhbz#2236591

* Wed Jul 19 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.8.0.7-2
- Bump release number so we are newer than 8.6
- Related: rhbz#2221106

* Fri Jul 14 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.8.0.7-1
- Update to jdk-17.0.8+7 (GA)
- Update release notes to 17.0.8+7
- Switch to GA mode for final release.
- Sync the copy of the portable specfile with the latest update
- Add note at top of spec file about rebuilding
- * This tarball is embargoed until 2023-07-18 @ 1pm PT. *
- Resolves: rhbz#2221106

* Thu Jul 13 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.8.0.6-0.1.ea
- Update to jdk-17.0.8+6 (EA)
- Sync the copy of the portable specfile with the latest update
- Resolves: rhbz#2217714

* Wed Jul 12 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.8.0.1-0.1.ea
- Update to jdk-17.0.8+1 (EA)
- Update release notes to 17.0.8+1
- Switch to EA mode
- Drop local inclusion of JDK-8274864 & JDK-8305113 as they are included in 17.0.8+1
- Bump bundled LCMS version to 2.15 as in jdk-17.0.8+1.
- Bump bundled HarfBuzz version to 7.0.1 as in jdk-17.0.8+1
- Use tapsets from the misc tarball
- Introduce 'prelease' for the portable release versioning, to handle EA builds
- Make sure root installation directory is created first
- Use in-place substitution for all but the first of the tapset changes
- Related: rhbz#2217714

* Tue Jul 11 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.7.0.7-4
- Introduce vm_variant global for consistency with future JDK builds
- Related: rhbz#2196908

* Mon May 15 2023 Jiri Vanek <jvanek@redhat.com> - 1:17.0.7.0.7-4
- Exclude classes_nocoops.jsa on i686 and arm32
- Related: rhbz#2196908

* Mon May 15 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.7.0.7-4
- Following JDK-8005165, class data sharing can be enabled on all JIT architectures
- Related: rhbz#2196908

* Wed May 10 2023 Severin Gehwolf <sgehwolf@redhat.com> - 1:17.0.7.0.7-4
- Fix packaging of CDS archives
- Resolves: rhbz#2196908

* Wed Apr 26 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.7.0.7-3
- Sync portable spec file with current version
- Related: rhbz#2189330

* Wed Apr 26 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.7.0.7-2
- Update to jdk-17.0.7.0+7
- Update release notes to 17.0.7.0+7
- Require tzdata 2023c due to local inclusion of JDK-8274864 & JDK-8305113
- Update generate_tarball.sh to add support for passing a boot JDK to the configure run
- Add POSIX-friendly error codes to generate_tarball.sh and fix whitespace
- Remove .jcheck and GitHub support when generating tarballs, as done in upstream release tarballs
- Update FIPS support against 17.0.7+6 and bring in latest changes:
- * RH2134669: Add missing attributes when registering services in FIPS mode.
- * test/jdk/sun/security/pkcs11/fips/VerifyMissingAttributes.java: fixed jtreg main class
- * RH1940064: Enable XML Signature provider in FIPS mode
- * RH2173781: Avoid calling C_GetInfo() too early, before cryptoki is initialized
- Fix trailing '.' in tarball name
- Use portablerelease in vendor version to avoid inclusion of dist tag
- ** This tarball is embargoed until 2023-04-18 @ 1pm PT. **
- Resolves: rhbz#2185182
- Resolves: rhbz#2186834
- Resolves: rhbz#2186826
- Resolves: rhbz#2186830

* Wed Apr 26 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.6.0.10-6
- Include the java-17-openjdk-portable.spec file with instructions on how to rebuild.
- Related: rhbz#2189330

* Tue Apr 25 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.6.0.10-5
- Replace local copies of JDK portable binaries with build dependencies
- Resolves: rhbz#2189330

* Wed Feb 15 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.6.0.10-4
- Replace build section with extraction of existing builds from portables
- Rewrite ELF files so the source file path is correct and debugsources can be assembled
- Resolves: rhbz#2150205

* Fri Jan 20 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.6.0.10-3
- Update to jdk-17.0.6.0+10
- Update release notes to 17.0.6.0+10
- Switch to GA mode for release
- Resolves: rhbz#2160111

* Fri Jan 13 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.6.0.9-0.4.ea
- Update FIPS support to bring in latest changes
- * OJ1357: Fix issue on FIPS with a SecurityManager in place
- Related: rhbz#2117972

* Fri Jan 13 2023 Stephan Bergmann <sbergman@redhat.com> - 1:17.0.6.0.9-0.4.ea
- Fix flatpak builds by disabling TestTranslations test due to missing tzdb.dat
- Related: rhbz#2150195

* Wed Jan 04 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.6.0.9-0.3.ea
- Update to jdk-17.0.6+9
- Update release notes to 17.0.6+9
- Drop local copy of JDK-8293834 now this is upstream
- Require tzdata 2022g due to inclusion of JDK-8296108, JDK-8296715 & JDK-8297804
- Update TestTranslations.java to test the new America/Ciudad_Juarez zone
- Resolves: rhbz#2150195

* Sat Dec 03 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.6.0.1-0.3.ea
- Update to jdk-17.0.6+1
- Update release notes to 17.0.6+1
- Switch to EA mode for 17.0.6 pre-release builds.
- Re-enable EA upstream status check now it is being actively maintained.
- Drop JDK-8294357 (tzdata2022d) & JDK-8295173 (tzdata2022e) local patches which are now upstream
- Drop JDK-8275535 local patch now this has been accepted and backported upstream
- Bump tzdata requirement to 2022e now the package is available in RHEL
- Related: rhbz#2150195

* Wed Nov 23 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.5.0.8-5
- Update FIPS support to bring in latest changes
- * Add nss.fips.cfg support to OpenJDK tree
- * RH2117972: Extend the support for NSS DBs (PKCS11) in FIPS mode
- * Remove forgotten dead code from RH2020290 and RH2104724
- Drop local nss.fips.cfg.in handling now this is handled in the patched OpenJDK build
- Resolves: rhbz#2117972

* Wed Oct 26 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.5.0.8-2
- Update to jdk-17.0.5+8 (GA)
- Update release notes to 17.0.5+8 (GA)
- Switch to GA mode for final release.
- Update in-tree tzdata to 2022e with JDK-8294357 & JDK-8295173
- Update CLDR data with Europe/Kyiv (JDK-8293834)
- Drop JDK-8292223 patch which we found to be unnecessary
- Update TestTranslations.java to use public API based on TimeZoneNamesTest upstream
- The stdc++lib, zlib & freetype options should always be set from the global, so they are not altered for staticlibs builds
- Remove freetype sources along with zlib sources
- Resolves: rhbz#2133695

* Tue Oct 04 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.5.0.7-0.2.ea
- Update to jdk-17.0.5+7
- Update release notes to 17.0.5+7
- Drop JDK-8288985 patch that is now upstream
- Resolves: rhbz#2130617

* Mon Oct 03 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.5.0.1-0.2.ea
- Update to jdk-17.0.5+1
- Update release notes to 17.0.5+1
- Switch to EA mode for 17.0.5 pre-release builds.
- Bump HarfBuzz bundled version to 4.4.1 following JDK-8289853
- Bump FreeType bundled version to 2.12.1 following JDK-8290334
- Related: rhbz#2130617

* Tue Aug 30 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.4.1.1-6
- Backport JDK-8288985 to enable use of ChaCha20-Poly1305 with the PKCS11 provider
- Upstream backport in progress: https://github.com/openjdk/jdk17u-dev/pull/650
- Resolves: rhbz#2006351

* Tue Aug 30 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.4.1.1-5
- Switch to static builds, reducing system dependencies and making build more portable
- Resolves: rhbz#2121263

* Mon Aug 29 2022 Stephan Bergmann <sbergman@redhat.com> - 1:17.0.4.1.1-4
- Fix flatpak builds (catering for their uncompressed manual pages)
- Fix flatpak builds by exempting them from bootstrap
- Resolves: rhbz#2102734

* Mon Aug 29 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.4.1.1-3
- Update FIPS support to bring in latest changes
- * RH2104724: Avoid import/export of DH private keys
- * RH2092507: P11Key.getEncoded does not work for DH keys in FIPS mode
- * Build the systemconf library on all platforms
- * RH2048582: Support PKCS#12 keystores
- * RH2020290: Support TLS 1.3 in FIPS mode
- Resolves: rhbz#2104724
- Resolves: rhbz#2092507
- Resolves: rhbz#2048582
- Resolves: rhbz#2020290

* Sun Aug 21 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.4.1.1-2
- Update to jdk-17.0.4.1+1
- Update release notes to 17.0.4.1+1
- Add patch to provide translations for Europe/Kyiv added in tzdata2022b
- Add test to ensure timezones can be translated
- Resolves: rhbz#2119531

* Fri Jul 22 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.4.0.8-3
- Update to jdk-17.0.4.0+8
- Update release notes to 17.0.4.0+8
- Switch to GA mode for release
- Resolves: rhbz#2106522

* Wed Jul 20 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.4.0.7-0.2.ea
- Revert the following changes until copy-java-configs has adapted to relative symlinks:
- * Move cacerts replacement to install section and retain original of this and tzdb.dat
- * Run tests on the installed image, rather than the build image
- * Introduce variables to refer to the static library installation directories
- * Use relative symlinks so they work within the image
- * Run debug symbols check during build stage, before the install strips them
- The move of turning on system security properties is retained so we don't ship with them off
- Related: rhbz#2100674

* Wed Jul 20 2022 Jiri Vanek <jvanek@redhat.com> - 1:17.0.4.0.7-0.2.ea
- retutrned absolute symlinks
- relative symlinks are breaking cjc, and deeper investigations are necessary
-- why cjc intentionally skips relative symllinks
- images have to be workarounded differently
- Related: rhbz#2100674

* Sat Jul 16 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.4.0.7-0.1.ea
- Update to jdk-17.0.4.0+7
- Update release notes to 17.0.4.0+7
- Switch to EA mode for 17.0.4 pre-release builds.
- Need to include the '.S' suffix in debuginfo checks after JDK-8284661
- Print release file during build, which should now include a correct SOURCE value from .src-rev
- Update tarball script with IcedTea GitHub URL and .src-rev generation
- Include script to generate bug list for release notes
- Update tzdata requirement to 2022a to match JDK-8283350
- Move EA designator check to prep so failures can be caught earlier
- Make EA designator check non-fatal while upstream is not maintaining it
- Explicitly require crypto-policies during build and runtime for system security properties
- Make use of the vendor version string to store our version & release rather than an upstream release date
- Include a test in the RPM to check the build has the correct vendor information.
- Resolves: rhbz#2083316

* Thu Jul 14 2022 Jayashree Huttanagoudar <jhuttana@redhat.com> - 1:17.0.4.0.1-0.2.ea
- Fix issue where CheckVendor.java test erroneously passes when it should fail.
- Add proper quoting so '&' is not treated as a special character by the shell.
- Related: rhbz#2083316

* Fri Jul 08 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.3.0.7-6
- Fix whitespace in spec file
- Related: rhbz#2100674

* Fri Jul 08 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.3.0.7-6
- Sequence spec file sections as they are run by rpmbuild (build, install then test)
- Related: rhbz#2100674

* Fri Jul 08 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.3.0.7-6
- Turn on system security properties as part of the build's install section
- Move cacerts replacement to install section and retain original of this and tzdb.dat
- Run tests on the installed image, rather than the build image
- Introduce variables to refer to the static library installation directories
- Use relative symlinks so they work within the image
- Run debug symbols check during build stage, before the install strips them
- Related: rhbz#2100674

* Thu Jun 30 2022 Francisco Ferrari Bihurriet <fferrari@redhat.com> - 1:17.0.3.0.7-5
- RH2007331: SecretKey generate/import operations don't add the CKA_SIGN attribute in FIPS mode
- Resolves: rhbz#2007331

* Tue Jun 28 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.3.0.7-4
- Update FIPS support to bring in latest changes
- * RH2036462: sun.security.pkcs11.wrapper.PKCS11.getInstance breakage
- * RH2090378: Revert to disabling system security properties and FIPS mode support together
- Rebase RH1648249 nss.cfg patch so it applies after the FIPS patch
- Enable system security properties in the RPM (now disabled by default in the FIPS repo)
- Improve security properties test to check both enabled and disabled behaviour
- Run security properties test with property debugging on
- Resolves: rhbz#2099840
- Resolves: rhbz#2100674

* Tue Jun 28 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.3.0.7-3
- Add rpminspect.yaml to turn off Java bytecode inspections
- java-17-openjdk deliberately produces Java 17 bytecode, not the default Java 11 bytecode
- Resolves: rhbz#2101524

* Sun Jun 12 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.3.0.7-2
- Rebase FIPS patches from fips-17u branch and simplify by using a single patch from that repository
- Rebase RH1648249 nss.cfg patch so it applies after the FIPS patch
- RH2023467: Enable FIPS keys export
- RH2094027: SunEC runtime permission for FIPS
- Resolves: rhbz#2023467
- Resolves: rhbz#2094027

* Wed Apr 20 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.3.0.7-1
- April 2022 security update to jdk 17.0.3+7
- Update to jdk-17.0.3.0+7 release tarball
- Update release notes to 17.0.3.0+6
- Add missing README.md and generate_source_tarball.sh
- Switch to GA mode for release
- JDK-8283911 patch no longer needed now we're GA...
- Resolves: rhbz#2073577

* Wed Apr 06 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.3.0.5-0.1.ea
- Update to jdk-17.0.3.0+5
- Update release notes to 17.0.3.0+5
- Resolves: rhbz#2050456

* Tue Mar 29 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.3.0.1-0.1.ea
- Update to jdk-17.0.3.0+1
- Update release notes to 17.0.3.0+1
- Switch to EA mode for 17.0.3 pre-release builds.
- Add JDK-8283911 to fix bad DEFAULT_PROMOTED_VERSION_PRE value
- Related: rhbz#2050456

* Mon Feb 28 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.2.0.8-15
- Enable AlgorithmParameters and AlgorithmParameterGenerator services in FIPS mode
- Resolves: rhbz#2052070

* Sun Feb 27 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.2.0.8-14
- Introduce tests/tests.yml, based on the one in java-11-openjdk
- Resolves: rhbz#2058493

* Sun Feb 27 2022 Severin Gehwolf <sgehwolf@redhat.com> - 1:17.0.2.0.8-13
- Use 'sql:' prefix in nss.fips.cfg as F35+ no longer ship the legacy
  secmod.db file as part of nss
- Resolves: rhbz#2023536

* Sun Feb 27 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.2.0.8-12
- Detect NSS at runtime for FIPS detection
- Turn off build-time NSS linking and go back to an explicit Requires on NSS
- Resolves: rhbz#2051605

* Fri Feb 25 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.2.0.8-11
- Add JDK-8275535 patch to fix LDAP authentication issue.
- Resolves: rhbz#2053256

* Fri Feb 25 2022 Jiri Vanek <jvanek@redhat.com> - 1:17.0.2.0.8-10
- Storing and restoring alterntives during update manually
- Fixing Bug 2001567 - update of JDK/JRE is removing its manually selected alterantives and select (as auto) system JDK/JRE
-- The move of alternatives creation to posttrans to fix:
-- Bug 1200302 - dnf reinstall breaks alternatives
-- Had caused the alternatives to be removed, and then created again,
-- instead of being added, and then removing the old, and thus persisting
-- the selection in family
-- Thus this fix, is storing the family of manually selected master, and if
-- stored, then it is restoring the family of the master
- Resolves: rhbz#2008200

* Fri Feb 25 2022 Jiri Vanek <jvanek@redhat.com> - 1:17.0.2.0.8-9
- Family extracted to globals
- Resolves: rhbz#2008200

* Fri Feb 25 2022 Jiri Vanek <jvanek@redhat.com> - 1:17.0.2.0.8-8
- alternatives creation moved to posttrans
- Thus fixing the old reisntall issue:
- https://bugzilla.redhat.com/show_bug.cgi?id=1200302
- https://bugzilla.redhat.com/show_bug.cgi?id=1976053
- Resolves: rhbz#2008200

* Mon Feb 21 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.2.0.8-7
- Separate crypto policy initialisation from FIPS initialisation, now they are no longer interdependent
- Resolves: rhbz#2051590

* Fri Feb 18 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.2.0.8-6
- Fix FIPS issues in native code and with initialisation of java.security.Security
- Resolves: rhbz#2023378

* Thu Feb 17 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.2.0.8-5
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

* Thu Feb 17 2022 Jiri Vanek <jvanek@redhat.com> - 1:17.0.2.0.8-5
- Replaced tabs by sets of spaces to make rpmlint happy
- javadoc-zip gets its own provides next to plain javadoc ones
- Resolves: rhbz#2022822

* Tue Feb 08 2022 Jiri Vanek <jvanek@redhat.com> - 1:17.0.2.0.8-4
- Minor cosmetic improvements to make spec more comparable between variants
- Related: rhbz#2022822

* Thu Feb 03 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.2.0.8-3
- Update tapsets from IcedTea 6.x repository with fix for JDK-8015774 changes (_heap->_heaps) and @JAVA_SPEC_VER@
- Update icedtea_sync.sh with a VCS mode that retrieves sources from a Mercurial repository
- Related: rhbz#2022822

* Thu Feb 03 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.2.0.8-2
- Extend LTS check to exclude EPEL.
- Related: rhbz#2022822

* Thu Feb 03 2022 Severin Gehwolf <sgehwolf@redhat.com> - 1:17.0.2.0.8-2
- Set LTS designator.
- Related: rhbz#2022822

* Wed Jan 12 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.2.0.8-1
- January 2022 security update to jdk 17.0.2+8
- Rebase RH1995150 & RH1996182 patches following JDK-8275863 addition to module-info.java
- Rename libsvml.so to libjsvml.so following JDK-8276025
- Resolves: rhbz#2039366

* Thu Oct 28 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.1.0.12-3
- Sync desktop files with upstream IcedTea release 3.15.0 using new script
- Related: rhbz#2013842

* Tue Oct 26 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.1.0.12-2
- Drop JDK-8272332/RH2004078 patch which is upstream in 17.0.1
- Resolves: rhbz#2013842

* Wed Oct 20 2021 Petra Alice Mikova <pmikova@redhat.com> - 1:17.0.1.0.12-2
- October CPU update to jdk 17.0.1+12
- Dropped commented-out source line
- Resolves: rhbz#2013842

* Sun Oct 10 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.0.0.35-6
- Allow plain key import to be disabled with -Dcom.redhat.fips.plainKeySupport=false
- Resolves: rhbz#1994661

* Sun Oct 10 2021 Martin Balao <mbalao@redhat.com> - 1:17.0.0.0.35-6
- Add patch to allow plain key import.
- Resolves: rhbz#1994661

* Mon Sep 27 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.0.0.35-5
- Update release notes to document the major changes between OpenJDK 11 & 17.
- Resolves: rhbz#2003072

* Thu Sep 16 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.0.0.35-3
- Update to jdk-17+35, also known as jdk-17-ga.
- Switch to GA mode.
- Add JDK-8272332 fix so we actually link against HarfBuzz.
- Resolves: rhbz#2003072
- Resolves: rhbz#2004078

* Mon Aug 30 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.0.0.33-0.5.ea
- Extend the default security policy to accomodate PKCS11 accessing jdk.internal.access.
- Resolves: rhbz#1996182

* Sat Aug 28 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.0.0.33-0.4.ea
- Fix unused function compiler warning found in systemconf.c
- Related: rhbz#1995150

* Sat Aug 28 2021 Martin Balao <mbalao@redhat.com> - 1:17.0.0.0.33-0.4.ea
- Add patch to login to the NSS software token when in FIPS mode.
- Resolves: rhbz#1996182

* Fri Aug 27 2021 Martin Balao <mbalao@redhat.com> - 1:17.0.0.0.33-0.3.ea
- Add patch to disable non-FIPS crypto in the SUN and SunEC security providers.
- Resolves: rhbz#1995150

* Fri Aug 27 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.0.0.33-0.2.ea
- Minor code cleanups on FIPS detection patch and check for SECMOD_GetSystemFIPSEnabled in configure.
- Remove unneeded Requires on NSS as it will now be dynamically linked and detected by RPM.
- Related: rhbz#1995150

* Fri Aug 27 2021 Martin Balao <mbalao@redhat.com> - 1:17.0.0.0.33-0.2.ea
- Detect FIPS using SECMOD_GetSystemFIPSEnabled in the new libsystemconf JDK library.
- Related: rhbz#1995150

* Thu Aug 26 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.0.0.33-0.1.ea
- Update RH1655466 FIPS patch with changes in OpenJDK 8 version.
- SunPKCS11 runtime provider name is a concatenation of "SunPKCS11-" and the name in the config file.
- Change nss.fips.cfg config name to "NSS-FIPS" to avoid confusion with nss.cfg.
- No need to substitute path to nss.fips.cfg as java.security file supports a java.home variable.
- Disable FIPS mode support unless com.redhat.fips is set to "true".
- Enable alignment with FIPS crypto policy by default (-Dcom.redhat.fips=false to disable).
- Add explicit runtime dependency on NSS for the PKCS11 provider in FIPS mode
- Move setup of JavaSecuritySystemConfiguratorAccess to Security class so it always occurs (RH1915071)
- Related: rhbz#1995150

* Thu Aug 26 2021 Martin Balao <mbalao@redhat.com> - 1:17.0.0.0.33-0.1.ea
- Support the FIPS mode crypto policy (RH1655466)
- Use appropriate keystore types when in FIPS mode (RH1818909)
- Disable TLSv1.3 when the FIPS crypto policy and the NSS-FIPS provider are in use (RH1860986)
- Related: rhbz#1995150

* Thu Aug 26 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.0.0.33-0.0.ea
- Update to jdk-17+33, including JDWP fix and July 2021 CPU
- Resolves: rhbz#1959487

* Thu Aug 26 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.0.0.26-0.5.ea
- Use the "reverse" build loop (debug first) as the main and only build loop to get more diagnostics.
- Remove restriction on disabling product build, as debug packages no longer have javadoc packages.
- Resolves: rhbz#1959487

* Wed Aug 25 2021 Petra Alice Mikova <pmikova@redhat.com> - 1:17.0.0.0.26-0.4.ea
- Fix patch rh1648249-add_commented_out_nss_cfg_provider_to_java_security.patch which made the SunPKCS provider show up again
- Resolves: rhbz#1959487

* Wed Aug 25 2021 Severin Gehwolf <sgehwolf@redhat.com> - 1:17.0.0.0.26-0.3.ea
- Re-enable TestSecurityProperties after inclusion of PR3695
- Resolves: rhbz#1959487

* Wed Aug 25 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.0.0.26-0.3.ea
- Add PR3695 to allow the system crypto policy to be turned off
- Resolves: rhbz#1959487

* Wed Jul 14 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.0.0.26-0.2.ea
- Remove boot JDKs in favour of OpenJDK 17 build now in the buildroot.
- Resolves: rhbz#1959487

* Wed Jul 14 2021 Severin Gehwolf <sgehwolf@redhat.com> - 1:17.0.0.0.26-0.2.ea
- Update buildjdkver to 17 so as to build with itself
- Resolves: rhbz#1959487

* Tue Jul 13 2021 Jiri Vanek <jvanek@redhat.com> - 1:17.0.0.0.26-0.1.ea
- Add gating support
- Resolves: rhbz#1959487

* Mon Jun 21 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:17.0.0.0.26-0.0.ea
- Rename as java-17-openjdk and bootstrap using boot JDK in local sources
- Exclude x86 as this is not supported by OpenJDK 17
- Resolves: rhbz#1959487

* Fri Jun 11 2021 Petra Alice Mikova <pmikova@redhat.com> - 1:17.0.0.0.26-0.0.ea.rolling
- update sources to jdk 17.0.0+26
- set is_ga to 0, as this is early access build
- change vendor_version_string
- change path to the version-numbers.conf
- removed rmid binary from files and from slaves
- removed JAVAC_FLAGS=-g from make command, as it breaks the build since JDK-8258407
- add lib/libsyslookup.so to files
- renamed lib/security/blacklisted.certs to lib/security/blocked.certs
- add lib/libsvml.so for intel
- skip debuginfo check for libsyslookup.so on s390x

* Thu Apr 29 2021 Jiri Vanek <jvanek@redhat.com> -  1:16.0.1.0.9-2.rolling
- adapted to debug handling  in newer cjc
- The rest of the "rpm 4.17" patch must NOT be backported, as on rpm 4.16 and down, it would casue double execution
- Disable copy-jdk-configs for Flatpak builds

* Sun Apr 25 2021 Petra Alice Mikova <pmikova@redhat.com> - 1:16.0.1.0.9-1.rolling
- update to 16.0.1+9 april cpu tag
- dropped jdk8259949-allow_cf-protection_on_x86.patch

* Thu Mar 11 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:16.0.0.0.36-2.rolling
- Perform static library build on a separate source tree with bundled image libraries
- Make static library build optional
- Based on initial work by Severin Gehwolf

* Tue Mar 09 2021 Jiri Vanek <jvanek@redhat.com> - 1:16.0.0.0.36-1.rolling
- fixed suggests of wrong pcsc-lite-devel%{?_isa} to correct pcsc-lite-libs%{?_isa}
- bumped buildjdkver to build by itself - 16

* Fri Feb 19 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:16.0.0.0.36-0.rolling
- Update to jdk-16.0.0.0+36
- Update tarball generation script to use git following OpenJDK's move to github
- Update tarball generation script to use PR3823 which handles JDK-8235710 changes
- Use upstream default for version-pre rather than setting it to "ea" or ""
- Drop libsunec.so which is no longer generated, thanks to JDK-8235710
- Drop unnecessary compiler flags, dating back to work on GCC 6 & 10
- Adapt RH1750419 alt-java patch to still apply after some variable re-naming in the makefiles
- Update filever to remove any trailing zeros, as in the OpenJDK build, and use for source filename
- Use system harfbuzz now this is supported.
- Pass SOURCE_DATE_EPOCH to build for reproducible builds

* Fri Feb 19 2021 Stephan Bergmann <sbergman@redhat.com> - 1:15.0.2.0.7-1.rolling
- Hardcode /usr/sbin/alternatives for Flatpak builds

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1:15.0.2.0.7-0.rolling.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Fri Jan 22 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:15.0.2.0.7-0.rolling
- Update to jdk-15.0.2.0+7
- Add release notes for 15.0.1.0 & 15.0.2.0
- Use JEP-322 Time-Based Versioning so we can handle a future 11.0.9.1-like release correctly.
- Still use 15.0.x rather than 15.0.x.0 for file naming, as the trailing zero is omitted from tags.
- Cleanup debug package descriptions and version number placement.
- Remove unused patch files.

* Tue Jan 19 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:15.0.1.9-10.rolling
- Use -march=i686 for x86 builds if -fcf-protection is detected (needs CMOV)

* Tue Dec 22 2020 Jiri Vanek <jvanek@redhat.com> - 1:15.0.1.9-9.rolling
- fixed missing condition for fastdebug packages being counted as debug ones

* Sat Dec 19 2020 Jiri Vanek <jvanek@redhat.com> - 1:15.0.1.9-8.rolling
- removed lib-style provides for fastdebug_suffix_unquoted

* Sat Dec 19 2020 Jiri Vanek <jvanek@redhat.com> - 1:15.0.1.9-6.rolling
- many cosmetic changes taken from more maintained jdk11
- introduced debug_arches, bootstrap_arches, systemtap_arches, fastdebug_arches, sa_arches, share_arches, shenandoah_arches, zgc_arches
  instead of various hardcoded ifarches
- updated systemtap
- added requires excludes for debug pkgs
- removed redundant logic around jsa files
- added runtime requires of lksctp-tools and libXcomposite%
- added and used Source15 TestSecurityProperties.java, but is made always positive as jdk15 now does not honor system policies
- s390x excluded form fastdebug build

* Thu Dec 17 2020 Andrew Hughes <gnu.andrew@redhat.com> - 1:15.0.1.9-5.rolling
- introduced nm based check to verify alt-java on x86_64 is patched, and no other alt-java or java is patched
- patch600 rh1750419-redhat_alt_java.patch amended to die, if it is used wrongly
- introduced ssbd_arches with currently only valid arch of x86_64 to separate real alt-java architectures

* Wed Dec 9 2020 Jiri Vanek <jvanek@redhat.com> - 1:15.0.1.9-4.rolling
- moved wrongly placed licenses to accompany other ones
- this bad placement was killng parallel-installability and thus having bad impact to leapp if used

* Tue Dec 01 2020 Jiri Vanek <jvanek@redhat.com> - 1:15.0.1.9-3.rolling
- added patch600, rh1750419-redhat_alt_java.patch, suprassing removed patch
- no longer copying of java->alt-java as it is created by  patch600

* Mon Nov 23 2020 Jiri Vanek <jvanek@redhat.com> - 1:15.0.1.9-2.rolling
- Create a copy of java as alt-java with alternatives and man pages
- java-11-openjdk doesn't have a JRE tree, so don't try and copy alt-java there...

* Sun Oct 25 2020 Petra Alice Mikova <pmikova@redhat.com> - 1:15.0.1.9-1.rolling
- updated to October CPU 2020 sources

* Thu Oct 22 2020 Severin Gehwolf <sgehwolf@redhat.com> - 1:15.0.0.36-4.rolling
- Fix directory ownership of -static-libs sub-package.

* Fri Oct 09 2020 Jiri Vanek <jvanek@redhat.com> - 1:15.0.0.36-3.rolling
- Build static-libs-image and add resulting files via -static-libs sub-package.
- Disable stripping of debug symbols for static libraries part of the -static-libs sub-package.
- JDK-8245832 increases the set of static libraries, so try and include them all with a wildcard.
- Update static-libs packaging to new layout

* Mon Sep 21 2020 Petra Alice Mikova <pmikova@redhat.com> - 1:15.0.0.36-2.rolling
- Add support for fastdebug builds on 64 bit architectures

* Tue Sep 15 2020 Severin Gehwolf <sgehwolf@redhat.com> - 1:15.0.0.36-1.rolling
- Remove EA designation
- Re-generate sources with PR3803 patch

* Mon Aug 31 2020 Petra Alice Mikova <pmikova@redhat.com> - 1:15.0.0.36-0.1.ea.rolling
- Update to jdk 15.0.0.36 tag
- Modify rh1648249-add_commented_out_nss_cfg_provider_to_java_security.patch
- Update vendor version string to 20.9
- jjs removed from packaging after JEP 372: Nashorn removal
- rmic removed from packaging after JDK-8225319

* Mon Jul 27 2020 Severin Gehwolf <sgehwolf@redhat.com> - 1:14.0.2.12-2.rolling
- Disable LTO so as to pass debuginfo check

* Wed Jul 22 2020 Petra Alice Mikova <pmikova@redhat.com> - 1:14.0.2.12-1.rolling
- update to jdk 14.0.2.12 CPU version
- remove upstreamed patch jdk8237879-make_4_3_build_fixes.patch
- remove upstreamed patch jdk8235833-posixplatform_cpp_should_not_include_sysctl_h.patch
- remove upstreamed patch jdk8243059-build_fails_when_with_vendor_contains_comma.patch

* Thu Jul 09 2020 Andrew Hughes <gnu.andrew@redhat.com> - 1:14.0.1.7-4.rolling
- Re-introduce java-openjdk-src & java-openjdk-demo for system_jdk builds.
- Fix accidental renaming of java-openjdk-devel to java-devel-openjdk.

* Thu May 14 2020 Petra Alice Mikova <pmikova@redhat.com> -  1:14.0.1.7-3.rolling
- introduce patch jdk8235833-posixplatform_cpp_should_not_include_sysctl_h to fix build issues in rawhide
- rename and reorganize patch sections

* Thu Apr 23 2020 Severin Gehwolf <sgehwolf@redhat.com> - 1:14.0.1.7-2.rolling
- Fix vendor version to 20.3 (from 19.9)

* Fri Apr 17 2020 Petra Alice Mikova <pmikova@redhat.com> - 1:14.0.1.7-1.rolling
- April security update
- uploaded new src tarball

* Wed Apr 08 2020 Jiri Vanek <jvanek@redhat.com> - 1:14.0.0.36-4.rolling
- set vendor property and vendor urls
- made urls to be preconfigured by os

* Tue Mar 24 2020 Petra Alice Mikova <pmikova@redhat.com> - 1:14.0.0.36-3.rolling
- Remove s390x workaround flags for GCC 10
- bump buildjdkver to 14
- uploaded new src tarball

* Mon Mar 23 2020 Petra Alice Mikova <pmikova@redhat.com> - 1:14.0.0.36-2.rolling
- removed a whitespace causing fail of postinstall script
- removed backslashes at the end of alternatives command

* Fri Mar 13 2020 Petra Alice Mikova <pmikova@redhat.com> - 1:14.0.0.36-1.rolling
- update to jdk 14+36 ga build
- remove JDK-8224851 patch, as OpenJDK 14 already contains it
- removed pack200 and unpack200 binaries, slaves, manpages and libunpack.so library
- added listings for jpackage binary, manpages and added slave records to alternatives

* Thu Mar 12 2020 Petra Alice Mikova <pmikova@redhat.com> - 1:13.0.2.8-4.rolling
- add patch for build issues with make 4.3

* Thu Feb 27 2020 Severin Gehwolf <sgehwolf@redhat.com> - 1:13.0.2.8-3.rolling
- add workaround for issues with build with GCC10 on s390x (see RHBZ#1799531)
- fix issues with build with GCC10: JDK-8224851, -fcommon switch

* Thu Feb 27 2020 Petra Alice Mikova pmikova@redhat.com> - 1:13.0.2.8-3.rolling
- Add JDK-8224851 patch to resolve aarch64 issues

* Tue Feb 04 2020 Petra Alice Mikova <pmikova@redhat.com> - 1:13.0.2.8-2.rolling
- fix Release, as it was broken by last rpmdev-bumpspec

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1:13.0.2.8-1.rolling.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Fri Jan 17 2020 Petra Alice Mikova <pmikova@redhat.com> - 1:13.0.2.8-1.rolling
- removed patch jdk8231405_guarantee_d_nonequals_null_failed_null_dominator_info.patch
- removed patch jdk8231583_fix_register_clash_in_sbsa_resolve_forwarding_pointer_borrowing.patch
- updated sources to the 13.0.2+8 tag

* Fri Oct 25 2019 Petra Alice Mikova <pmikova@redhat.com> - 1:13.0.1.9-2.rolling
- Fixed hardcoded major version in jdk13u to macro
- added jdk8231405_guarantee_d_nonequals_null_failed_null_dominator_info.patch
- added jdk8231583_fix_register_clash_in_sbsa_resolve_forwarding_pointer_borrowing.patch

* Mon Oct 21 2019 Petra Alice Mikova <pmikova@redhat.com> - 1:13.0.1.9-1.rolling
- Updated to October 2019 CPU sources

* Wed Oct 16 2019 Petra Alice Mikova <pmikova@redhat.com> - 1:13.0.0.33-3.rolling
- synced up generate tarball script with other OpenJDK packages
- dropped pr2126-synchronise_elliptic_curves_in_sun_security_ec_namedcurve_with_those_listed_by_nss.patch from the sources
- regenerated sources with the updated script

* Wed Oct 02 2019 Andrew Hughes <gnu.andrew@redhat.com> - 1:13.0.0.33-3.rolling
- Switch to in-tree SunEC code, dropping NSS runtime dependencies and patches to link against it.

* Wed Oct 02 2019 Andrew John Hughes <gnu.andrew@redhat.com> -  1:13.0.0.33-3.rolling
- Drop unnecessary build requirement on gtk3-devel, as OpenJDK searches for Gtk+ at runtime.
- Add missing build requirement for libXrender-devel, previously masked by Gtk3+ dependency
- Add missing build requirement for libXrandr-devel, previously masked by Gtk3+ dependency
- fontconfig build requirement should be fontconfig-devel, previously masked by Gtk3+ dependency

* Wed Oct 02 2019 Andrew Hughes <gnu.andrew@redhat.com> - 1:13.0.0.33-3.rolling
- Obsolete javadoc-slowdebug and javadoc-slowdebug-zip packages via javadoc and javadoc-zip respectively.

* Tue Oct 01 2019 Severin Gehwolf <sgehwolf@redhat.com> - 1:13.0.0.33-2.rolling
- Don't produce javadoc/javadoc-zip sub packages for the
  debug variant build.
- Don't perform a bootcycle build for the debug variant build.

* Mon Sep 30 2019 Severin Gehwolf <sgehwolf@redhat.com> - 1:13.0.0.33-2.rolling
- Fix vendor version as JDK 13 has been GA'ed September 2019: 19.3 => 19.9

* Wed Aug 14 2019 Petra Alice Mikova <pmikova@redhat.com> - 1:13.0.0.33-1.rolling
- updated to 13+33 sources
- added two manpages to file listings (jfr, jaotc)
- set is_ga to 1 to match build from jdk.java.net

* Fri Jul 26 2019 Severin Gehwolf <sgehwolf@redhat.com> - 1:13.0.0.28-0.2.ea.rolling
- Fix bootjdkver macro. It attempted to build with jdk 12, which is
  no longer available in rawhide (it's 13 instead).
- Fix Release as rpmdev-bumpspec doesn't do it correctly.

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1:13.0.0.28-0.1.ea.rolling.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Tue Jul 09 2019 Petra Alice Mikova <pmikova@redhat.com> - 1:13.0.0.28-0.1.ea.rolling
- updated to jdk 13
- adapted pr2126-synchronise_elliptic_curves_in_sun_security_ec_namedcurve_with_those_listed_by_nss.patch
- adapted rh1648242-accessible_toolkit_crash_do_not_break_jvm.patch
- fixed file listings
- included https://src.fedoraproject.org/rpms/java-11-openjdk/pull-request/49:
- Include 'ea' designator in Release when appropriate
- Handle milestone as variables so we can alter it easily and set the docs zip filename appropriately

* Tue May 21 2019 Petra Alice Mikova <pmikova@redhat.com> - 1:12.0.1.12-2.rolling
- fixed requires/provides for the non-system JDK case (backport of RHBZ#1702324)

* Thu Apr 18 2019 Petra Mikova <pmikova@redhat.com> - 1:12.0.1.12-1.rolling
- updated sources to current CPU release

* Thu Apr 04 2019 Petra Mikova <pmikova@redhat.com> - 1:12.0.0.33-4.rolling
- added slave for jfr binary in devel package

* Thu Mar 21 2019 Petra Mikova <pmikova@redhat.com> - 1:12.0.0.33-3.rolling
- Replaced pcsc-lite-devel (which is in optional channel) with pcsc-lite-libs.
- added rh1684077-openjdk_should_depend_on_pcsc-lite-libs_instead_of_pcsc-lite-devel.patch to make jdk work with pcsc
- removed LTS string from LTS designator, because epel builds get identified as rhel and JDK 12 is not LTS
- removed duplicated dependency on lksctp-tools

* Wed Mar 20 2019 Peter Robinson <pbrobinson@fedoraproject.org> 1:12.0.0.33-2.ea.1.rolling
- Drop chkconfig dep, 1.7 shipped in f24

* Thu Mar 07 2019 Petra Mikova <pmikova@redhat.com> - 1:12.0.0.33-1.ea.1.rolling
- bumped sources to jdk12+33

* Mon Feb 11 2019 Severin Gehwolf <sgehwolf@redhat.com> - 1:12.0.0.30-1.ea.1.rolling
- Only build 'bootcycle-images docs' target and 'images docs' targets, respectively.

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1:12.0.0.25-0.ea.1.rolling.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Dec 21 2018 Jiri Vanek <jvanek@redhat.com> - 1:12.0.0.25-0.ea.1.rolling
- bumped sources to jdk12. Crypto list synced.
- adapted patches to usptream (removed are upstreamed)
- removed fixed upstreamed patch6, jdk8211105-aarch64-disable_cos_sin_and_log_intrinsics.patch:
- renamed patch5, pr1983-rh1565658-..._sunec_provider_jdk11.patch to pr1983-rh1565658-..._sunec_provider_jdk12.patch
- adapted patch5, pr1983-rh1565658 to jdk12 (libraries.m4 and /Lib-jdk.crypto.ec.gmk)
- removed patch8, jdk8210416-rh1632174-compile_fdlibm_with_o2_ffp_contract_off_on_gcc_clang_arches.patch
- removed patch9, jdk8210425-rh1632174-sharedRuntimeTrig_sharedRuntimeTrans_compiled_without_optimization.patch
- removed patch10, jdk8210647-rh1632174. Is rummored to be in upstream
- removed patch11, jdk8210761-rh1632174-libjsig_is_being_compiled_without_optimization.patch
- removed patch12, jdk8210703-rh1632174-vmStructs_cpp_no_longer_compiled_with_o0
- removed patch584, jdk8209639-rh1640127-02-coalesce_attempted_spill_non_spillable.patch
- removed patch585, jdk8209639-rh1640127-02-coalesce_attempted_spill_non_spillable.patch
- set build jdk to jdk11; buildjdkver set to 11
- todo, revisit _privatelibs and slaves, discuse patch10, more?
- now building with --no-print-directory to workaround JDK8215213
- renamed original of docs zip to jdk-major+build
- check shenandaoh with -XX:+UnlockExperimentalVMOptions
- libjli moved from lib/libjli to lib
- added lib/jspawnhelper and bin/jfr and conf/sdp/sdp.conf.template
- added explanation to the --no-print-directory
- re-added lts_designator_zip macro
- added patch6 for rh1673833-remove_removal_of_wformat_during_test_compilation.patch

* Wed Dec 5 2018 Jiri Vanek <jvanek@redhat.com> - 1:11.0.1.13-10.rolling
- for non debug supackages, ghosted all masters and slaves (rhbz1649776)
- for tech-preview packages, if-outed versionless provides. Aligned versions to be %%{epoch}:%%{version}-%%{release} instead of chaotic
- Removed all slowdebug provides (rhbz1655938); for tech-preview packages also removed all internal provides

* Tue Dec 04 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:11.0.1.13-9
- Added %%global _find_debuginfo_opts -g
- Resolves: RHBZ#1520879 (Detailed NMT issue)

* Fri Nov 30 2018 Jiri Vanek <jvanek@redhat.com> - 1:11.0.1.13-8
- added rolling suffix to release (before dist) to prevent conflict with java-11-openjdk which now have same major version

* Mon Nov 12 2018 Jiri Vanek <jvanek@redhat.com> - 1:11.0.1.13-6
- fixed tck failures of arraycopy and process exec with shenandoah on
- added patch585 rh1648995-shenandoah_array_copy_broken_by_not_always_copy_forward_for_disjoint_arrays.patch

* Wed Nov 07 2018 Jiri Vanek <jvanek@redhat.com> - 1:11.0.1.13-5
- headless' suggests of cups, replaced by Requires of cups-libs

* Thu Nov 01 2018 Jiri Vanek <jvanek@redhat.com> - 1:11.0.1.13-3
- added Patch584 jdk8209639-rh1640127-02-coalesce_attempted_spill_non_spillable.patch

* Mon Oct 29 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:11.0.1.13-3
- Use upstream's version of Aarch64 intrinsics disable patch:
  - Removed:
    RHBZ-1628612-JDK-8210461-workaround-disable-aarch64-intrinsic.patch
    RHBZ-1630996-JDK-8210858-workaround-disable-aarch64-intrinsic-log.patch
  - Superceded by:
    jdk8211105-aarch64-disable_cos_sin_and_log_intrinsics.patch

* Thu Oct 18 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:11.0.1.13-2
- Use LTS designator in version output for RHEL.

* Thu Oct 18 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:11.0.1.13-1
- Update to October 2018 CPU release, 11.0.1+13.

* Wed Oct 17 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:11.0.0.28-2
- Use --with-vendor-version-string=18.9 so as to show original
  GA date for the JDK.

* Fri Sep 28 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:11.0.0.28-1
- Identify as GA version and no longer as early access (EA).
- JDK 11 has been released for GA on 2018-09-25.

* Fri Sep 28 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:11.0.ea.28-9
- Rework changes from 1:11.0.ea.22-6. RHBZ#1632174 supercedes
  RHBZ-1624122.
- Add patch, jdk8210416-rh1632174-compile_fdlibm_with_o2_ffp_contract_off_on_gcc_clang_arches.patch, so as to
  optimize compilation of fdlibm library.
- Add patch, jdk8210425-rh1632174-sharedRuntimeTrig_sharedRuntimeTrans_compiled_without_optimization.patch, so
  as to optimize compilation of sharedRuntime{Trig,Trans}.cpp
- Add patch, jdk8210647-rh1632174-libsaproc_is_being_compiled_without_optimization.patch, so as to
  optimize compilation of libsaproc (extra c flags won't override
  optimization).
- Add patch, jdk8210761-rh1632174-libjsig_is_being_compiled_without_optimization.patch, so as to
  optimize compilation of libjsig.
- Add patch, jdk8210703-rh1632174-vmStructs_cpp_no_longer_compiled_with_o0, so as to
  optimize compilation of vmStructs.cpp (part of libjvm.so).
- Reinstate filtering of opt flags coming from redhat-rpm-config.

* Thu Sep 27 2018 Jiri Vanek <jvanek@redhat.com> - 1:11.0.ea.28-8
- removed version less provides
- javadocdir moved to arched dir as it is no longer noarch

* Thu Sep 20 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:11.0.ea.28-6
- Add patch, RHBZ-1630996-JDK-8210858-workaround-disable-aarch64-intrinsic-log.patch,
  so as to disable log math intrinsic on aarch64. Work-around for
  JDK-8210858

* Thu Sep 13 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:11.0.ea.28-5
- Add patch, RHBZ-1628612-JDK-8210461-workaround-disable-aarch64-intrinsic.patch,
  so as to disable dsin/dcos math intrinsics on aarch64. Work-around for
  JDK-8210461.

* Wed Sep 12 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:11.0.ea.22-6
- Add patch, JDK-8210416-RHBZ-1624122-fdlibm-opt-fix.patch, so as to
  optimize compilation of fdlibm library.
- Add patch, JDK-8210425-RHBZ-1624122-sharedRuntimeTrig-opt-fix.patch, so
  as to optimize compilation of sharedRuntime{Trig,Trans}.cpp
- Add patch, JDK-8210647-RHBZ-1624122-libsaproc-opt-fix.patch, so as to
  optimize compilation of libsaproc (extra c flags won't override
  optimization).
- Add patch, JDK-8210703-RHBZ-1624122-vmStructs-opt-fix.patch, so as to
  optimize compilation of vmStructs.cpp (part of libjvm.so).
- No longer filter -O flags from C flags coming from
  redhat-rpm-config.

* Mon Sep 10 2018 Jiri Vanek <jvanek@redhat.com> - 1:11.0.ea.28-4
- link to jhsdb followed its file to ifarch jit_arches ifnarch s390x

* Fri Sep 7 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:11.0.ea.28-3
- Enable ZGC on x86_64.

* Tue Sep 4 2018 Jiri Vanek <jvanek@redhat.com> - 1:11.0.ea.28-2
- jfr/*jfc files listed for all arches
- lib/classlist do not exists s390, ifarch-ed via jit_arches out

* Fri Aug 31 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:11.0.ea.28-1
- Update to latest upstream build jdk11+28, the first release
  candidate.

* Wed Aug 29 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:11.0.ea.22-8
- Adjust system NSS patch, pr1983-rh1565658-support_using_the_system_installation_of_nss_with_the_sunec_provider_jdk11.patch, so
  as to filter -Wl,--as-needed from linker flags. Fixes FTBFS issue.

* Thu Aug 23 2018 Jiri Vanek <jvanek@redhat.com> - 1:11.0.ea.22-6
- dissabled accessibility, fixed provides for main package's debug variant

* Mon Jul 30 2018 Jiri Vanek <jvanek@redhat.com> - 1:11.0.ea.22-5
- now buildrequires javapackages-filesystem as the  issue with macros should be fixed

* Wed Jul 18 2018 Jiri Vanek <jvanek@redhat.com> - 1:11.0.ea.22-2
- changed to build by itself instead of by jdk10

* Tue Jul 17 2018 Jiri Vanek <jvanek@redhat.com> - 1:11.0.ea.22-1
- added Recommends gtk3 for main package
- changed BuildRequires from gtk2-devel to gtk3-devel (it can be more likely dropped)
- added Suggests lksctp-tools, pcsc-lite-devel, cups for headless package
- see RHBZ1598152
- added trick to catch hs_err files (sgehwolf)
- updated to shenandaoh-jdk-11+22

* Sat Jul 07 2018 Jiri Vanek <jvanek@redhat.com> - 1:11.0.ea.20-1
- removed patch6 JDK-8205616-systemLcmsAndJpgFixFor-rev_f0aeede1b855.patch
- improved a bit generate_source_tarball.sh to serve also for systemtap
- thus deleted generate_tapsets.sh
- simplified and cleared update_package.sh
- moved to single source jdk - from shenandoah/jdk11
- bumped to latest jdk11+20
- adapted PR2126 to jdk11+20
- adapted handling of systemtap sources to new style
- (no (misleading) version inside (full version is in name), thus different sed on tapsets and different directory)
- shortened summaries and descriptions to around 80 chars
- Hunspell spell checked
- license fixed to correct jdk11 (sgehwolf)
- more correct handling of internal libraries (sgehwolf)
- added lib/security/public_suffix_list.dat as +20 have added it (JDK-8201815)
- added test for shenandaoh GC presence where expected
- Removed workaround for broken aarch64 slowdebug build
- Removed all defattrs
- Removed no longer necessary cleanup of diz and  debuginfo files

* Fri Jun 22 2018 Jiri Vanek <jvanek@redhat.com> - 1:11.0.ea.19-1
- updated sources to jdk-11+19
- added patch6 systemLcmsAndJpgFixFor-f0aeede1b855.patch to fix regression of system libraries after f0aeede1b855 commit
- adapted pr1983-rh1565658-support_using_the_system_installation_of_nss_with_the_sunec_provider_jdk11.patch to accommodate changes after f0aeede1b855 commit

* Thu Jun 14 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:11.0.ea.16-5
- Revert rename: java-11-openjdk => java-openjdk.

* Wed Jun 13 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:11.0.ea.16-4
- Add aarch64 to aot_arches.

* Wed Jun 13 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:11.0.ea.16-3
- Rename to package java-11-openjdk.

* Wed Jun 13 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:11.0.ea.16-2
- Disable Aarch64 slowdebug build (see JDK-8204331).
- s390x doesn't have the SA even though it's a JIT arch.

* Wed Jun 13 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:11.0.ea.16-1
- Initial version of JDK 11 ea based on tag jdk-11+16.
- Removed patches no longer needed or upstream:
  sorted-diff.patch (see JDK-8198844)
  JDK-8201788-bootcycle-images-jobs.patch
  JDK-8201509-s390-atomic_store.patch
  JDK-8202262-libjsig.so-extra-link-flags.patch (never was an issue on 11)
  JDK-8193802-npe-jar-getVersionMap.patch
- Updated and renamed patches:
  java-openjdk-s390-size_t.patch => JDK-8203030-s390-size_t.patch
- Updated patches for JDK 11:
  pr1983-rh1565658-support_using_the_system_installation_of_nss_with_the_sunec_provider_jdk11.patch

* Tue Jun 12 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:10.0.1.10-9
- Use proper private_libs expression for filtering requires/provides.

* Fri Jun 08 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:10.0.1.10-8
- Bump release and rebuild for fixed gdb. See RHBZ#1589118.

* Mon Jun 04 2018 Jiri Vanek <jvanek@redhat.com> - 1:10.0.1.10-7
- quoted sed expressions, changed possibly confusing # by @
- added vendor(origin) into icons
- removed last trace of relative symlinks
- added BuildRequires of javapackages-tools to fix build failure after Requires change to javapackages-filesystem

* Thu May 17 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:10.0.1.10-5
- Move to javapackages-filesystem for directory ownership.
  Resolves RHBZ#1500288

* Mon Apr 30 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:10.0.1.10-4
- Add JDK-8193802-npe-jar-getVersionMap.patch so as to fix
  RHBZ#1557375.

* Mon Apr 23 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:10.0.1.10-3
- Inject build flags properly. See RHBZ#1571359
- Added patch JDK-8202262-libjsig.so-extra-link-flags.patch
  since libjsig.so doesn't get linker flags injected properly.

* Fri Apr 20 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:10.0.1.10-2
- Removed unneeded patches:
  PStack-808293.patch
  multiple-pkcs11-library-init.patch
  ppc_stack_overflow_fix.patch
- Added patches for s390 Zero builds:
  JDK-8201495-s390-java-opts.patch
  JDK-8201509-s390-atomic_store.patch
- Renamed patches for clarity:
  aarch64BuildFailure.patch => JDK-8200556-aarch64-slowdebug-crash.patch
  systemCryptoPolicyPR3183.patch => pr3183-rh1340845-support_fedora_rhel_system_crypto_policy.patch
  bootcycle_jobs.patch => JDK-8201788-bootcycle-images-jobs.patch
  system-nss-ec-rh1565658.patch => pr1983-rh1565658-support_using_the_system_installation_of_nss_with_the_sunec_provider_jdk11.patch

* Fri Apr 20 2018 Jiri Vanek <jvanek@redhat.com> - 1:10.0.1.10-1
- updated to security update 1
- jexec unlinked from path
- used java-openjdk as boot jdk
- aligned provides/requires
- renamed zip javadoc

* Tue Apr 10 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:10.0.0.46-12
- Enable basic EC ciphers test in %%check.

* Tue Apr 10 2018 Severin Gehwolf <sgehwolf@redhat.com> - 1:10.0.0.46-11
- Port Martin Balao's JDK 9 patch for system NSS support to JDK 10.
- Resolves RHBZ#1565658

* Mon Apr 09 2018 Jiri Vanek <jvanek@redhat.com> - 1:10.0.0.46-10
- jexec linked to path

* Fri Apr 06 2018 Jiri Vanek <jvanek@redhat.com> - 1:10.0.0.46-9
- subpackage(s) replaced by sub-package(s) and other cosmetic changes

* Tue Apr 03 2018 Jiri Vanek <jvanek@redhat.com> - 1:10.0.0.46-8
- removed accessibility sub-packages
- kept applied patch and properties files
- debug sub-packages renamed to slowdebug

* Fri Feb 23 2018 Jiri Vanek <jvanek@redhat.com> - 1:10.0.0.46-1
- initial load
