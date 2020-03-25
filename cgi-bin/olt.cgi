#!/usr/bin/perl
use CGI qw/:standard/;
use strict;
use warnings;
use DBI;
use utf8;
use Socket;

binmode(STDOUT,':utf8');
use POSIX;

my $cgi = new CGI; 
my $source   = "DBI:mysql:cdata:localhost";
my $username = "cdata";
my $password = "cdata";
my $dbh      = DBI->connect(
    $source,
    $username,
    $password, {
        mysql_enable_utf8       => 1,
        PrintError              => 1,
        mysql_client_found_rows => 1,
    }
);

$dbh->do("set names utf8");

print $cgi->header(
    -charset=>'UTF-8'
);

print $cgi->start_html(
    -title=>'Cdata Control',
    -style=>{'src'=>'/cdata/style.css'}
);

print qq'<div class="block-round-content"><a href="index.cgi">Панель управления Cdata</a> </div>';
my $sth;
my @olt_ip = split( /\&/, $ENV{'QUERY_STRING'});
olt($olt_ip[0]);

sub olt($) {
    my $x = shift;
    my $ip = unpack("N",pack("C4",split(/\./,$x)));
    if ($cgi->param('sort')){
        $sth = $dbh->prepare("select number, sugnal, mac, address, serial from olt_$ip order by address;");
        $sth->execute;
    } else {
        $sth = $dbh->prepare("select number, sugnal, mac, address, serial from olt_$ip order by number;");
        $sth->execute;
    }    
    print "<h3 align=\"center\">$x</h3>";
    print qq'<center><FORM action="olt.cgi?$x" METHOD="POST"><INPUT name="edit" type="Submit" value="ОПРОСИТЬ OLT"><INPUT name="sort" type="Submit" value="Сортировка А-Я"></FORM></center><br>';
    print qq'
    <table border="1"><th>Номер порта</th><th>MAC</th><th>Сигнал</th><th>Описание</th><tr></tr>';
    while (my $ref = $sth->fetchrow_hashref()) {
        my $query = $ENV{'QUERY_STRING'};        
        print "<tr onclick=\"document.location = 'onu.cgi?$query&$ref->{'number'}'\" >";
        my $port = $ref->{'number'};  
        for ($port){
            my ($v, $p) = (floor($_/256) % 256 - 10, $_ % 64);
            print  "<td><b>",$v,"/",$p,"</b><br><small>",$port,"</small></td>";
        }
        print "<td>", $ref->{'mac'},"</td>"; 
        my $signal = $ref->{'sugnal'};
        for ($signal){
            if ($_ >= -24.9 && $_ <= -8){
                print "<td><font color=\"green\">", $signal,"</font></td>"; 
            }
            elsif ($_ >= -26 && $_ <= -25){
                print "<td><font color=\"#ff8000\">", $signal,"</font></td>"; 
            }
            elsif ($_ == ''){
                print "<td><font color=\"red\">Offline</font></td>"; 
            }
            else {
                print "<td><font color=\"red\">", $signal,"</font></td>";
            }
        }
        print "<td><font color=\"blue\">", $ref->{'address'},"</font><br><small>",$ref->{'serial'},"</small></td>";
        print "</tr>"; 
    }
    print qq'</table>';
    if ($cgi->param('edit')){
       mysql($x); 
    }
}

sub mysql {
    my $ip_address = shift;

    my %OID = (
        mac    => '1.3.6.1.4.1.17409.2.3.4.1.1.7',
        signal => '1.3.6.1.4.1.17409.2.3.4.2.1.4'
    );
    
    
    for ($ip_address) {
        my $ip_address_conver = unpack "N", inet_aton($_);

        my $snmp_mac    = `snmpwalk -v2c -c public $_ $OID{mac}`;
        my $snmp_signal = `snmpwalk -v2c -c public $_ $OID{signal}`;

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
}

$sth->finish;    
$dbh->disconnect;
