По всем вопросам - https://t.me/nekut_pr

Возможности
-----------
+ Мониторинг уровней сиганала на каждой ONU.
+ Хранение адреса установки ONU.
+ Хранение серийного номера ONU.
+ Добавлять новые OLT через WEB интерфейс.


Настройки
-----------

#### Perl (уставнока модулей)
```
perl -MCPAN -e 'install CGI'
perl -MCPAN -e 'install DBI'
```
#### Cron (опрос cdata каждые 5 минут)
```
nano /etc/crontab
*/5 *    * * *   root    perl /var/www/cdata/modules/poll-olt-cron.pm
```
#### Mysql

```
CREATE TABLE olt(ip int(16) unsigned, name varchar(60));
CREATE USER 'cdata'@'localhost' IDENTIFIED BY 'cdata';
GRANT ALL PRIVILEGES ON * . * TO 'cdata'@'localhost';
FLUSH PRIVILEGES;
```
#### Настройка Apache2
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
        ServerName  cdata.domain.org
        ServerAlias www.cdata.domain.org
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
#### Видео

[![Cdata Onu Monitoring](https://prm.ua/wp-content/uploads/2019/04/dc1275f0-282f-11e9-82da-d9da8d55b88b-1024x683.jpeg)](https://www.youtube.com/watch?v=6XcBKonYYc0&feature=youtu.be)
