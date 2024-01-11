OpenJDK 17 is the latest Long-Term Support (LTS) release of the Java platform.

For a list of major changes from OpenJDK 11 (java-11-openjdk), see the upstream
release page for OpenJDK 17 and the preceding interim releases:

* 12: https://openjdk.java.net/projects/jdk/12/
* 13: https://openjdk.java.net/projects/jdk/13/
* 14: https://openjdk.java.net/projects/jdk/14/
* 15: https://openjdk.java.net/projects/jdk/15/
* 16: https://openjdk.java.net/projects/jdk/16/
* 17: https://openjdk.java.net/projects/jdk/17/

# Rebuilding the OpenJDK package

The OpenJDK packages are now created from a single build which is then
packaged for different major versions of Red Hat Enterprise Linux
(RHEL). This allows the OpenJDK team to focus their efforts on the
development and testing of this single build, rather than having
multiple builds which only differ by the platform they were built on.

This does make rebuilding the package slightly more complicated than a
normal package. Modifications should be made to the
`java-17-openjdk-portable.specfile` file, which can be found with this
README file in the source RPM or installed in the documentation tree
by the `java-17-openjdk-headless` RPM.

Once the modified `java-17-openjdk-portable` RPMs are built, they
should be installed and will produce a number of tarballs in the
`/usr/lib/jvm` directory. The `java-17-openjdk` RPMs can then be
built, which will use these tarballs to create the usual RPMs found in
RHEL. The `java-17-openjdk-portable` RPMs can be uninstalled once the
desired final RPMs are produced.

Note that the `java-17-openjdk.spec` file has a hard requirement on
the exact version of java-17-openjdk-portable to use, so this will
need to be modified if the version or rpmrelease values are changed in
`java-17-openjdk-portable.specfile`.

To reduce the number of RPMs involved, the `fastdebug` and `slowdebug`
builds may be disabled using `--without fastdebug` and `--without
slowdebug`.
