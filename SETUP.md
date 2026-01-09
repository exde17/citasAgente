# Agente de Citas Médicas

Sistema de gestión de citas médicas usando Agno y Google Sheets.

## Configuración

### 1. Instalar dependencias

```bash
pip install agno anthropic google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv
```

### 2. Configurar Google Sheets API

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la API de Google Sheets
4. Crea credenciales (OAuth 2.0 o Service Account)
5. Descarga el archivo `credentials.json` y colócalo en la raíz del proyecto

### 3. Configurar variables de entorno

Copia `.env.example` a `.env`:

```bash
cp .env.example .env
```

Edita `.env` con tus valores:

```
ANTHROPIC_API_KEY=sk-ant-api03-...
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_SPREADSHEET_ID=1abc...xyz
```

### 4. Estructura de la hoja de cálculo

Tu hoja de Google Sheets debe tener estas columnas:

| Fecha | Hora | Paciente | Médico | Especialidad | Estado | Teléfono | Email |
|-------|------|----------|--------|--------------|--------|----------|-------|
| 2026-01-10 | 09:00 | Juan Pérez | Dr. García | Cardiología | Confirmada | 555-1234 | juan@email.com |

## Uso

### Iniciar el servidor

```bash
source .venv/Scripts/activate
export ANTHROPIC_API_KEY="tu-key"
export GOOGLE_SPREADSHEET_ID="tu-spreadsheet-id"
fastapi dev agno_agent.py
```

### Funcionalidades del agente

- ✅ Consultar citas disponibles
- ✅ Agendar nuevas citas
- ✅ Modificar citas existentes
- ✅ Cancelar citas
- ✅ Buscar citas por paciente
- ✅ Verificar disponibilidad de médicos

### Ejemplos de uso

**Agendar una cita:**
```
Usuario: "Necesito agendar una cita con el Dr. García para el 15 de enero"
Agente: "¿A qué hora prefiere? Tengo disponibilidad a las 9:00, 11:00 y 15:00"
```

**Consultar citas:**
```
Usuario: "¿Qué citas tengo esta semana?"
Agente: "Tienes 2 citas programadas: 
- Martes 10 a las 9:00 con Dr. García (Cardiología)
- Jueves 12 a las 14:00 con Dra. López (Medicina General)"
```

## Estructura del proyecto

```
pruebaAgno/
├── agno_agent.py          # Agente principal
├── .env                    # Variables de entorno (no subir a git)
├── .env.example            # Ejemplo de configuración
├── credentials.json        # Credenciales de Google (no subir a git)
├── citas_medicas.db        # Base de datos SQLite
└── SETUP.md               # Este archivo
```

## Notas

- Asegúrate de agregar `.env` y `credentials.json` a tu `.gitignore`
- El agente mantiene un historial de conversaciones en `citas_medicas.db`
- Todas las operaciones se sincronizan con Google Sheets en tiempo real
