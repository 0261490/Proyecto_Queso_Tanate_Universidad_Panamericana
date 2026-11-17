# Sección 5: PWA accesible y offline

## Estado

**Completada al 17 de noviembre de 2026.** El usuario confirmó la comprobación
final de instalación y funcionamiento offline y autorizó el cierre documental.
La aceptación manual se registra como confirmación del usuario; no se
reportaron navegador ni versión. Las pruebas y la compilación aprobadas en
Docker, así como la revisión del flujo y vista de 320 px, corresponden al
5 de noviembre. No se ejecutó una nueva prueba de navegador durante este cierre.

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
Después de editar respuestas se oculta el resultado anterior y se debe pulsar
nuevamente el botón de análisis.

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
navegaciones devuelve primero el HTML de su propia caché, incluso con red, para
mantener juntos el documento y los recursos de la misma compilación. Las nuevas
versiones llegan al actualizar el service worker. Para otros recursos consulta
su propia caché primero y almacena respuestas de red válidas cuando falta el recurso.

La interfaz distingue el estado de red de la preparación offline. El aviso
«Lista para usar sin conexión en este navegador» indica que el documento está
controlado por un service worker; no sustituye la prueba real de recarga y cálculo.

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

## Validación de preparación — 5 de noviembre de 2026

| Comprobación | Resultado |
| --- | --- |
| PWA en Docker | 11/11 aprobadas, incluidas tres pruebas de ejecución del service worker con caché/red simuladas |
| Motor en Docker | 28/28 aprobadas |
| Suite científica Python en Docker | 30/30 aprobadas; avisos de deprecación de pgmpy, sin fallos |
| Compilación Linux con dependencias aisladas | Correcta; Vite 7.3.7, siete recursos precacheados |
| Auditoría npm | Cero vulnerabilidades después de actualizar Vite y source-map-js |
| Modelo congelado | SHA-256 idéntico al registrado arriba |
| Navegador integrado, con servidor disponible | Siete preguntas, error por omisiones, progreso, 9.8 % / 81.4 %, cambio de recomendación, reinicio y teclado comprobados |
| Vista de 320 px | Corregido el desbordamiento: ancho de contenido igual al ancho útil de 305 px con barra de desplazamiento |
| Navegador integrado, servidor detenido | No aprobado: se recuperó HTML, pero no CSS/JavaScript; causa no determinada, pendiente de contraste en Chrome/Edge |
| Instalación en Chrome/Edge | Pendiente; el usuario eligió realizar la comprobación guiada |

Correcciones de esta preparación:

- eliminar el ancho mínimo del body que producía desplazamiento horizontal;
- conservar texto de conexión en móvil y mejorar contraste del botón principal;
- respetar movimiento reducido al desplazar la página desde JavaScript;
- ocultar resultados anteriores cuando se modifica una respuesta;
- mostrar un estado específico de preparación offline;
- servir HTML y recursos desde la caché de la misma versión;
- agregar pruebas del worker para navegación y recursos sin red, coherencia de
  versión y limpieza limitada a cachés Tenate.

Las pruebas simuladas no certifican por sí solas la instalación ni la recarga
offline real. La comprobación de teclado/semántica tampoco equivale a una
auditoría integral WCAG o a una prueba con lector de pantalla.

### Comandos reproducibles

```text
docker compose run --rm -v tenate-pwa-linux-deps:/workspace/pwa-app/node_modules node sh -c 'npm --prefix pwa-app ci && npm --prefix pwa-app test && npm --prefix pwa-app run build'
docker compose run --rm node npm --prefix inference-engine test
docker compose run --rm python python -m unittest discover -s tests -p "test_*.py"
```

El volumen Linux conserva las dependencias locales de Windows sin reemplazarlas.

### Aceptación final — 17 de noviembre de 2026

Tras recibir la lista de pendientes (instalación, recarga y cálculo offline de
81.4 % y 9.8 %), el usuario confirmó: «ya lo confirme esta perfecto» y autorizó
cerrar la documentación. Esta confirmación satisface la aceptación pendiente.

| Comprobación | Registro de cierre |
| --- | --- |
| Instalación y apertura | Aceptadas por confirmación del usuario |
| Recarga y cálculo offline | Aceptados por confirmación del usuario |
| Navegador y versión | No reportados |
| Evidencia de aceptación | Confirmación del usuario en el chat del 17 de noviembre de 2026 |

Se conserva el ensayo fallido del navegador integrado del 5 de noviembre como
antecedente histórico; no se atribuye una causa ni una corrección no comprobadas.
El cierre actual se sustenta en la posterior aceptación del usuario. Se actualizan
la documentación técnica y el Google Doc privado. El historial local queda
fuera de esta sección y corresponde a la Sección 6.

## Control de cambios

La implementación base está en `a33ed84`. El 6 de noviembre de 2026 el usuario
autorizó el commit y push de esta actualización, conservando los pendientes de
aceptación y sin crear la etiqueta de cierre. Se incorporan también sus ajustes
visuales: queso en la cabecera, ilustración central con paisaje sin caja,
eliminación de la frase de acompañamiento y pie «incluso sin conexión».
Mantener fuera de la entrega
la eliminación previa de `docs/seccion-1-documentacion.md` y el archivo no seguido
`resultados-pruebas-motor.txt`. El documento explicativo permanece en Google Drive.
