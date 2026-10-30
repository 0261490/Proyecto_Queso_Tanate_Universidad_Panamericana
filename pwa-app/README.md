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

Las respuestas y la inferencia permanecen en el dispositivo. Esta sección no
guarda historial; la persistencia local corresponde a la Sección 6. El resultado
es una orientación probabilística, no una garantía comercial.

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
Tras cambiar respuestas, pulse de nuevo el botón de análisis para actualizar
el resultado. El modelo reconstruido no equivale exactamente al publicado ni
demuestra el efecto causal de mejorar un atributo del producto.
