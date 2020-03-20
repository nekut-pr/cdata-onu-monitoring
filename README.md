Настройки Apache
===========
```
Alias /cdata/ "/var/www/cdata/"
<Directory "/var/www/cdata">
    Options FollowSymLinks Indexes MultiViews
    AllowOverride All
    Order allow,deny
    Allow from all
</Directory>

<VirtualHost *:80>
        DocumentRoot "/var/www/cdata/"
        ServerName  cdata.domen.org
        ServerAlias www.cdata.domen.org
        ErrorLog ${APACHE_LOG_DIR}/error_cdata.log
        CustomLog ${APACHE_LOG_DIR}/access_cdata.log combined
        Alias /cdata/ "/var/www/cdata/"
</VirtualHost>

<Directory "/var/www/cdata/cgi-bin/">
    Options FollowSymLinks Indexes MultiViews
    AllowOverride All
    Order allow,deny
    Allow from all
       Options +ExecCGI
       SetHandler cgi-script
       AllowOverride All
</Directory>
```
