# Sección 5: PWA accesible y offline

## Estado

Entrega de implementación con siete preguntas originales. Validación final en Docker/navegador y etiqueta de cierre sprint-5 pendientes.

## Alcance

La PWA entrega el primer flujo completo para el productor: presenta preguntas
naturales, valida que estén respondidas, traduce las respuestas mediante la
Sección 4, ejecuta inferencia exacta en el navegador y explica la probabilidad
estimada de intención de compra.

La pregunta de intención de compra no se incluye como evidencia. Es la variable
de resultado; preguntarla antes de inferirla produciría una respuesta circular y
una probabilidad trivial de cero o cien por ciento. Se conservan las otras
siete preguntas del catálogo original y se envían todas sus respuestas al
traductor y al motor. No se filtra la recomendación ni se modifica el modelo.

## Limitación conocida del resultado

Al observar recomendación, el DAG congelado hace que las demás respuestas no
aporten información adicional sobre intención de compra. Por ello, las 128
combinaciones del formulario se distribuyen en dos resultados:

| Recomendación | Probabilidad de compra | Combinaciones |
| --- | ---: | ---: |
| Sí | 81.4 % (96/118) | 64 |
| No | 9.8 % (5/51) | 64 |

La variable sensorial está aislada. Esta es una propiedad de la estructura
reconstruida, no un fallo de redondeo. Se preservan las siete preguntas y el
proceso original por decisión del usuario. El ensayo de cuatro preguntas se
retiró y no forma parte del entregable. No se afirma que las siete preguntas
influyan independientemente ni que más respuestas Sí aumenten el resultado.
Después de editar respuestas se debe pulsar nuevamente el botón de análisis.

## Componentes

- encabezado con estado de conectividad e instalación;
- introducción que explica privacidad y funcionamiento local;
- formulario generado desde el catálogo congelado de la Sección 4;
- tarjetas con iconografía SVG, preguntas naturales y respuestas Sí/No;
- progreso de respuestas y resumen de errores;
- resultado porcentual, interpretación prudente y advertencia de alcance;
- manifiesto instalable, íconos PNG de 192 y 512 píxeles, respaldo SVG y
  service worker precacheado;
- diseño responsive para teléfono, tableta y escritorio.

No se incorporó persistencia de respuestas o resultados porque corresponde a
la Sección 6.

## Accesibilidad

La interfaz se diseñó para uso con teclado, lector de pantalla, ampliación y
preferencias del sistema:

- idioma `es-MX`, títulos jerárquicos y regiones semánticas;
- enlace para saltar directamente al cuestionario;
- cada pregunta usa `fieldset` y `legend`;
- controles de radio nativos con etiquetas completas y áreas táctiles amplias;
- foco visible con contraste alto y retorno de foco al reiniciar;
- errores anunciados mediante `role="alert"`;
- resultados anunciados mediante `aria-live="polite"` y `role="meter"`;
- iconos decorativos ocultos del árbol de accesibilidad;
- estado de conexión anunciado sin depender únicamente del color;
- compatibilidad con `prefers-reduced-motion` y `prefers-contrast`;
- maquetación fluida desde 320 px y controles apilados en pantallas estrechas;
- texto alternativo funcional cuando JavaScript está deshabilitado.

La gráfica circular nunca es la única fuente del resultado: el porcentaje y su
interpretación aparecen también como texto.

## Funcionamiento offline

Vite crea el paquete estático y el script posterior enumera todos sus recursos,
calcula una huella de contenido y genera `dist/sw.js`. Durante la instalación,
el service worker precarga HTML, JavaScript, CSS, manifiesto e iconografía. En
navegaciones sin red devuelve el documento precacheado; para otros recursos usa
caché primero y actualiza la caché cuando obtiene una respuesta válida.

Al activar una versión nueva, elimina únicamente cachés anteriores cuyo nombre
empieza con `tenate-`. No interviene sobre cachés ajenas al proyecto.

## Instalación y verificación

Las instrucciones reproducibles de desarrollo, compilación, previsualización e
instalación están en `pwa-app/README.md`. Comandos de validación:

```text
docker compose run --rm node npm --prefix pwa-app test
docker compose run --rm node npm --prefix pwa-app run build
```

Las pruebas cubren el marcado semántico, ausencia de identificadores Q1–Q8 en la
interfaz, controles accesibles, formato localizado de probabilidades, bandas de
interpretación, manifiesto relativo, foco visible, preferencias de movimiento y
contraste, así como las estrategias esenciales del service worker.

## Validación de preparación — 30 de octubre de 2026

- Node.js 24.19.0: 8 pruebas PWA y 28 pruebas del motor aprobadas.
- Compilación Vite correcta; siete recursos en el precache generado.
- Las 128 combinaciones del formulario original reproducen 81.4 % / 9.8 %.
  La prueba de regresión verifica los conteos de 64 casos por cada resultado
  y compara el motor con las probabilidades empíricas independientes 96/118 y 5/51.
- SHA-256 del modelo sin cambios:
  `8ecb6ae7cd8236aa3e7930287bb8ae51f4828cbe97baf138d63bb75388800f3b`.
- `git diff --check` sin errores.

### Comprobaciones pendientes antes del cierre

Docker Desktop responde que no puede iniciar. La alternativa Python local
no pudo cargar seis módulos de pruebas: faltan pandas, numpy, pgmpy y networkx.
Esto es una limitación del entorno, no una suite científica aprobada.
La prueba automática de Edge no se ejecutó porque se rechazó su autorización.

1. Con Docker operativo, ejecutar pruebas PWA, build, pruebas del motor y
   `docker compose run --rm python python -m unittest discover -s tests -p "test_*.py"`.
   Si node_modules contiene binarios Windows, usar un volumen aislado de Linux
   para las dependencias del contenedor, sin borrar las dependencias locales.
2. Abrir la compilación con preview y comprobar siete preguntas, errores ante
   respuestas pendientes, progreso, navegación por teclado y vista a 320 px.
3. Probar todas No (9.8 %) y todas Sí (81.4 %). Mantener recomendación y
   cambiar otras respuestas debe conservar el resultado al volver a calcular.
   Cambiar recomendación debe alternar los dos valores. Reiniciar debe limpiar
   selecciones y progreso.
4. Esperar al service worker, desconectar la red, recargar y volver a calcular.
   Verificar instalación desde un navegador compatible. El servidor dev no
   sustituye esta comprobación de la compilación de producción.
5. Actualizar el estado con la evidencia obtenida; crear commit de cierre y etiqueta
   únicamente cuando las comprobaciones hayan terminado satisfactoriamente.

## Alcance previsto del commit

Incluir `pwa-app/` (incluida la retirada de su .gitkeep), esta documentación y
la sección correspondiente del README. El plan maestro contiene además cambios
locales previos de política documental: revisar su diff antes de incorporarlos.
No incluir automáticamente la eliminación previa de
`docs/seccion-1-documentacion.md` ni `resultados-pruebas-motor.txt`.
El Google Doc explicativo existente se actualiza en Drive y no se copia aquí.

Mensaje previsto: `Sprint 5: desarrollar interfaz PWA accesible y offline`.
Esta entrega publica la implementación; no declara el cierre completo ni crea la etiqueta sprint-5 mientras las verificaciones anteriores estén pendientes.
