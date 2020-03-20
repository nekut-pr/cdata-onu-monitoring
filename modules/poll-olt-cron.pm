#!/usr/bin/perl
use strict;
use utf8;
use warnings;
use strict;
use Socket;
use DBI;

binmode(STDOUT, ':utf8');

my %OID = (
    mac    => '1.3.6.1.4.1.17409.2.3.4.1.1.7',
    signal => '1.3.6.1.4.1.17409.2.3.4.2.1.4'
);

my $source   = "DBI:mysql:cdata:localhost";
my $username = "cdata";
my $password = "cdata";
my $dbh      = DBI->connect(
    $source,
    $username,
    $password, {
        mysql_enable_utf8 => 1,
        PrintError        => 1,
    }
);

$dbh->do("set names utf8");

my $ips = $dbh->selectcol_arrayref("select ip from olt");

for my $ip_address (@$ips) {

    my $snmp_mac    = `snmpwalk -v2c -c public $ip_address $OID{mac}`;
    my $snmp_signal = `snmpwalk -v2c -c public $ip_address $OID{signal}`;

    my @mac    = split(/\n/, $snmp_mac);
    my @signal = split(/\n/, $snmp_signal);

    for (@mac) {
        if (/\.(\d+)\s+=\s+Hex-STRING:\s+([0-9A-F\s]+)/) {
            my ($port, $mac) = ($1, $2);
            $mac =~ s/\s+$//;
            $mac =~ tr/ /:/;
            comparison(
                ip_olt   => $ip_address,
                mac_port => $port,
                mac      => $mac
            );
            add(
                mac_port => $port,
                ip_olt   => $ip_address,
                mac => $mac
            );
        }
    }

    for (@signal) {
        if (/\.(\d+).0.0\s+=\s+INTEGER:\s+(-\d+)/) {
            my ($port, $signal) = ($1, $2);
            my @a = map {$_ / 100} $signal;
            my $signal_tenth = sprintf("%.1f", @a);
            comparison(
                ip_olt   => $ip_address,
                signal_port => $port,
                signal      => $signal_tenth
            );
            add(
                signal_port => $port,
                ip_olt   => $ip_address,
                signal => $signal_tenth
            ); 
        }
    }
}

sub comparison {
    my (%h) = @_;
    my $ip_olt      = $h{ip_olt}        || '';
    my $mac_port    = $h{mac_port}      || '';
    my $mac         = $h{mac}           || '';
    my $signal_port = $h{signal_port}   || '';
    my $signal      = $h{signal}        || ''; 
    if ($mac_port = $signal_port) {
        refresh(
            ip_olt => $ip_olt,
            port   => $mac_port,
            signal => $signal,
        );
    } 
}

sub refresh {
    my (%h) = @_;
    my $ip     = $h{ip_olt};
    my $port   = $h{port};
    my $signal = $h{signal};
    my $olt_count = $dbh->selectrow_array("SELECT Count(number) FROM olt_$ip WHERE number = ?", undef, $port) ;
    if ($olt_count > 0) {
        $dbh->do("UPDATE olt_$ip SET sugnal=? WHERE number=?", undef, $signal, $port) ;
        print "update $port\n";
    }
}

sub add {
    my (%h)     = @_;
    my $ip      = $h{ip_olt};
    my $mac_port    =  $h{mac_port};
    my $mac         = $h{mac};
    my $signal_port = $h{signal_port};
    my $signal      = $h{signal};
    my $olt_count =
      $dbh->selectrow_array("SELECT Count(number) FROM olt_$ip WHERE number = ?", undef, $mac_port);
    if ($olt_count < 0) {
        $dbh->do("INSERT INTO olt_$ip VALUES(?, ?, ?, '','','');", undef, $mac_port, $signal, $mac);
    }
}
