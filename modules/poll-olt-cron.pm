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

require "../config.pl";

our %conf;

my $dbh = DBI->connect(
    "DBI:mysql:" . $conf{dbuser} . ":" . $conf{dbhost}, 
    $conf{dbuser}, 
    $conf{dbpasswd}, 
    {
        mysql_enable_utf8       => 1,
        PrintError              => 1,
        mysql_client_found_rows => 1,
    }
);

$dbh->do("set names utf8");

my $ips = $dbh->selectcol_arrayref("select ip from olt order by ip");

for my $ip_address (@$ips) {

    my $ip_address_conver = unpack "N", inet_aton($ip_address);

    my $snmp_mac    = `snmpwalk -v2c -c public $ip_address $OID{mac}`;
    my $snmp_signal = `snmpwalk -v2c -c public $ip_address $OID{signal}`;

    my %ports =
      map {
        my ($port, $mac);
        (($port, $mac) = /\.(\d+)\s+=\s+Hex-STRING:\s+([0-9A-F\s]+)/)
          ? ($port, {mac => $mac =~ s/\s+$//r =~ tr/ /:/r =~ tr/A-Z/a-z/r})
          : ()
      }
      split(/\n/, $snmp_mac);
    for (split(/\n/, $snmp_signal)) {
        if (/\.(\d+).0.0\s+=\s+INTEGER:\s+(-\d+)/) {
            $ports{$1}{signal} = sprintf("%.1f", $2 / 100);
        }
    }
    for my $port (keys %ports) {
        if (exists $ports{$port}{signal}) {
            my $updated =
              $dbh->do("UPDATE olt_$ip_address_conver SET sugnal=? WHERE number=?", undef, $ports{$port}{signal}, $port);
            if ($updated == 0) {
                $dbh->do(
                    "INSERT INTO olt_$ip_address_conver (number, sugnal, mac, address, serial) VALUES(?, ?, ?, '','')",
                    undef, $port,
                    $ports{$port}{signal},
                    $ports{$port}{mac}
                );
            }
        } else {
            my ($olt_count) =
              $dbh->selectrow_array("SELECT Count(number) FROM olt_$ip_address_conver WHERE number = ?",
                undef, $port);
            if (!$olt_count) {
                $dbh->do(
                    "INSERT INTO olt_$ip_address_conver (number, sugnal, mac, address, serial) VALUES(?, ?, ?, '','')",
                    undef, $port, undef, $ports{$port}{mac});
            }
        }
    }
}

$dbh->disconnect;

1;
