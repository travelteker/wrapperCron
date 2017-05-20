# wrapperCron
Script para ejecutar otros scripts via crontab sistemas linux, permitiendo registrar los tiempos de ejecución así como la duración del proceso.

# Objetivo:
Obtener un fichero log que podamos procesar por ejemplo con Kibana, y controlar si los procesos del crontab se ejecutan en el tiempo establecido.

Esto es especialmente útil cuando tenemos máquinas que ejecutan multitud de procesos cron, donde podría darse el caso que la salida de un proceso sea necesaria para la ejecución de otro proceso y si el primero no terminó antes de iniciarse el segundo, comenzarán a producirse errores.

# Ejemplo linea Crontab

