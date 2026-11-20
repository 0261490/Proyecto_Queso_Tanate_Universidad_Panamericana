# Sección 6: persistencia e historial local

## Estado

**Completada al 20 de noviembre de 2026.** Implementación y validación local
realizadas el 17 de noviembre. El usuario autorizó la publicación del cierre con
commit, push y etiqueta `sprint-6` el 20 de noviembre.
El documento explicativo privado se conserva únicamente en Google Drive.

## Comportamiento

Cada envío válido del formulario calcula primero la inferencia y después guarda
una copia de la evaluación completa. La interfaz informa si se guardó o si hubo
un error; la inferencia sigue disponible aunque IndexedDB falle. Durante el
guardado se desactiva el envío para evitar solicitudes duplicadas simultáneas.
Cada evaluación posterior constituye un registro nuevo, aunque repita respuestas.

El historial se carga al abrir la PWA y tras guardar o eliminar una evaluación.
Se muestra de más reciente a más antiguo, con fecha local, probabilidad y siete
respuestas en lenguaje natural. El botón Actualizar historial permite volver a
leer cambios efectuados desde otra pestaña. El borrado individual y total requiere
confirmación; cancelar no modifica registros. Reiniciar el cuestionario conserva
el historial. No hay guardado de borradores incompletos ni recuperación automática
del formulario: las respuestas anteriores se consultan dentro del historial.

## Arquitectura y esquema

`pwa-app/src/storage/history.ts` encapsula IndexedDB; `history-ui.ts` presenta el
historial mediante nodos DOM y texto, y `main.ts` coordina inferencia y guardado.
No se modifica el motor, el traductor, el DAG ni las CPT.

| Elemento | Valor |
| --- | --- |
| Base de datos | `tenate-history` |
| Versión IndexedDB | `1` |
| Almacén | `assessments` |
| Clave primaria | `id`, UUID generado para cada evaluación |
| Índice | `createdAt` |
| Versión de registro | `schemaVersion: 1` |

| Campo | Contenido |
| --- | --- |
| `id` | Identificador único; `add` rechaza duplicados sin sobrescribir |
| `createdAt` | Fecha ISO UTC, presentada en la zona horaria del dispositivo |
| `model.version` | `model_version` del JSON científico |
| `model.sha256` | Huella del archivo científico, tomada de `model.sha256` |
| `answers` | Las siete respuestas booleanas del formulario |
| `evidence` | Evidencia exacta generada por el traductor |
| `result.variable` / `state` | `Q2_Purchase_Intention` / `Yes` |
| `result.probability` | Probabilidad original entre 0 y 1, sin redondeo visual |

Se valida la estructura de cada registro y la correspondencia entre respuestas
y evidencia antes de escribir y después de leer. El almacenamiento no recalcula
la inferencia; el resultado proviene del motor. La probabilidad mostrada se
formatea con la misma función que el resultado actual. Un modelo con otra huella
se identifica como distinto, conservando el resultado histórico sin recalcularlo.

Cada operación abre una conexión y la cierra al terminar. Las escrituras y
borrados solo se consideran exitosos al completarse su transacción, no al
resolver la petición individual. Una apertura bloqueada o que supera cinco
segundos produce un error controlado. Ante cambios de versión se cierra la
conexión para no bloquear una futura migración. La versión inicial crea el
almacén y su índice; cualquier cambio futuro del esquema debe incrementar la
versión y añadir una migración explícita que preserve los registros.

## Privacidad, offline y límites

- No se envían registros a una API ni se sincronizan entre dispositivos.
- IndexedDB pertenece al origen y perfil del navegador. `localhost`, `127.0.0.1`
  y puertos diferentes tienen historiales separados.
- El service worker mantiene los recursos de la PWA; IndexedDB mantiene los
  datos. Eliminar historial no borra las cachés ni otras bases de datos.
- Tras cargar y preparar la PWA, consulta, guardado y eliminación funcionan sin red.
- No se garantiza almacenamiento permanente: navegación privada, borrado de
  datos del sitio, presión de almacenamiento o pérdida del dispositivo pueden
  eliminar registros. No hay copia de respaldo ni cifrado propio de la aplicación.
