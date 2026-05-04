# ADT TEST — Automatización de Auditoría de Asistencia

Suite de automatización con Selenium que genera, descarga y valida reportes de asistencia laboral desde el portal [asistenciadt.baplicada.cl](https://asistenciadt.baplicada.cl) para 13 empresas clientes. Incluye además un sistema de monitoreo de disponibilidad del portal.

---

## ¿Qué hace?

### Auditoría de reportes (`test_reporte.py`)

Por cada empresa configurada, el sistema:

1. Inicia sesión en el portal
2. Selecciona la empresa por RUT
3. Genera y descarga 6 tipos de reporte (PDF y/o Excel)
4. Valida los datos del reporte de Jornada Diaria contra cálculos esperados
5. Captura evidencia en imagen PNG del PDF
6. Genera un reporte HTML con el resumen de resultados
7. Consolida todo en un PDF y lo envía por email

### Monitoreo de disponibilidad (`test_disponibilidad.py`)

Por cada empresa configurada, el sistema:

1. Inicia sesión en el portal
2. Selecciona la empresa y accede a la página de fiscalización
3. Verifica que el nombre de la empresa aparece correctamente en el panel
4. Registra el resultado (OK / FAIL) con captura de pantalla
5. Genera un informe PDF con el resumen
6. Envía una alerta por email **solo si hay empresas con FAIL**

---

## Reportes generados por empresa (auditoría)

| Clave | Descripción |
|-------|-------------|
| `asistencia` | Reporte de asistencia general |
| `jor_diaria` | Jornada diaria (incluye auditoría de horas) |
| `domingos` | Trabajo en domingos y festivos |
| `modificaciones` | Modificaciones de turno |
| `diario` | Reporte diario |
| `incidentes` | Incidentes técnicos |

## Estados en los reportes

| Badge | Descripción |
|-------|-------------|
| `OK` | Reporte generado y auditado correctamente |
| `SIN DATOS` | No hay trabajadores registrados (cuenta como WARNING, no FAIL) |
| `AUDITORIA` | Inconsistencias detectadas en horas o balances |
| `BDATOS` | Error de conexión con la base de datos del portal |
| `SERVIDOR` | El servidor no respondió o la sesión expiró |
| `TIEMPO` | Timeout — el reporte no cargó dentro del tiempo máximo |
| `R. VACÍO` | Reporte Diario generado pero sin datos para el período |
| `CREDENCIAL` | Usuario o contraseña inválida detectada via toast del portal |

---

## Requisitos

### Sistema

- Python 3.13
- Google Chrome (versión estable)
- [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) — para convertir HTML a PDF
- [Poppler](https://github.com/oschwartz10612/poppler-windows/releases/) — para convertir PDF a imagen (Windows: agregar `bin/` al PATH)

### Python

```bash
pip install -r requirements.txt
```

## Variables de entorno

Crea un archivo `.env` en la raíz del proyecto (nunca lo subas al repositorio):

```env
EMAIL_USER=tu_correo@gmail.com
EMAIL_PASS=tu_app_password_de_gmail
```

> El password debe ser una [App Password de Google](https://myaccount.google.com/apppasswords), no tu contraseña normal.

Las credenciales del portal se configuran en [data/credenciales.py](data/credenciales.py).

---

## Estructura del proyecto

```
ADT_TEST/
├── conftest.py                     # Fixtures de Selenium: driver y driver_factory
├── requirements.txt
├── data/
│   ├── credenciales.py             # Usuario y contraseña del portal
│   └── empresas.py                 # 13 empresas con RUT y configuración
├── pages/
│   ├── base_page.py                # Clase base con waits y utilidades
│   ├── login_page.py               # Login + detección de toasts de error
│   ├── init_page.py                # Selección de empresa y acceso a fiscalización
│   └── fisc_page.py                # Generación y descarga de reportes
├── tests/
│   ├── test_login.py               # Validación del login
│   ├── test_reporte.py             # Flujo principal: 13 empresas × 6 reportes
│   └── test_disponibilidad.py      # Monitoreo de disponibilidad del portal
├── utils/
│   ├── auditoria.py                # Valida el Excel de Jornada Diaria
│   ├── enviar_correo.py            # Email con ZIP de auditoría (Gmail SMTP)
│   ├── enviar_correo_disponibilidad.py  # Email de alerta de disponibilidad
│   ├── helpers.py                  # Limpieza de descargas
│   ├── pdf_converter.py            # Convierte PDF a PNG
│   ├── pdf_merger.py               # Fusiona HTMLs en PDF consolidado
│   ├── report_html.py              # Reporte HTML de auditoría por empresa
│   ├── report_disponibilidad.py    # Reporte HTML/PDF de disponibilidad
│   ├── screenshots.py              # Captura de pantalla con timestamp
│   └── zipper.py                   # Empaqueta artefactos en ZIP
├── .github/workflows/
│   ├── test.yml                    # CI auditoría (push a master + manual)
│   └── disponibilidad.yml          # CI disponibilidad (workflow_dispatch vía cron-job.org)
├── downloads/                      # Archivos descargados (generado)
├── reports/                        # Reportes HTML y PDF (generado)
└── screenshots/                    # Capturas de evidencia (generado)
```

---

## Cómo ejecutar

### Auditoría de reportes

```bash
pytest tests/test_reporte.py -s
```

### Monitoreo de disponibilidad

```bash
pytest tests/test_disponibilidad.py -s
```

### Una empresa específica

```bash
pytest tests/test_reporte.py -s -k "ENAP"
```

### Post-procesamiento manual

Después de correr pytest, para generar el PDF consolidado y enviar el email:

**PowerShell:**
```powershell
python utils/pdf_merger.py        # genera reports/Reporte_Consolidado_Auditoria.pdf
python utils/zipper.py            # genera Paquete_Final_YYYY-MM-DD.zip
python utils/enviar_correo.py     # envía el ZIP por email
```

> Los scripts de correo leen las credenciales del `.env` automáticamente.

---

## CI/CD (GitHub Actions)

### Auditoría (`test.yml`)
Se activa en push a `master` y manualmente (workflow_dispatch). Ejecuta `test_reporte.py`, genera el PDF consolidado y sube los artefactos.

### Disponibilidad (`disponibilidad.yml`)
Se activa únicamente vía `workflow_dispatch`, programado externamente desde [cron-job.org](https://cron-job.org). Ejecuta `test_disponibilidad.py`, genera el informe PDF y envía alerta por email solo si hay empresas con FAIL.

**Secrets requeridos en GitHub → Settings → Secrets and variables → Actions:**

| Secret | Descripción |
|--------|-------------|
| `EMAIL_USER` | Dirección Gmail del remitente |
| `EMAIL_PASS` | App Password de Google (16 caracteres) |
| `PORTAL_USER` | Usuario del portal asistenciadt |
| `PORTAL_PASS` | Contraseña del portal asistenciadt |

---

## Empresas configuradas

| Empresa | RUT |
|---------|-----|
| ALTERNATTIVA | 79777010-8 |
| Biometria Aplicada Spa | 76257834-4 |
| CYGNUS | 77128770-0 |
| Empresa Nacional del Petroleo | 92604000-6 |
| ENAP REFINERIAS S.A | 87756500-9 |
| Enap Sipetrol S.A | 96579730-0 |
| NUEVA BIOMETRIA SPA | 77091268-7 |
| Sigdo Koppers (IC) | 91915000-9 |
| SIGDO KOPPERS S.A. | 99598300-1 |
| SIO RRHH | 78167971-2 |
| SK CAPACITACION | 76788120-7 |
| SK INDUSTRIAL | 76662490-1 |
| SKCOMSA | 96717980-9 |

**Total: 13 empresas × 6 reportes = 78 escenarios automatizados**
