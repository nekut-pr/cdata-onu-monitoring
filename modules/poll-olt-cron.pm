#!/usr/bin/perl
use warnings;
use strict;
use DBI;
use utf8;

binmode(STDOUT,':utf8');

my %OID = (
    mac => '1.3.6.1.4.1.17409.2.3.4.1.1.7',
    signal => '1.3.6.1.4.1.17409.2.3.4.2.1.4'
);

my $source = "DBI:mysql:cdata:localhost";
my $username = "cdata";
my $password = "cdata";
my $dbc = DBI->connect($source, $username, $password, {mysql_enable_utf8 => 1});
$dbc->do("set names utf8");

my $sth = $dbc->prepare("SELECT ip FROM olt;");
$sth->execute;

while (my $ref = $sth->fetchrow_hashref()) {

    my $ip_address = $ref->{'ip'};

    my $snmp_mac = `snmpwalk -v2c -c public $ip_address $OID{mac}`;
    my $snmp_signal = `snmpwalk -v2c -c public $ip_address $OID{signal}`;
   
    my @mac = split(/\n/, $snmp_mac);
    my @signal = split(/\n/, $snmp_signal);   

    for(@mac) { 
        if( /\.(\d+)\s+=\s+Hex-STRING:\s+([0-9A-F\s]+)/ ) { 
            my ($port, $mac) = ($1, $2); 
            $mac =~ s/\s+$//; 
            $mac =~ tr/A-Z/a-z/;
            $mac =~ tr/ /:/; 
            comparison(
                mac_port => $port,
                mac => $mac,
                ip_olt   => $ip_address

            );
            add(
                mac_port => $port,
                mac => $mac,
                ip_olt   => $ip_address

            );
        } 
    }

    for (@signal){
        if ( /\.(\d+).0.0\s+=\s+INTEGER:\s+(-\d+)/ ){
            my ($port, $signal) = ($1, $2);
            my @a = map { $_ / 100} $signal;  
            my $signal_tenth = sprintf("%.1f", @a);
            comparison(
                signal_port => $port,
                signal => $signal_tenth,
                ip_olt   => $ip_address
            );
            add(
                signal_port => $port,
                signal => $signal_tenth,
                p_olt   => $ip_address
            );              
        }
    }
}

sub comparison {  
    my (%h) = @_;
    my $ip = delete $h{ip_olt};

    my $mac_port = delete $h{mac_port};
    my $mac = delete $h{mac};

    my $signal_port = delete $h{signal_port};
    my $signal = delete $h{signal};

    if ( $mac_port = $signal_port ) {
        refresh(
            port => $mac_port,
            signal => $signal,
            ip_olt => $ip
        );
    }
}

sub refresh {
    my (%h) = @_;
    my $ip     = $h{ip_olt};

    my $port =  $h{port};
    my $signal =  $h{signal};
    my $sth = $dbc->prepare("SELECT Count(number) FROM olt_$ip WHERE number = '$port'");
    $sth->execute;
    while (my $ref = $sth->fetchrow_hashref()) {    
        if ($ref->{'Count(number)'} > 0){
            print $signal;
            my $sth = $dbc->prepare("UPDATE olt_$ip SET sugnal='$signal' WHERE number=$port;");
            $sth->execute;
        }    
    }
}

sub add {
    my (%h) = @_;
    my $ip     = $h{ip_olt};

    my $mac_port =  $h{mac_port};
    my $mac =  $h{mac};

    my $signal_port =  $h{signal_port};
    my $signal =  $h{signal};

    my $sth = $dbc->prepare("SELECT Count(number) FROM olt_$ip WHERE number = '$mac_port'");
    $sth->execute;
    while (my $ref = $sth->fetchrow_hashref()) {    
        unless ($ref->{'Count(number)'} > 0){
            my $sth = $dbc->prepare("INSERT INTO olt_$ip VALUES($mac_port, '$signal', '$mac', '','','');");
            $sth->execute; 
        }
    }
}

$sth->finish;    
$dbc->disconnect;

1;
