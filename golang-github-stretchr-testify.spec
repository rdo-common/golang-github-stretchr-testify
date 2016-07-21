%if 0%{?fedora} || 0%{?rhel} == 6
%global with_devel 1
%global with_bundled 0
%global with_debug 0
# as long as there is circular dependency between 
# golang-github-stretchr-testify and golang-github-stretchr-objx
# there can not by test
%global with_check 0
%global with_unit_test 1
%else
%global with_devel 0
%global with_bundled 0
%global with_debug 0
%global with_check 0
%global with_unit_test 0
%endif

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%define copying() \
%if 0%{?fedora} >= 21 || 0%{?rhel} >= 7 \
%license %{*} \
%else \
%doc %{*} \
%endif

%global provider        github
%global provider_tld    com
%global project         stretchr
%global repo            testify
# https://github.com/stretchr/testify
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     %{provider_prefix}
%global commit          089c7181b8c728499929ff09b62d3fdd8df8adff
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

Name:           golang-%{provider}-%{project}-%{repo}
Version:        1.0
Release:        0.6.git%{shortcommit}%{?dist}
Summary:        Tools for testifying that your code will behave as you intend
License:        MIT
URL:            https://%{provider_prefix}
Source0:        https://%{provider_prefix}/archive/%{commit}/%{repo}-%{shortcommit}.tar.gz

# If go_arches not defined fall through to implicit golang archs
%if 0%{?go_arches:1}
ExclusiveArch:  %{go_arches}
%else
ExclusiveArch:   %{ix86} x86_64 %{arm}
%endif
# If gccgo_arches does not fit or is not defined fall through to golang
%ifarch 0%{?gccgo_arches}
BuildRequires:   gcc-go >= %{gccgo_min_vers}
%else
BuildRequires:   golang
%endif

%description
Thou Shalt Write Tests

Go code (golang) set of packages that provide many tools for testifying that
your code will behave as you intend.

%if 0%{?with_devel}
%package devel
Summary:       %{summary}
BuildArch:     noarch

%if 0%{?with_check}
# cyclic deps
BuildRequires: golang(github.com/stretchr/objx)
%endif

Requires:      golang(github.com/stretchr/objx)

Provides:      golang(%{import_path}) = %{version}-%{release}
Provides:      golang(%{import_path}/assert) = %{version}-%{release}
Provides:      golang(%{import_path}/http) = %{version}-%{release}
Provides:      golang(%{import_path}/mock) = %{version}-%{release}
Provides:      golang(%{import_path}/require) = %{version}-%{release}
Provides:      golang(%{import_path}/suite) = %{version}-%{release}

%description devel
%{summary}

This package contains library source intended for
building other packages which use import path with
%{import_path} prefix.
%endif

%if 0%{?with_unit_test}
%package unit-test
Summary:         Unit tests for %{name} package
# If go_arches not defined fall through to implicit golang archs
%if 0%{?go_arches:1}
ExclusiveArch:  %{go_arches}
%else
ExclusiveArch:   %{ix86} x86_64 %{arm}
%endif
# If gccgo_arches does not fit or is not defined fall through to golang
%ifarch 0%{?gccgo_arches}
BuildRequires:   gcc-go >= %{gccgo_min_vers}
%else
BuildRequires:   golang
%endif

%if 0%{?with_check}
#Here comes all BuildRequires: PACKAGE the unit tests
#in %%check section need for running
%endif

# test subpackage tests code from devel subpackage
Requires:        %{name}-devel = %{version}-%{release}

%description unit-test
%{summary}

This package contains unit tests for project
providing packages with %{import_path} prefix.
%endif

%prep
%setup -q -n %{repo}-%{commit}

mv LICENCE.txt LICENSE.txt

%build

%install
# source codes for building projects
%if 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
# find all *.go but no *_test.go files and generate devel.file-list
for file in $(find . -iname "*.go" \! -iname "*_test.go") ; do
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list
done
%endif

# testing files for this project
%if 0%{?with_unit_test}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
# find all *_test.go files and generate unit-test.file-list
for file in $(find . -iname "*_test.go"); do
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> unit-test.file-list
done
%endif

%check
%if 0%{?with_check} && 0%{?with_unit_test} && 0%{?with_devel}
%ifarch 0%{?gccgo_arches}
function gotest { %{gcc_go_test} "$@"; }
%else
%if 0%{?golang_test:1}
function gotest { %{golang_test} "$@"; }
%else
function gotest { go test "$@"; }
%endif
%endif

export GOPATH=%{buildroot}/%{gopath}:%{gopath}
gotest %{import_path}
gotest %{import_path}/assert
gotest %{import_path}/mock
gotest %{import_path}/require
gotest %{import_path}/suite
%endif

%if 0%{?with_devel}
%files devel -f devel.file-list
%copying LICENSE.txt
%doc README.md
%dir %{gopath}/src/%{provider}.%{provider_tld}/%{project}
%dir %{gopath}/src/%{import_path}
%endif

%if 0%{?with_unit_test}
%files unit-test -f unit-test.file-list
%copying LICENSE.txt
%doc README.md
%endif

%changelog
* Thu Jul 21 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0-0.6.git089c718
- https://fedoraproject.org/wiki/Changes/golang1.7

* Mon Feb 22 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0-0.5.git089c718
- https://fedoraproject.org/wiki/Changes/golang1.6

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.0-0.4.git089c718
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Aug 11 2015 jchaloup <jchaloup@redhat.com> - 1.0-0.3.git089c718
- Add missing license in unit-test, BR of devel can be uncommented out
  relates: #1246684

* Mon Aug 10 2015 Fridolin Pokorny <fpokorny@redhat.com> - 1.0-0.2.git089c718
- Update spec file to spec-2.0
  relates: #1246684

* Fri Jul 24 2015 jchaloup <jchaloup@redhat.com> - 1.0-0.1.git089c718
- Bump to upstream 089c7181b8c728499929ff09b62d3fdd8df8adff
  resolves: #1246684

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-0.8.gite4ec815
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Mar 06 2015 jchaloup <jchaloup@redhat.com> - 0-0.7.gite4ec815
- update URL to point to github repository
  related: #1141872

* Thu Mar 05 2015 jchaloup <jchaloup@redhat.com> - 0-0.6.gite4ec815
- Bump to upstream e4ec8152c15fc46bd5056ce65997a07c7d415325
  related: #1141872

* Thu Oct 23 2014 jchaloup <jchaloup@redhat.com> - 0-0.5.gitd6577e0
- Bump to upstream d6577e08ec30538639ac0ea38b562b6f250e9055
- Spec file polishing to follow go draft
  related: #1141872

* Mon Sep 15 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0-0.3.gitda775f0
- preserve timestamps of copied files

* Wed Aug 06 2014 Adam Miller <maxamillion@fedoraproject.org> - 0-0.2.gitda775f0
- Fix up devel package listing

* Wed Aug 06 2014 Adam Miller <maxamillion@fedoraproject.org> - 0-0.1.gitda775f0
- First package for Fedora.
