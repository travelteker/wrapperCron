# wrapperCron
Script para ejecutar otros scripts via crontab sistemas linux, permitiendo registrar los tiempos de ejecución así como la duración del proceso.

# Objetivo:
Obtener un fichero log que podamos procesar por ejemplo con Kibana, y controlar si los procesos del crontab se ejecutan en el tiempo establecido.

Esto es especialmente útil cuando tenemos máquinas que ejecutan multitud de procesos cron, donde podría darse el caso que la salida de un proceso sea necesaria para la ejecución de otro proceso y si el primero no terminó antes de iniciarse el segundo, comenzarán a producirse errores.

# Ejemplo linea Crontab
*/5 * * * * /usr/bin/nice /usr/bin/python /home/user/wrapperCron.py -lphp -p/home/user/myScripts/script.php

Cada 5 min se ejecutaría el fichero "/home/user/myScrits/script.php"

Y la salida del wrapperCron sería algo como:

20/05/2017 21:15:01.570607|1495307701|20/05/2017|21:15:01|592095b58b4d8|php|/home/user/myScripts/script.php|script.php|---|0|0|54|---|---

# Uso del wrapper en cron:
>*/5 * * * * (Indicar marco horario de ejecución)

>/usr/bin/nice (Tener en cuenta nice, para usarlo con los valores por defecto)

>/usr/bin/python (path donde encontrar el ejecutable python)

>/home/user/wrapperCron.py (path absoluto donde encontrar el fichero que queremos ejecutar)

>-lphp (-l es un argumento del script a ejecutar que indica el lenguaje del script embebido que tenemos que ejecutar)

>-p/home/user/myScripts/script.php (-p es un argumento para indicar el paht absoluto de nuestro script embebido)

>-a (si lo hubiera es otro argumento que indicaría los parámetros que necesita nuestro script embebido para su ejecución)

