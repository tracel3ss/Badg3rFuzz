```markdown
# 🦡 Badg3rFuzz

```

╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║        ██████╗  █████╗ ██████╗  ██████╗ ██████╗ ██████╗                      ║
║        ██╔══██╗██╔══██╗██╔══██╗██╔════╝ ╚════██╗██╔══██╗                     ║
║        ██████╔╝███████║██║  ██║██║  ███╗ █████╔╝██████╔╝                     ║
║        ██╔══██╗██╔══██║██║  ██║██║   ██║ ╚═══██╗██╔══██╗                     ║
║        ██████╔╝██║  ██║██████╔╝╚██████╔╝██████╔╝██║  ██║                     ║
║        ╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝                     ║
║                                                                              ║
║   ░▒▓███████▓▒░ ░▒▓██████▓▒░ ░▒▓███████▓▒░ ░▒▓██████▓▒░ ░▒▓██████▓▒░         ║
║                                                                              ║
║                  🦡 Badg3rFuzz - Fuzzing & brute force with reCAPTCHAv3 🦡  ║
╚══════════════════════════════════════════════════════════════════════════════╝

````

**Badg3rFuzz** es una herramienta para realizar fuzzing y ataques de fuerza bruta en formularios protegidos con reCAPTCHA v3, combinando Selenium para la obtención automática del token y múltiples hilos para maximizar la velocidad.

---

## 🔥 Características principales

- Compatible con reCAPTCHA v3 (`site-key` + `action`)
- Soporte para fuerza bruta de usuarios y contraseñas
- Generación automática de fuzzers para usuarios
- Multihilo configurable para paralelizar ataques
- Detención automática al encontrar credenciales válidas (`--stop-on-success`)
- Registro detallado en archivo `.log`
- Soporte para cabecera `Origin` personalizada para requests
- Manejo limpio de `Ctrl+C` para detener la ejecución

---

## 💻 Requisitos y compatibilidad

- Python 3.7+
- Google Chrome instalado en el sistema:
  - En Windows: Instalar Chrome desde [https://google.com/chrome](https://google.com/chrome)
  - En Linux (Debian/Ubuntu): `sudo apt install google-chrome-stable` o usar Chrome/Chromium oficial
- Paquetes Python:
  ```bash
  pip install -r requirements.txt
````

* Entornos Unix/Windows funcionan igual, pero en Windows se recomienda ejecutar en CMD/Powershell con permisos adecuados y evitar rutas con espacios en los nombres.
* El script utiliza Selenium con `webdriver-manager` para manejar automáticamente la versión compatible de `chromedriver`.

---

## 🚀 Uso básico

```bash
python badg3rscan.py \
  --site-key 6LemxMwUAAAAABCD1234XYZ \
  --captcha-action login \
  --login-url https://targetsite.com/login \
  --post-url https://targetsite.com/api/login \
  --pass-file passwords.txt \
  --user-file users.txt \
  --threads 10 \
  --stop-on-success
```

---

## ⚙️ Uso con fuzzer para usuarios y cabecera Origin

```bash
python badg3rscan.py \
  --site-key 6LemxMwUAAAAABCD1234XYZ \
  --captcha-action submit_form \
  --login-url https://secure.example.com/auth \
  --post-url https://secure.example.com/api/auth \
  --pass-file rockyou.txt \
  --user-fuzz digits:6:8:500 \
  --threads 8 \
  --origin-url https://secure.example.com \
  --stop-on-success
```

* `--user-fuzz digits:6:8:500` genera 500 usuarios numéricos de longitud entre 6 y 8 caracteres.
* `--origin-url` fija las cabeceras HTTP `Origin` y `Referer` (útil para evitar bloqueos CORS o validaciones estrictas).

---

## 📋 Parámetros

| Parámetro           | Descripción                                                                                     | Obligatorio    |
| ------------------- | ----------------------------------------------------------------------------------------------- | -------------- |
| `--site-key`        | Clave pública del reCAPTCHA que se usa para obtener tokens                                      | Sí             |
| `--captcha-action`  | Acción (action) que se asocia al reCAPTCHA (ej: `login`, `submit_form`)                         | Sí             |
| `--login-url`       | URL donde se carga el formulario y el widget de reCAPTCHA                                       | Sí             |
| `--post-url`        | URL que recibe la solicitud POST con las credenciales                                           | Sí             |
| `--pass-file`       | Archivo con las contraseñas (una por línea)                                                     | No\*           |
| `--user-file`       | Archivo con los nombres de usuario (uno por línea)                                              | No\*           |
| `--user-fuzz`       | Fuzzer para generar usuarios automáticamente, formato `tipo:min_len:max_len:cantidad`           | No\*           |
| `--threads`         | Número de hilos paralelos para enviar peticiones                                                | No (default 5) |
| `--stop-on-success` | Detiene el proceso cuando se encuentra una credencial válida                                    | No             |
| `--origin-url`      | URL para la cabecera HTTP `Origin` y `Referer` (útil para sitios que verifican estas cabeceras) | No             |
| `--no-banner`       | Desactiva la impresión del banner en ASCII                                                      | No             |

\* Si no se especifica `--user-file` y `--user-fuzz`, se generan usuarios numéricos por defecto. Si no se especifica `--pass-file`, se genera un fuzzer fuerte para passwords.

---

## 📈 To-Do / Mejoras futuras

* [ ] Integración con proxies para anonimizar peticiones
* [ ] Soporte para reCAPTCHA v2 / desafíos visibles
* [ ] Implementar pausa y reanudación más robusta con checkpointing
* [ ] Incorporar soporte para múltiples tipos de autenticación/formularios
* [ ] Mejorar detección automática de éxito/error con análisis dinámico de respuestas
* [ ] Añadir reportes más detallados en formato JSON o CSV
* [ ] Mejorar la interfaz con menú interactivo o GUI web básica

---

## ☕ ¿Quieres invitarme un café?

Si te gusta Badg3rFuzz y quieres apoyarme para seguir mejorando herramientas y aprendiendo, puedes invitarme un café.


```markdown

Si quieres apoyar mi trabajo, puedes hacerlo aquí:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/X8X61IO019)
```

Solo cambia el enlace a tu perfil personal.

Para pagos en criptomonedas, PayPal o Patreon, puedes añadir secciones similares con tus links.

---

## 🔧 Instalación rápida

```bash
git clone https://github.com/tuusuario/badg3rfuzz.git
cd badg3rfuzz
pip install -r requirements.txt
```

---

## 📞 Contacto

Si tienes dudas o sugerencias, abre un issue en GitHub.

---

¡Gracias por usar Badg3rFuzz! 🦡💥
```