import matplotlib.pyplot as plt
import numpy as np

# Listas para almacenar los datos
eje_x_problemas = []
eje_y_tiempos = []

archivo_entrada = '/home/jorge/JSHOP2/JSHOP2/domains/emergencias/benchmark.txt'

with open(archivo_entrada, 'r') as f:
    for linea in f:
        if 'Problema' in linea or '---' in linea or '|' not in linea:
            continue
        try:
            partes = linea.split('|')
            n_problema = int(partes[0].strip().replace('p', ''))
            tiempo = float(partes[1].strip())
            
            eje_x_problemas.append(n_problema)
            eje_y_tiempos.append(tiempo)
        except (ValueError, IndexError):
            continue

# Convertir a arrays de numpy para cálculos matemáticos
x = np.array(eje_x_problemas)
y = np.array(eje_y_tiempos)

# Calcular la línea de tendencia (regresión lineal de grado 1)
z = np.polyfit(x, y, 1)
p = np.poly1d(z)

# Crear la gráfica
plt.figure(figsize=(10, 6))

# Dibujar los datos reales
plt.plot(x, y, marker='o', linestyle='-', color='teal', label='Datos Reales (JSHOP2)', alpha=0.6)

# Dibujar la línea de tendencia (puntos discontinuos)
plt.plot(x, p(x), color='red', linestyle='--', linewidth=2, label='Tendencia Lineal')

# Configuración de estética
plt.title('Escalabilidad de JSHOP2 con Línea de Tendencia')
plt.xlabel('Número de Personas / Cajas')
plt.ylabel('Tiempo de ejecución (segundos)')
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend()

# Guardar la gráfica para la memoria
plt.tight_layout()
plt.savefig('grafica_emergencias_tendencia.png')
plt.show()

print(f"Ecuación de la recta: y = {z[0]:.6f}x + {z[1]:.6f}")