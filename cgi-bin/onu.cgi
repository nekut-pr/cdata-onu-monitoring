#!/usr/bin/perl
use CGI qw/:standard/;
use strict;
use warnings;
use DBI;
use utf8;
binmode(STDOUT,':utf8');

my $cgi = new CGI; 
my $source = "DBI:mysql:cdata:localhost";
my $username = "cdata";
my $password = "cdata";
my $dbc = DBI->connect($source, $username, $password, {mysql_enable_utf8 => 1});
$dbc->do("set names utf8");

print $cgi->header(
    -charset=>'UTF-8'
);

print $cgi->start_html(
    -title=>'Cdata Control',
    -style=>{'src'=>'/cdata/style.css'}
);

print qq'<div class="block-round-content"><a href="index.cgi">Панель управления Cdata</a></div>';

my $sth;
my @olt_ip = split( /\&/, $ENV{'QUERY_STRING'});
olt($olt_ip[0], $olt_ip[1]);

sub olt($) {
    my $x = shift;
    my $y = shift;
    my $ip = unpack("N",pack("C4",split(/\./,$x)));
    $sth = $dbc->prepare("SELECT number, sugnal, mac, address, voltage  FROM olt_$ip WHERE number=$y;");
    $sth->execute;
    print qq'<table border=1><tr><th>number</th><th>Signal</th><th>MAC</th><th>Адрес</th><th>Напряжение</th></tr>';
    while (my $ref = $sth->fetchrow_hashref()) {
        print "<tr>";
        print "<td>", $ref->{'number'},"</td>";
        print "<td>", $ref->{'sugnal'},"</td>"; 
        print "<td>", $ref->{'mac'},"</td>"; 
        print "<td>", $ref->{'address'},"</td>"; 
        print "<td>", $ref->{'voltage'},"</td>";
        print "<td><a href=\"onu.cgi?$x&$y&edit\">Edit</a></td>";
    }   
}

my @edit = split( /\&/, $ENV{'QUERY_STRING'});
edit($edit[0], $edit[1], $edit[2]);

sub edit($) {
    my $ip = shift;
    my $onu = shift;
    my $var = shift;
    my $ip_olt = unpack("N",pack("C4",split(/\./,$ip)));

    if ($var eq "edit"){
        print qq'
        <form method="post" action="onu.cgi?$ip&$onu" >
            Редактировать адрес: 
            <input type="name" name="edit_param" required placeholder="Адрес" >
            <input type="submit" value="Отправить" >
        </form>';
    }

    if ($cgi->param('edit_param')){
        my $edit_param = $cgi->param('edit_param');
        $sth = $dbc->prepare("UPDATE olt_$ip_olt SET address='$edit_param' WHERE number=$onu;");
        $sth->execute;
    }
}

$sth->finish;    
$dbc->disconnect;
