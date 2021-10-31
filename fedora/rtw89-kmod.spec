# (un)define the next line to either build for the newest or all current kernels
#define buildforkernels newest
#define buildforkernels current
%define buildforkernels akmod

# We are not building any debug packages.
%define debug_package %{nil}

# Tag we are building
%global git_tag 20211027

# name should have a -kmod suffix
Name: rtw89-kmod           

Version: 	6
Release: 	1.git%{git_tag}%{?dist}.1
Summary: 	RTL8852AE driver kernel module

Group:          System Environment/Kernel

License:        GPLv2
URL:            https://github.com/lwfinger/rtw89
Source0:        https://github.com/lwfinger/rtw89/archive/refs/tags/%{git_tag}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  %{_bindir}/kmodtool


# Verify that the package build for all architectures.
# In most time you should remove the Exclusive/ExcludeArch directives
# and fix the code (if needed).
# ExclusiveArch:  i686 x86_64 ppc64 ppc64le armv7hl aarch64
ExclusiveArch:  x86_64
# ExcludeArch: i686 x86_64 ppc64 ppc64le armv7hl aarch64

# get the proper build-sysbuild package from the repo, which
# tracks in all the kernel-devel packages
BuildRequires:  %{_bindir}/kmodtool

%{!?kernels:BuildRequires: gcc, elfutils-libelf-devel, buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }

# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
Kernel driver module for the RTL8852AE wifi adapter.

%package common
Summary: RTL8852AE driver firmware files
Group:   System Environment/Kernel

%description common
Firmware files for the RTL8852AE wifi adapter.


%prep
# error out if there was something wrong with kmodtool
%{?kmodtool_check}

# print kmodtool output for debugging purposes:
kmodtool  --target %{_target_cpu}  --repo %{repo} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%setup -q -c -T -a 0

%define build_common %( if [ "%{?kernel_versions}" == "" ] ; then echo 0 ; else echo 1 ; fi )

# apply patches and do other stuff here
# pushd foo-%{version}
# #patch0 -p1 -b .suffix
# popd

for kernel_version in %{?kernel_versions} ; do
    cp -a rtw89-%{git_tag} _kmod_build_${kernel_version%%___*}
done


%build -x
for kernel_version in %{?kernel_versions}; do
    make %{?_smp_mflags} -C "${kernel_version##*___}" M="${PWD}/_kmod_build_${kernel_version%%___*}" modules
done


%install
rm -rf ${RPM_BUILD_ROOT}

for kernel_version in %{?kernel_versions}; do
    #make install DESTDIR=${RPM_BUILD_ROOT} KMODPATH=%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}
    install -D -m 755 _kmod_build_${kernel_version%%___*}/rtw89core.ko  ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/rtw89core.ko
    install -D -m 755 _kmod_build_${kernel_version%%___*}/rtw89pci.ko  ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/rtw89pci.ko
    mkdir -pv ${RPM_BUILD_ROOT}/lib/firmware/rtw89
    for CUR_FW in `ls -1 _kmod_build_${kernel_version%%___*}/*.bin`; do
        install -D -m 644 ${CUR_FW} ${RPM_BUILD_ROOT}/lib/firmware/rtw89/`basename ${CUR_FW}`
    done
done

%{?akmod_install}

%if %build_common 
%files common
/lib/firmware/rtw89
/lib/firmware/rtw89/*
%endif

%clean
rm -rf $RPM_BUILD_ROOT


%changelog
* Sat Oct 30 2021 Daniel Riek <riek@llunved.net> - 5-1.2021103001
- Initial RPM release.
