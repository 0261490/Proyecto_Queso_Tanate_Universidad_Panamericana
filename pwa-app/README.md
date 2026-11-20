# PWA de Proyecto Tenate

Interfaz accesible y offline para estimar localmente la intención de compra del
Queso Tenate. No requiere servidor de aplicación: el modelo, el traductor y el
motor se empaquetan para ejecutarse en el navegador.

## Desarrollo con Docker

Desde la raíz del repositorio:

```text
docker compose run --rm -p 5173:5173 node npm --prefix pwa-app run dev -- --port 5173
```

Abra `http://localhost:5173`. Para detener el servidor use `Ctrl+C`.

## Pruebas y compilación

```text
docker compose run --rm node npm --prefix pwa-app test
docker compose run --rm node npm --prefix pwa-app run build
```

La compilación queda en `pwa-app/dist/`. El generador ejecutado después de Vite
incluye todos los archivos producidos en el precache y crea un nombre de caché
basado en su contenido.

El manifiesto incluye iconos PNG de 192×192 y 512×512 píxeles para cumplir los
requisitos de instalación de navegadores Chromium, además del SVG escalable.

Para comprobar el resultado instalable:

```text
docker compose run --rm -p 4173:4173 node npm --prefix pwa-app run preview -- --port 4173
```

Abra `http://localhost:4173`, visite la aplicación una vez y active el modo sin
conexión de las herramientas del navegador. La recarga y la evaluación deben
seguir funcionando.

## Instalación

La instalación requiere servir la compilación mediante HTTPS o desde
`localhost`. En navegadores compatibles:

1. abra la aplicación;
2. espere a que aparezca **Instalar aplicación**;
3. active el botón y confirme la instalación del navegador.

También se puede usar la opción de instalación del menú del navegador. En iOS,
use **Compartir → Añadir a pantalla de inicio**.

## Privacidad y alcance

Las respuestas y la inferencia permanecen en el dispositivo. Desde la Sección 6,
cada evaluación completada se guarda automáticamente en IndexedDB junto con
sus respuestas, evidencia, resultado, fecha y versión del modelo. El historial
permite consultar las respuestas y eliminar una evaluación o todos los registros,
con confirmación. El resultado es una orientación probabilística, no una garantía comercial.

El historial pertenece al navegador y origen utilizados: cambiar de dispositivo,
perfil, dominio o puerto muestra otro almacenamiento. No se sincroniza ni se
respalda en un servidor. Borrar los datos del sitio, la navegación privada o la
limpieza automática del navegador pueden eliminarlo. En dispositivos compartidos,
otras personas con acceso al mismo perfil pueden consultarlo.

Si falla el guardado, el resultado sigue disponible y se muestra un aviso.
Reiniciar el formulario no borra el historial. No se guardan borradores incompletos.
El esquema y las decisiones técnicas se describen en `../docs/seccion-6-persistencia.md`.

## Pruebas del historial en navegador

```powershell
npm.cmd --prefix pwa-app ci
npm.cmd --prefix pwa-app run build
npm.cmd --prefix pwa-app run test:e2e
```

Playwright usa Edge instalado en Windows, sin ventana visible, y un servidor de
pruebas aislado en el puerto 4176. En Linux/macOS se usa Chromium de Playwright;
instale primero su navegador con `npx playwright install chromium` desde `pwa-app`.
Las pruebas usan un perfil temporal sin tocar el historial del usuario. Cubren
recarga, reapertura de página, operaciones offline, errores de almacenamiento y 320 px.

## Demostración local sin Docker

Con Node.js 24 o posterior y las dependencias instaladas:

```powershell
npm.cmd --prefix pwa-app run dev -- --port 5173
```

Para comprobar instalación y offline, use primero build y después preview.
El service worker solo se registra en la compilación de producción. Si usó
una versión anterior en el puerto de desarrollo, elimine su service worker y
los datos de ese sitio desde las herramientas del navegador antes de probar.

