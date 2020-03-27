По всем вопросам - https://t.me/nekut_pr

Возможности
-----------
- Взаимодействие с OLT:
    - Добавлять новые OLT через WEB интерфейс.
    - Кнопка опроса уровней сигнала и добавления новой ONU.
    - Сортировка.
        - Кнопка сортировки по адресу  (А-Я) дя всей OLT.
        - Cортировка по районам.

- Взаимодействие с каждой ONU:
    - Мониторинг уровней сиганала на каждой ONU.
        - Кнопка обновления уровня сигнала в выбраной ONU.
    - Хранение адреса установки каждой ONU.
    - Хранение серийного номера каждой ONU.

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
- Создание таблицы свитчей.
```
CREATE TABLE olt(ip int(16) unsigned, name varchar(100));
```
- Создать таблицу районов.
```
CREATE TABLE areas(name VARCHAR (100));
```
- Создание пользователя.
```
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
