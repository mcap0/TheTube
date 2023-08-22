# TheTube: Messaggistica Criptata End-to-End per Terminale

Benvenuto in TheTube, la soluzione di messaggistica criptata per il tuo terminale by matteocapo. La sicurezza è implementata by design:

- **Crittografia Robusta**: Messaggi protetti con crittografia RSA end-to-end per una privacy totale.

- **Gestione Utenti**: Username, public key e hash della private key garantiscono l'identità e l'autenticazione.

- **Chat Sicure**: Ogni chat è identificata univocamente e le conversazioni sono interamente crittografate per massima protezione. Nessuno saprà nemmeno i tuoi contatti!

- **Operazioni Efficiente**: Registrazione, login, creazione di nuove chat e messaggi - tutto gestito in modo veloce e sicuro.

- **Autenticazione Forte**: La private key salvata solo nel tuo computer garantisce l'autenticità e l'integrità dei messaggi.

- **Semplice Integrazione**: Client Python per operazioni di crittografia e decrittografia senza sforzo.
- 
Sii padrone della tua privacy su TheTube, dove la comunicazione diventa sicura e confidenziale come dovrebbe essere.

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