## Cuestionario

Se conservan las siete preguntas originales: tradición mexicana, recomendación,
patrimonio gastronómico, autenticidad, potencial comercial, preservación cultural
y características sensoriales. Se envían las siete respuestas al traductor y al
motor; intención de compra se reserva como resultado.

Con este formulario completo, la recomendación determina el resultado: Sí da
81.4 % y No da 9.8 %. Las otras respuestas no cambian ese porcentaje en el DAG
congelado cuando recomendación ya está observada. Esta limitación se documenta;
no se altera la evidencia ni el modelo para producir porcentajes diferentes.
Tras cambiar respuestas, el resultado anterior se oculta; pulse de nuevo el botón
de análisis para actualizarlo. El modelo reconstruido no equivale exactamente al publicado ni
demuestra el efecto causal de mejorar un atributo del producto.

## Comprobación final guiada en Chrome o Edge

El usuario confirmó la comprobación final el 17 de noviembre de 2026 y autorizó
el cierre documental. La guía se conserva para reproducir la validación.
El ensayo previo del navegador integrado del 5 de noviembre recuperó HTML,
pero no estilos ni cuestionario; se conserva como antecedente, no como prueba aprobada.

Para iniciar la versión de producción desde la raíz del repositorio:

```powershell
npm.cmd --prefix pwa-app run build
npm.cmd --prefix pwa-app run preview -- --host 127.0.0.1 --port 4174 --strictPort
```

1. Abra `http://127.0.0.1:4174` en **Chrome o Edge**. Use siempre esta misma
   dirección y puerto: `localhost` y `127.0.0.1` tienen almacenamientos distintos.
2. Espere el aviso **Lista para usar sin conexión en este navegador**. Compruebe
   siete preguntas, seleccione todas **Sí** y pulse **Ver orientación comercial**:
   debe aparecer **81.4 %**. Cambie recomendación a **No**: el resultado anterior
   se oculta; al analizar nuevamente debe aparecer **9.8 %**.
3. Pulse **Instalar aplicación** o la opción de instalación del navegador.
   Confirme la instalación y verifique que Tenate abre en su propia ventana.
   Si no aparece la opción, anote navegador/versión y el mensaje visible; no
   dé por aprobada la instalación sólo por existir un manifiesto.
4. En la pestaña del navegador, abra **F12 → Application/Aplicación → Service
   Workers**, compruebe que `sw.js` está activado y marque **Offline**. Esta
   opción simula pérdida de red sólo para la prueba. No active «Bypass for network».
5. Recargue normalmente con **Ctrl+R**. Deben mantenerse estilos y las siete
   preguntas. El formulario puede reiniciarse; las evaluaciones completadas
   deben seguir disponibles en **Su historial** desde la sección 6.
6. Sin quitar **Offline**, haga dos evaluaciones: todas **No → 9.8 %** y todas
   **Sí → 81.4 %**. Compruebe que **Realizar otra evaluación** limpia el formulario.
7. Desmarque **Offline** al terminar. Informe navegador/versión y si instalación,
   recarga con estilos y ambos cálculos funcionaron. Si algo falla, copie el
   mensaje o describa el paso exacto; aún no se debe cerrar la sección.

Registro de aceptación — 17 de noviembre de 2026:

| Dato | Resultado |
| --- | --- |
| Navegador y versión | No reportados por el usuario |
| Instalación y apertura en ventana propia | Aceptadas por confirmación del usuario |
| Recarga offline con estilos y siete preguntas | Aceptada por confirmación del usuario |
| Offline: 9.8 % / 81.4 % y reinicio | Aceptados por confirmación del usuario |

La aceptación se basa en la confirmación del usuario en el chat; no se realizó
una nueva comprobación automatizada de navegador durante el cierre documental.
La sección 5 queda completada. La persistencia local corresponde a la sección 6.
