# Agente de Citas Médicas

Sistema inteligente de gestión de citas médicas usando Agno y Google Sheets. El agente consulta disponibilidades de médicos y permite a pacientes agendar citas de forma automática.

## Características

- ✅ Consultar citas disponibles por especialidad
- ✅ Listar todas las especialidades disponibles
- ✅ Agendar nuevas citas automáticamente
- ✅ Sincronización en tiempo real con Google Sheets
- ✅ Actualización automática de disponibilidades (marca como "no disponible")
- ✅ Búsqueda flexible (ej: "Pediatría" coincide con "Pediatra")
- ✅ Historial de conversaciones en base de datos local

## Configuración

### 1. Instalar dependencias

```bash
pip install agno anthropic google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv
```

### 2. Configurar Google Sheets API

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto
3. Habilita la API de Google Sheets
4. Crea una **Cuenta de Servicio** (Service Account)
5. Crea una clave JSON y descárgala
6. Renómbrala a `credentials.json` y colócala en la raíz del proyecto

### 3. Crear tu hoja de Google Sheets

Crea una hoja de cálculo con **DOS hojas**:

#### **Hoja 1: "Hoja 1" - Citas Agendadas**
Columnas: `Fecha | Hora | Paciente | Médico | Especialidad | Estado | Teléfono | Email`

Aquí se registran todas las citas agendadas por pacientes.

#### **Hoja 2: "Hoja 2" - Disponibilidades**
Columnas: `Médico | Especialidad | Hora | Fecha | Estado`

Ejemplo:
```
Médico           | Especialidad      | Hora  | Fecha      | Estado
German Gomez     | Pediatra          | 8:00  | 2026-01-20 | disponible
German Gomez     | Pediatra          | 8:30  | 2026-01-20 | disponible
Jimena Mesa      | Medico General    | 6:00  | 2026-01-14 | disponible
Dr. García       | Cardiología       | 13:00 | 2026-01-15 | disponible
```

### 4. Configurar variables de entorno

Copia `.env.example` a `.env`:

```bash
cp .env.example .env
```

Edita `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
GOOGLE_SPREADSHEET_ID=tu-id-de-sheets
```

Obtén el ID de tu sheet de la URL:
```
https://docs.google.com/spreadsheets/d/[ESTE_ES_EL_ID]/edit
```

### 5. Compartir la hoja con el agente

- Abre tu Google Sheet
- Clic en **Compartir**
- Pega el email de la Service Account (que aparece en `credentials.json`)
- Dale permisos de **Editor**

## Uso

### Iniciar el servidor

```bash
source .venv/Scripts/activate
fastapi dev agno_agent.py
```

El servidor estará disponible en: `http://127.0.0.1:8000`

### Funcionalidades del agente

**El agente puede:**

1. **Listar especialidades disponibles**
   - Usuario: "¿Qué especialidades tienes?"
   - Agente: Muestra lista de especialidades

2. **Ver citas disponibles por especialidad**
   - Usuario: "Muéstrame citas de Pediatría"
   - Agente: Lista todas las citas disponibles para esa especialidad

3. **Agendar una cita**
   - Usuario: "Quiero agendar una cita de Pediatría"
   - Agente: Pide nombre, teléfono y email
   - Agente: Agenda automáticamente y actualiza estados

4. **Ver todas las citas disponibles**
   - Usuario: "Muéstrame todas las citas disponibles"
   - Agente: Lista completa de citas por especialidad

### Ejemplos de conversación

**Ejemplo 1: Agendar una cita**
```
Usuario: Quiero una cita con un pediatra
Agente: ¡Perfecto! Tengo disponibilidad con German Gomez en Pediatría
        ¿Cuál es tu nombre, teléfono y email?
Usuario: Carlos Rodríguez, 555-1234, carlos@email.com
Agente: ✅ Cita agendada para Carlos Rodríguez
        Médico: German Gomez
        Especialidad: Pediatría
        Fecha: 20 de enero de 2026
        Hora: 8:00
```

**Ejemplo 2: Buscar por especialidad específica**
```
Usuario: ¿Tienes citas de Cardiología?
Agente: Sí, el Dr. García tiene 5 citas disponibles:
        13:00 - 15 de enero
        14:00 - 16 de enero
        15:00 - 17 de enero
        16:00 - 18 de enero
        17:00 - 19 de enero
```

## Cómo funciona

1. **El agente lee Hoja 2** para ver qué citas están disponibles
2. **Filtra por estado "disponible"** - solo muestra esas
3. **Cuando alguien agenda:**
   - Agrega el registro a **Hoja 1** con los datos del paciente
   - Cambia el estado a **"no disponible"** en **Hoja 2**
4. **Búsqueda flexible:** "Pediatría" = "Pediatra", "Medicina General" = "Medico General"

## Estructura del proyecto

```
pruebaAgno/
├── agno_agent.py              # Agente principal con funciones
├── google_sheets_tool.py       # Herramienta para interactuar con Google Sheets
├── .env                        # Variables de entorno (NO SUBIR)
├── .env.example                # Plantilla de .env
├── credentials.json            # Credenciales de Google (NO SUBIR)
├── citas_medicas.db           # Base de datos SQLite local
├── .gitignore                  # Archivos a ignorar
└── SETUP.md                    # Este archivo
```

## Solución de problemas

### "No hay citas disponibles" pero veo citas en la hoja

- Verifica que el **Estado** sea exactamente `disponible` (minúsculas, sin espacios)
- Comprueba que los datos en Hoja 2 estén completos

### El agente no actualiza después de agendar

- Verifica que Hoja 2 tenga una columna **Estado**
- Revisa que el email de la Service Account tenga permisos de **Editor**

### Error de autenticación con Google

- Asegúrate de que `credentials.json` esté en la raíz del proyecto
- Verifica que la Service Account esté compartida en tu Google Sheet

## Notas importantes

- ⚠️ Agrega `.env` y `credentials.json` a `.gitignore`
- 📊 El agente sincroniza AUTOMÁTICAMENTE con Google Sheets
- 💾 Mantiene historial local en `citas_medicas.db`
- 🔄 Las citas agendadas se marcan como "no disponible" inmediatamente
