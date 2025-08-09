
### BD
```bash
CREATE DATABASE IF NOT EXISTS db_OCULUS CHARACTER SET utf8mb4 COLLATE utf8mb4_spanish_ci;

CREATE USER IF NOT EXISTS 'admin'@'localhost' IDENTIFIED BY 'ad123.';
GRANT ALL PRIVILEGES ON db_OCULUS.* TO 'admin'@'localhost';
FLUSH PRIVILEGES;

```


```bash
SELECT user, host FROM mysql.user;
SHOW GRANTS FOR 'adminNotes'@'localhost';

```

```bash
Usuario =   superAdmin
Correro =   admin@superadmin.com
Contraseña =   ad123.
```
