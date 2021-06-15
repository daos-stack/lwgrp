%global with_mpich 1
%if (0%{?rhel} >= 8)
%global with_openmpi 1
%global with_openmpi3 0
%else
%global with_openmpi 0
%global with_openmpi3 1
%endif

%if (0%{?suse_version} >= 1500)
%global module_load() if [ "%{1}" == "openmpi3" ]; then MODULEPATH=/usr/share/modules module load gnu-openmpi; else MODULEPATH=/usr/share/modules module load gnu-%{1}; fi
%else
%global module_load() module load mpi/%{1}-%{_arch}
%endif

%if %{with_mpich}
%global mpi_list mpich
%endif
%if %{with_openmpi}
%global mpi_list %{?mpi_list} openmpi
%endif
%if %{with_openmpi3}
%if 0%{?fedora}
# this would be nice to use but causes issues with linting
# since that is done on Fedora
#{error: openmpi3 doesn't exist on Fedora}
%endif
%global mpi_list %{?mpi_list} openmpi3
%endif

%if (0%{?suse_version} >= 1500)
%global mpi_libdir %{_libdir}/mpi/gcc
%global mpi_lib_ext lib64
%global mpi_includedir %{_libdir}/mpi/gcc
%global mpi_include_ext /include
%else
%global mpi_libdir %{_libdir}
%global mpi_lib_ext lib
%global mpi_includedir  %{_includedir}
%global mpi_include_ext -%{_arch}
%endif

Name:		lwgrp
Version:	1.0.3
Release:	2%{?dist}
Summary:	Light-weight Group Library for MPI process groups 

License:	BSD
URL:		https://github.com/LLNL/lwgrp
Source0:	https://github.com/LLNL/lwgrp/releases/download/v%version/lwgrp-%version.tar.gz
Patch1:		lwgrp-sover.patch
BuildRequires: automake
%if (0%{?suse_version} >= 1500)
BuildRequires: lua-lmod
%else
BuildRequires: Lmod
%endif

%description
The light-weight group library defines data structures and collective
operations to group MPI processes as an ordered set.  Such groups are
useful as substitutes for MPI communicators when the overhead of
communicator creation is too costly.  For example, certain sorting
algorithms recursively divide processes into subgroups as the sort
algorithm progresses.  These groups may be different with each
invocation, so that it is inefficient to create and destroy
communicators during the sort routine.

%if %{with_openmpi}
%package openmpi
Summary: Light-weight Group Library for MPI process groups
BuildRequires: openmpi-devel

%description openmpi
The light-weight group library defines data structures and collective
operations to group MPI processes as an ordered set.

%package openmpi-devel
Summary: Light-weight Group Library for MPI process groups -- development files
Requires: %{name}-openmpi%{_isa} = %version-%release

%description openmpi-devel
Development files for %{name}-openmpi.
%endif

%if %{with_openmpi3}
%package openmpi3
Summary: Light-weight Group Library for MPI process groups
BuildRequires: openmpi3-devel

%description openmpi3
The light-weight group library defines data structures and collective
operations to group MPI processes as an ordered set.

%if (0%{?suse_version} >= 1500)
%package -n liblwgrp0-openmpi3
Summary: Light-weight Group Library for MPI process groups -- Shared libraries

%description -n liblwgrp0-openmpi3
Shared libraries for %{name}-openmpi3.
%endif

%package openmpi3-devel
Summary: Light-weight Group Library for MPI process groups -- development files
%if (0%{?suse_version} >= 1500)
Requires: liblwgrp0-openmpi3%{_isa} = %version-%release
%else
Requires: %{name}-openmpi3%{_isa} = %version-%release
%endif

%description openmpi3-devel
Development files for %{name}-openmpi3.
%endif

%if %{with_mpich}
%package mpich
Summary: Light-weight Group Library for MPI process groups
BuildRequires: mpich-devel

%description mpich
The light-weight group library defines data structures and collective
operations to group MPI processes as an ordered set.

%if (0%{?suse_version} >= 1500)
%package -n liblwgrp0-mpich
Summary: Light-weight Group Library for MPI process groups -- Shared libraries

