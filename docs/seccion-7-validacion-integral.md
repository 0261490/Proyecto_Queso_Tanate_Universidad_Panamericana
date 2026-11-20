# Sección 7: validación científica e integración

## Estado y conclusión

Validación automatizada completada localmente el 20 de noviembre de 2026:
**90 pruebas aprobadas** y **128 combinaciones del cuestionario contrastadas
con pgmpy**. Los 128 casos son datos recorridos por pruebas; no se suman como
128 pruebas adicionales al total. Cierre formal identificado con la etiqueta `sprint-7`. El documento explicativo privado permanece en Google Drive.

TypeScript reproduce la inferencia del modelo reconstruido y exportado desde
Python dentro de una tolerancia absoluta de `1e-12`. Esta conclusión no equivale
a recuperar el modelo original de la publicación ni a validar causalidad o
utilidad comercial mediante un estudio con productores.

No se modificaron DAG, CPT, estados, exportador ni datos científicos.
SHA-256 de `model-export/model.json`:
`8ecb6ae7cd8236aa3e7930287bb8ae51f4828cbe97baf138d63bb75388800f3b`.

## Pruebas de referencia

Se conserva `inference-engine/tests/fixtures/python-reference.json` con siete
consultas de variables y evidencias diversas. Se añade
`inference-engine/tests/fixtures/assessment-reference.json`, generado mediante
`inference-engine/tools/generate_assessment_reference.py` y pgmpy VariableElimination.

El generador contiene una correspondencia explícita de las siete preguntas,
independiente del catálogo TypeScript. Para cada combinación produce respuestas,
evidencia esperada y probabilidad; también registra la huella del modelo, su
versión y la comparación con la publicación. No calcula los valores esperados
invocando el motor TypeScript ni copiando constantes de la interfaz.

La opción `--check` regenera en memoria y compara sin sobrescribir el archivo.
Un desacuerdo falla: debe investigarse antes de actualizar una referencia. La
regeneración usa el entorno Python fijado en Docker. El JSON es una referencia
del modelo exportado, no un entrenamiento independiente desde el CSV; la
reconstrucción y el exportador conservan sus propias pruebas Python.

`pwa-app/tests/golden-integration.test.ts` comprueba que hay exactamente 128
combinaciones booleanas únicas, verifica la huella y recorre la cadena:

```text
Referencia pgmpy → respuestas → traductor → inferencia TypeScript
                → registro IndexedDB simulado → lectura → formato visual
```

Resultado: error absoluto máximo Python/TypeScript de
`2.220446049250313e-16`, inferior a `1e-12`. Respuestas y evidencia coinciden
exactamente; probabilidades se comparan con tolerancia y su formato visual coincide.
Los resultados siguen agrupándose en 81.4 % / 9.8 % por la recomendación observada.

## Referencia científica de 62.6 %

| Consulta | Probabilidad |
| --- | ---: |
| `P(Q2=Yes \| Q8=Yes)` publicada, según la auditoría de la sección 2 | 62.6 % |
| Misma consulta en la reconstrucción actual, Python y TypeScript | 59.76331360946746 % |
| Diferencia reconstrucción menos publicación | −2.836686390532539 puntos porcentuales |

Q8 está aislada en el DAG reconstruido y no cambia la marginal de Q2, `101/169`.
La prueba registra el desacuerdo explícitamente y falla si se pierde esa
trazabilidad; no exige que la reconstrucción produzca artificialmente 62.6 %.
Véase `seccion-2-reconstruccion-modelo.md`, apartado 40 y validación probabilística.

Por tanto, el criterio literal de equivalencia con el **modelo original publicado**
no está demostrado. Se valida equivalencia Python/TypeScript para la reconstrucción
documentada. Si se exige equivalencia con el original, se necesita el artefacto
científico original o una revisión científica independiente; no se resuelve
modificando la interfaz o ajustando CPT para acercarse al porcentaje publicado.

## Matriz de cobertura funcional

| Área | Evidencia automatizada | Alcance |
| --- | --- | --- |
| Preparación, estructura, parámetros y exportación Python | `tests/test_*.py` | 30 pruebas existentes |
| Contrato y rechazo de modelos inválidos | `model-loader.test.ts` | JSON, versiones, nodos, ciclos, estados, ejes CPT, dimensiones y probabilidades |
| Inferencia y traductor | Pruebas del motor y siete referencias Python | Evidencia, consultas, errores y normalización |
| Cuestionario completo | `golden-integration.test.ts` y `assessment.test.ts` | Las 128 combinaciones, evidencia, resultado y persistencia simulada |
| Persistencia | `history.test.ts` | Copias, orden, reapertura, duplicados, abortos, errores y aislamiento |
| UI e IndexedDB nativo | `tests/browser/history.spec.ts` | Recarga, reapertura de página, CRUD offline, cuota y permisos |
| Integración con referencias Python en navegador | `tests/browser/validation.spec.ts` | Cuatro combinaciones mixtas, resultado visible y registro exacto offline |
| Validación y UX | `validation.spec.ts` | Siete omisiones, una omisión, foco, selección con teclado, cambio de respuesta y reinicio |
| Presentación y móvil | Pruebas de presentación, recursos y navegador | Lenguaje natural, formato, controles, preferencias CSS y ancho de 320 px |
| Service worker | `service-worker.test.ts` y prueba nativa offline | Precarga, coherencia de versión, limpieza limitada y primera recarga offline |

