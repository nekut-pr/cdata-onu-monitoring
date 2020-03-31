#!/usr/bin/perl
use CGI qw/:standard/;
use strict;
use warnings;
use DBI;
use utf8;
binmode(STDOUT,':utf8');
use POSIX;
my $sth;
my $cgi = new CGI; 
my $source = "DBI:mysql:cdata:localhost";
my $username = "cdata";
my $password = "cdata";
my $dbh = DBI->connect($source, $username, $password, {mysql_enable_utf8 => 1});
$dbh->do("set names utf8");

print $cgi->header(
    -charset=>'UTF-8'
);

print $cgi->start_html(
    -title=>'Cdata Control',
    -style=>{'src'=>'/cdata/style.css'}
);

print qq'<div class="block-round-content"><a href="index.cgi">Панель управления Cdata</a></div>';

my @olt_ip = split( /\&/, $ENV{'QUERY_STRING'});
olt($olt_ip[0], $olt_ip[1]);

sub olt($) {
    my ($x, $y) = @_;
    my $ip = unpack("N",pack("C4",split(/\./,$x)));
    $sth = $dbh->prepare("SELECT number, sugnal, mac, address, area, serial FROM olt_$ip WHERE number=$y;");
    $sth->execute;
    print qq'<center><FORM action="olt.cgi?$x" METHOD="POST"><INPUT name="back" type="Submit" value="Назад на OLT"></center></form><br>';         
    print qq'<table border=1><tr><th>Ветка/Порт</th><th>Сигнал</th><th>MAC</th><th>Адрес</th><th>Район</th><th>Серийный номер</th></tr>';
    while (my $ref = $sth->fetchrow_hashref()) {
        print "<tr>";
        my $port = $ref->{'number'};
        for ($port){
            my ($v, $p) = (floor($_/256) % 256 - 10, $_ % 64);
            print  "<td><b>",$v,"/",$p,"</b><br><small>",$port,"</small></td>";
        }
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
        print "<td>", $ref->{'mac'},"</td>"; 
        print   
        "<td>", 
            $ref->{'address'},"<br>
            <span style=\"font-size: 15px;\">
                <a href=\"onu.cgi?$x&$y&edit-address\">Редактировать</a>
            </span>
        </td>"; 
        print
        "<td>", $ref->{'area'}, "<br>
        <span style=\"font-size: 15px;\">
                <a href=\"onu.cgi?$x&$y&edit-areas\">Изменить</a>
            </span>
        </td>"; 
        print
        "<td>", 
            $ref->{'serial'},"<br>
            <span style=\"font-size: 15px;\">
                <a href=\"onu.cgi?$x&$y&edit-serial\">Изменить</a>
            </span>
        </td>";  
        print qq'<td>
           <FORM action="" METHOD="POST">
                <BUTTON name="ref" type="Submit" value="Сигнал"><img src="../images/icon-refresh.png" width="40" height="40" onclick="history.back();" onclick="window.location.reload()"></BUTTON>
           </FORM>
            </td>'; 
        if ($cgi->param('ref')){
            refresh($ip, $port);
        }
    }
}

my @edit = split( /\&/, $ENV{'QUERY_STRING'});
edit_address($edit[0], $edit[1], $edit[2]);

sub edit_address($) {
    my ($ip, $onu, $var) = @_;
    my $ip_olt = unpack("N",pack("C4",split(/\./,$ip)));
    if ($var eq "edit-address"){
        print qq'
        <form method="post" action="onu.cgi?$ip&$onu">
            Редактировать адрес: 
            <input type="name" name="edit_address" required placeholder="Адрес">
            <input type="submit" value="Отправить" >
        </form>';
    }
    if ($var eq "edit-serial"){
        print qq'
        <form method="post" action="onu.cgi?$ip&$onu">
            Редактировать серийный номер: 
            <input type="name" name="edit_serial" required placeholder="Номер">
            <input type="submit" value="Отправить" >
        </form>';
    }
    if ($var eq "edit-areas"){
        areas($ip_olt, $onu);
    }
    if ($cgi->param('edit_address')){
        my $edit_param = $cgi->param('edit_address');
        $dbh->do("UPDATE olt_$ip_olt SET address=? WHERE number=?", undef, $edit_param, $onu);
    }
    if ($cgi->param('edit_serial')){
        my $edit_param = $cgi->param('edit_serial');
        $dbh->do("UPDATE olt_$ip_olt SET serial=? WHERE number=?", undef, $edit_param, $onu);
    }
}

sub refresh($){
    my ($ip, $port) = @_;
    my $snmp_signal = `snmpwalk -v2c -c public $ip 1.3.6.1.4.1.17409.2.3.4.2.1.4 | grep $port`;
    my @signal = split(/\s/, $snmp_signal);
    my $str = sprintf("%.1f",  $signal[3] / 100);
    $dbh->do("UPDATE olt_$ip SET sugnal=? WHERE number=?", undef, $str, $port);
}

sub areas($) {
    my ($ip, $port) = @_;
    $sth = $dbh->prepare("select name from areas");
    $sth->execute;
    my $select = $cgi->param('pon');  
    print qq'<form method="post" action="#"><select name="pon" >';
    while (my $ref = $sth->fetchrow_hashref()) {
        my $name = $ref->{'name'};
        print qq'<option value="$name">$name</option>';
    }
    print qq'</select><input type="submit" value="изменить"></form>';
    unless ($select eq "") {
        $dbh->do("UPDATE olt_$ip SET area=? WHERE number=?", undef, $select, $port);
    }
}

$sth->finish;    
$dbh->disconnect;