%description -n liblwgrp0-mpich
Shared libraries for %{name}-mpich.
%endif

%package mpich-devel
Summary: Light-weight Group Library for MPI process groups -- development files
%if (0%{?suse_version} >= 1500)
Requires: liblwgrp0-mpich%{_isa} = %version-%release
%else
Requires: %{name}-mpich%{_isa} = %version-%release
%endif

%description mpich-devel
Development files for %{name}-mpich.
%endif

%prep
%setup -q
%patch1 -p1
autoreconf

%build
%global _configure ../configure
export CC=mpicc
for mpi in %{?mpi_list}; do
  mkdir $mpi
  pushd $mpi
  %module_load $mpi
  %configure --disable-static --includedir=%{mpi_includedir}/$mpi%{mpi_include_ext} --libdir=%{mpi_libdir}/$mpi/%{mpi_lib_ext}
  %make_build
  module purge
  popd
done

%install
for mpi in %{?mpi_list}; do
  %module_load $mpi
  %make_install -C $mpi
  rm %{buildroot}/%{mpi_libdir}/$mpi/%{mpi_lib_ext}/*.la
  rm -r %{buildroot}%{_datadir}/lwgrp
  module purge
done

%if %{with_openmpi}
%files openmpi
%license LICENSE.TXT
%doc README
%{mpi_libdir}/openmpi/%{mpi_lib_ext}/liblwgrp.so.*

%files openmpi-devel
%{mpi_includedir}/openmpi%{mpi_include_ext}/lwgrp.h
%{mpi_libdir}/openmpi/%{mpi_lib_ext}/liblwgrp.so
%{mpi_libdir}/openmpi/%{mpi_lib_ext}/pkgconfig/liblwgrp.pc
%endif

%if %{with_openmpi3}
%files openmpi3
%license LICENSE.TXT
%doc README
%if (0%{?suse_version} >= 1500)
%files -n liblwgrp0-openmpi3
%endif
%{mpi_libdir}/openmpi3/%{mpi_lib_ext}/liblwgrp.so.*

%files openmpi3-devel
%{mpi_includedir}/openmpi3%{mpi_include_ext}/lwgrp.h
%{mpi_libdir}/openmpi3/%{mpi_lib_ext}/liblwgrp.so
%{mpi_libdir}/openmpi3/%{mpi_lib_ext}/pkgconfig/liblwgrp.pc
%endif

%if %{with_mpich}
%files mpich
%license LICENSE.TXT
%doc README
%if (0%{?suse_version} >= 1500)
%files -n liblwgrp0-mpich
%endif
%{mpi_libdir}/mpich/%{mpi_lib_ext}/liblwgrp.so.*

%files mpich-devel
%{mpi_includedir}/mpich%{mpi_include_ext}/lwgrp.h
%{mpi_libdir}/mpich/%{mpi_lib_ext}/liblwgrp.so
%{mpi_libdir}/mpich/%{mpi_lib_ext}/pkgconfig/liblwgrp.pc
%endif

%changelog
* Mon May 17 2021 Brian J. Murrell <brian.murrell@intel.com> - 1.0.3-2
- Package for openmpi on EL8

* Thu Feb 04 2021 Dalton A. Bohning <daltonx.bohning@intel.com> - 1.0.3-1
- Update to version 1.0.3

* Mon Sep 28 2020 Brian J. Murrell <brian.murrell@intel.com> - 1.0.2-3.2
- Package for multiple MPI stacks and multiple distros

* Tue Sep 22 2020 John E. Malmberg <john.e.malmberg@intel.com> - 1.0.2-3.1
- Change to use openmpi3 for CentOS.

* Wed Sep 20 2017 Dave Love <loveshack@fedoraproject.org> - 1.0.2-3
- Add Requires

* Wed Sep 20 2017 Dave Love <loveshack@fedoraproject.org> - 1.0.2-2
- Add -devel

* Fri Sep 15 2017  <loveshack@fedoraproject.org> - 1.0.2-1
- Initial packaging

