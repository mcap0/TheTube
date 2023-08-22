## Info
Si vuole progettare la base di dati necessaria a supportare una piattaforma di messaggistica criptata tramite database relazionale. Le scelte di implementazione sono incentrate sulla sicurezza. La piattaforma e le sue funzioni sono basate sui bisogni dell'utente, per usare la piattaforma è necessario avere un client Python per effettuare le operazioni di encrypting, decrypting dei dati.

## Installazione
Installazione Locale via MySQL Shell
```mysql
\connect -u root
#password:root
\sql
#Switch to sql mode
CREATE DATABASE The_Tube;
use The_Tube;

\source The_TubeTables.sql # importa le tabelle
show tables; #stampa le 3 tabelle

\source TheTubeSP.sql # importa le stored procedures e le funzion
show procedure status where db = 'The_Tube'

CREATE USER 'TheTubeAPI'@'localhost' IDENTIFIED BY 'la_tua_password'; 
GRANT EXECUTE ON *.* TO 'TheTubeAPI'@'localhost';
```

Adesso che abbiamo configurato tutto, apriamo una finestra di PowerShell o Bash per eseguire lo script python `The_Tube.py`

> Se non si possiedono i moduli `mysql-connector`, `rsa` sarà necessario installarli con pip

```pip
pip install rsa;
pip install mysql-connector-python
```

```shell
mkdir keys;
python The_Tube.py
```
