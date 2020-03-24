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
my $dbh = DBI->connect($source, $username, $password, {mysql_enable_utf8 => 1});
$dbh->do("set names utf8");

print $cgi->header(
    -charset=>'UTF-8'
);

print $cgi->start_html(
    -title=>'Cdata Control',
    -style=>{'src'=>'/cdata/style.css'}
);

print qq'
    <form method="post" action="/cdata/cgi-bin/new-olt.cgi" > 
        <input type="name" name="ip" required placeholder="IP" >
        <input type="name" name="name" required placeholder="Имя" >
        <input type="submit" value="Отправить" >
    </form>';

if ($cgi->param('ip')){
    my $ip = $cgi->param('ip');
    my $name = $cgi->param('name');
    my $ip_olt = unpack("N",pack("C4",split(/\./,$ip)));

    $dbh->do("INSERT INTO olt VALUES($ip_olt, '$name');"); 
    my $sth = $dbh->prepare("CREATE TABLE olt_$ip_olt (
        number      int(11) ,
        sugnal      int(11) ,
        mac         varchar(50),
        address     varchar(50),
        voltage     int(11) ,
        serial      varchar(100) 
    );");
    $sth->execute;
}


