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

#my $sth = $dbc->prepare("CREATE TABLE olt_1234 (
#  number    int(11),
#  sugnal    int(11),
#  mac       varchar(50),
#  address   varchar(50),
#  voltage   int(11)       
#);");

print qq'
    <form method="post" action="" >
        <input type="name" name="ip" required placeholder="IP" >
        <input type="name" name="name" required placeholder="Имя" >
        <input type="submit" value="Отправить" >
    </form>';
