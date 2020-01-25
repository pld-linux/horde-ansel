# TODO
# - lighttpd: docs/lighttpd-ansel.conf
%define		hordeapp	ansel
Summary:	Ansel Photo Management and Web Gallery application
Name:		horde-%{hordeapp}
Version:	1.1.2
Release:	0.1
License:	GPL v2
Group:		Applications/WWW
Source0:	ftp://ftp.horde.org/pub/ansel/%{hordeapp}-h3-%{version}.tar.gz
# Source0-md5:	9ef6fce234593b1c40dc1ccdc39b5a37
Source1:	apache.conf
URL:		http://www.horde.org/ansel/
BuildRequires:	rpm-php-pearprov >= 4.0.2-98
BuildRequires:	rpmbuild(macros) >= 1.264
Requires:	horde >= 3.0
Requires:	webapps
Requires:	webserver(access)
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		hordedir	/usr/share/horde
%define		_appdir		%{hordedir}/%{hordeapp}
%define		_webapps	/etc/webapps
%define		_webapp		horde-%{hordeapp}
%define		_sysconfdir	%{_webapps}/%{_webapp}

%define		_noautoreq	pear(Horde.*)

%description
Ansel is a full featured photo management application. With it, you
can organize your photos in any number of galleries and subgalleries,
share galleries among other Horde users or even make them public.
Ansel supports a wide range of features.

%prep
%setup -q -n %{hordeapp}-h3-%{version}

rm {,*/}.htaccess
for i in config/*.dist; do
	mv $i config/$(basename $i .dist)
done
# considered harmful (horde/docs/SECURITY)
rm test.php

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_appdir}/docs}

cp -a *.php $RPM_BUILD_ROOT%{_appdir}
cp -a config/* $RPM_BUILD_ROOT%{_sysconfdir}
echo '<?php ?>' > $RPM_BUILD_ROOT%{_sysconfdir}/conf.php
touch $RPM_BUILD_ROOT%{_sysconfdir}/conf.php.bak
cp -a lib locale templates themes $RPM_BUILD_ROOT%{_appdir}
cp -a faces gallery img $RPM_BUILD_ROOT%{_appdir}
cp -a docs/CREDITS $RPM_BUILD_ROOT%{_appdir}/docs

ln -s %{_sysconfdir} $RPM_BUILD_ROOT%{_appdir}/config
cp -a %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
cp -a %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ ! -f %{_sysconfdir}/conf.php.bak ]; then
	install /dev/null -o root -g http -m 0660 %{_sysconfdir}/conf.php.bak
fi

# CHECK FIRST DOES IT HAVE SQL AND FILE THERE.
if [ "$1" = 1 ]; then
	%banner %{name} -e <<-EOF
	IMPORTANT:
	If you are installing Ansel for the first time, You may need to
	create the Ansel database tables. To do so run:
	zcat %{_docdir}/%{name}-%{version}/scripts/sql/%{hordeapp}.sql.gz | mysql horde
	EOF
fi

%triggerin -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%files
%defattr(644,root,root,755)
%doc README docs/* scripts
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(660,root,http) %config(noreplace) %{_sysconfdir}/conf.php
%attr(660,root,http) %config(noreplace) %ghost %{_sysconfdir}/conf.php.bak
%attr(640,root,http) %config(noreplace) %{_sysconfdir}/[!c]*.php
%attr(640,root,http) %{_sysconfdir}/conf.xml

%dir %{_appdir}
%{_appdir}/*.php
%{_appdir}/config
%{_appdir}/docs
%{_appdir}/faces
%{_appdir}/gallery
%{_appdir}/img
%{_appdir}/lib
%{_appdir}/locale
%{_appdir}/templates
%{_appdir}/themes