Las pruebas con teclado usan foco programático para seleccionar cada grupo,
Space y ArrowRight para responder, y Tab/Enter para comprobar controles concretos.
No constituyen una auditoría completa de orden de tabulación ni de lector de pantalla.

## Fallo descubierto y corrección offline

Una prueba nueva desconecta el navegador inmediatamente después del primer aviso
de preparación y recarga, sin una recarga intermedia online. Antes de la corrección,
el HTML reaparecía pero JavaScript/CSS fallaban con `net::ERR_FAILED`: había cero
radios. Las pruebas anteriores habían realizado más navegaciones antes de cortar
la conexión y no detectaron este caso.

Se registró un worker `activated` y los siete recursos precargados. Las respuestas
de Vite preview contenían `Vary: Origin`; las peticiones de precarga no tenían
Origin y las peticiones de módulos/CSS no encontraban su variante en Cache API.
La corrección usa `ignoreVary` únicamente para las URL exactas de los recursos
estáticos del manifiesto de precarga, del mismo origen y compilación. El resto
de peticiones conserva el comportamiento normal. La prueba unitaria adicional
comprueba también que un recurso ajeno a la precarga no recibe esa excepción.

La semántica de comparación se describe en la
[especificación de Cache API, parte de Service Workers](https://www.w3.org/TR/2026/CRD-service-workers-20261029/).
No se trata de ignorar las cabeceras de datos dinámicos ni de borrar IndexedDB.
La primera recarga offline y cuatro evaluaciones mixtas pasaron en Edge tras
la corrección, junto con el resto de las siete pruebas de navegador.

El aviso del usuario sobre tres recargas al actualizar una versión se conserva
como observación distinta: no se demuestra que tuviera esta misma causa. El
flujo de aviso/actualización de versiones sigue siendo mejora pendiente.

## Resultados y cobertura de código

Entorno: Docker Node 24.19.0 y Python 3.12.13 con pgmpy 1.1.2; navegador Edge
157.0.4341.60 en Windows, sin ventana visible y con perfil temporal.

| Suite | Aprobadas |
| --- | ---: |
| Python en Docker | 30/30 |
| Motor TypeScript en Docker | 32/32 |
| PWA e integración en Docker | 21/21 |
| Playwright en Edge | 7/7 |
| Total | 90/90 |
| Compilación PWA en Docker | Correcta; siete recursos precargados |
| Regeneración de referencias con `--check` | 128 casos idénticos |

Cobertura V8 recogida con `node --test --experimental-test-coverage`:

| Conjunto instrumentado | Líneas | Ramas | Funciones |
| --- | ---: | ---: | ---: |
| Motor: módulos cargados de `src/` | 96.76 % | 93.90 % | 100.00 % |
| Cargador del modelo | 100.00 % | 96.74 % | 100.00 % |
| PWA: `presentation.ts` y `storage/history.ts` | 98.25 % | 96.77 % | 84.85 % |

La cifra de PWA **no es cobertura global de la aplicación**: Node no carga
`main.ts` ni `history-ui.ts`, y el filtro tampoco cuenta el worker ejecutado en
VM. Esos flujos se prueban funcionalmente en navegador o VM, sin un porcentaje
de cobertura instrumentada. No se midió porcentaje de cobertura Python.

## Reproducción

Desde la raíz, con Docker iniciado:

```text
docker compose run --rm python python inference-engine/tools/generate_assessment_reference.py model-export/model.json inference-engine/tests/fixtures/assessment-reference.json --check
docker compose run --rm python python -m unittest discover -s tests -p "test_*.py"
docker compose run --rm node npm --prefix inference-engine run test:coverage
docker compose run --rm -v tenate-pwa-linux-deps:/workspace/pwa-app/node_modules node sh -c "npm --prefix pwa-app ci && npm --prefix pwa-app run test:coverage && npm --prefix pwa-app run build"
```

En Windows, con Node 24 y Edge instalado:

```text
npm.cmd --prefix pwa-app ci
npm.cmd --prefix pwa-app run build
npm.cmd --prefix pwa-app run test:e2e
```

Playwright inicia y detiene su servidor en el puerto 4176. Genera un reporte
JSON en `pwa-app/test-results/results.json`, diagnósticos de caché/red para la
primera recarga offline y la captura móvil. Estos artefactos temporales no se
versionan. La matriz, métricas y referencias reproducibles sí quedan en el repositorio.

## Límites y pendientes

- Sin estudio de usabilidad con productores ni auditoría integral WCAG/lector de pantalla.
- Sin validación de esta suite en Firefox, Safari o dispositivos móviles físicos.
- Docker ejecutó Linux sobre Windows; no demuestra ejecución nativa en todos los hosts.
- No se probó reinicio completo del sistema ni restauración de perfiles dañados.
- Las cuatro alertas altas de dependencias de desarrollo registradas en la sección 6
  siguen como pendiente; esta sección no modifica dependencias ni afirma una auditoría nueva.
- Optimización, CI/CD y versión `v1.0.0` corresponden a la sección 8.