- Un usuario con acceso al mismo perfil del navegador puede consultar el historial.
- Si falla el guardado por cuota o permisos, se conserva el resultado visible y
  se informa que no fue guardado. Una evaluación nueva permite reintentar.
- Si la lectura falla o detecta registros incompatibles, se avisa sin mostrarlos
  como válidos ni eliminarlos automáticamente. No hay herramienta de reparación.
- La lista carga todos los registros; paginación y exportación no forman parte
  de esta sección. La actualización entre pestañas es manual.

## Validación del 17 de noviembre de 2026

| Comprobación | Resultado |
| --- | --- |
| PWA, Node local y Docker | 17/17 pruebas aprobadas |
| Compilación Vite en Docker | Correcta, siete recursos precacheados |
| Motor TypeScript en Docker | 28/28 aprobadas |
| Python en Docker | 30/30 aprobadas; avisos de deprecación, sin fallos |
| Playwright con Edge 157.0.4341.60 en Windows | 4/4 aprobadas, sin ventana visible |
| Offline real del contexto de navegador | Recarga, guardado, lectura, borrado individual y total aprobados |
| Errores simulados en navegador | Cuota y acceso denegado mantienen inferencia y muestran fallo de guardado |
| Vista a 320 px | Sin desbordamiento; captura del historial inspeccionada |
| Modelo científico | SHA-256 sin cambios |

Las pruebas unitarias usan `fake-indexeddb` y cubren copias independientes,
orden, reapertura de conexiones, duplicados, validación, abortos y aislamiento
entre bases de datos. Las pruebas de navegador usan IndexedDB nativo y un perfil
temporal: comprueban recarga y reapertura de página, preservación de respuestas,
ambos resultados, cancelación de borrado, reinicio y eliminación persistente.
La simulación offline de Playwright corta la red del contexto. No se afirma una
prueba de reinicio completo del sistema ni de todos los navegadores.

Huella conservada:
`8ecb6ae7cd8236aa3e7930287bb8ae51f4828cbe97baf138d63bb75388800f3b`.

## Reproducción

Desde la raíz, con Docker iniciado:

```text
docker compose run --rm -v tenate-pwa-linux-deps:/workspace/pwa-app/node_modules node sh -c "npm --prefix pwa-app ci && npm --prefix pwa-app test && npm --prefix pwa-app run build"
docker compose run --rm node npm --prefix inference-engine test
docker compose run --rm python python -m unittest discover -s tests -p "test_*.py"
```

En Windows con Node 24 y Edge instalado:

```text
npm.cmd --prefix pwa-app ci
npm.cmd --prefix pwa-app run build
npm.cmd --prefix pwa-app run test:e2e
```

El servidor temporal usa `127.0.0.1:4176`; debe estar libre. Los resultados y
capturas se generan en `pwa-app/test-results/`, excluido de Git. En otros sistemas
se requiere instalar Chromium de Playwright. El volumen Docker aislado conserva
las dependencias nativas de Windows.

## Dependencias y pendiente de mantenimiento

El 20 de noviembre el usuario confirmó que el historial apareció después de
tres recargas. Se registra como mejora pendiente del flujo de actualización
de la PWA; la caché o el ciclo del service worker son una hipótesis, no una causa
diagnosticada. Esta publicación no incorpora una corrección de ese comportamiento.

Se añadieron únicamente dependencias de desarrollo: `fake-indexeddb` 6.2.8 y
`@playwright/test` 1.65.1, fijadas en el lockfile. La aplicación utiliza IndexedDB
nativo, sin biblioteca de persistencia en producción.

La auditoría npm del 17 de noviembre reportó cuatro alertas de severidad alta en
la cadena de desarrollo `picomatch` / `fdir` / `tinyglobby` / `vite`, asociadas a
`GHSA-fc5q-39xc-vjpf`. No se aplicó automáticamente la bajada de versión mayor de
Vite propuesta por npm. La revisión de esa cadena queda registrada como pendiente
de mantenimiento; no se presenta esta entrega como auditoría sin vulnerabilidades.
