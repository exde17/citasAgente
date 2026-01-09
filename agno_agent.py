import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.anthropic import Claude
from agno.os import AgentOS
from google_sheets_tool import GoogleSheetsTool
from typing import List

# Load environment variables
load_dotenv()

# Initialize Google Sheets Tool
sheets_tool = GoogleSheetsTool(
    credentials_file="credentials.json",
    spreadsheet_id=os.getenv("GOOGLE_SPREADSHEET_ID")
)

# Define tools as functions that the agent can call

def leer_todas_las_citas() -> str:
    """Lee todas las citas de la hoja de Google Sheets"""
    try:
        datos = sheets_tool.read_sheet()
        if not datos:
            return "No hay citas registradas"
        
        encabezados = datos[0] if datos else []
        citas = datos[1:] if len(datos) > 1 else []
        
        resultado = f"📊 Total de citas: {len(citas)}\n\n"
        for i, cita in enumerate(citas, 1):
            resultado += f"Cita {i}:\n"
            for j, valor in enumerate(cita):
                if j < len(encabezados):
                    resultado += f"  {encabezados[j]}: {valor}\n"
            resultado += "\n"
        return resultado
    except Exception as e:
        return f"Error al leer citas: {str(e)}"

def listar_especialidades() -> str:
    """Lista todas las especialidades disponibles"""
    try:
        especialidades = sheets_tool.get_especialidades_disponibles()
        if not especialidades:
            return "No hay especialidades disponibles"
        
        resultado = "📋 Especialidades disponibles:\n\n"
        for i, esp in enumerate(especialidades, 1):
            resultado += f"{i}. {esp}\n"
        return resultado
    except Exception as e:
        return f"Error al obtener especialidades: {str(e)}"

def listar_citas_disponibles(especialidad: str = None) -> str:
    """Lista todas las citas disponibles, opcionalmente por especialidad"""
    try:
        citas = sheets_tool.get_citas_disponibles(especialidad)
        if not citas:
            if especialidad:
                return f"No hay citas disponibles para {especialidad}"
            return "No hay citas disponibles en este momento"
        
        resultado = f"✅ Citas disponibles"
        if especialidad:
            resultado += f" en {especialidad}"
        resultado += f": ({len(citas)})\n\n"
        
        for i, cita in enumerate(citas, 1):
            resultado += f"{i}. {cita['medico']} ({cita['especialidad']})\n"
            resultado += f"   📅 Fecha: {cita['fecha']}\n"
            resultado += f"   🕐 Hora: {cita['hora']}\n"
            resultado += f"   Estado: {cita['estado']}\n\n"
        return resultado
    except Exception as e:
        return f"Error al obtener citas disponibles: {str(e)}"

def agendar_cita(especialidad: str, paciente: str, telefono: str, email: str, 
                 fecha: str = None, hora: str = None) -> str:
    """Agenda una cita para un paciente en una especialidad disponible"""
    try:
        citas_disponibles = sheets_tool.get_citas_disponibles(especialidad)
        
        if not citas_disponibles:
            return f"❌ No hay citas disponibles para {especialidad}"
        
        # Si se especifica fecha y hora, buscar esa cita específica
        if fecha and hora:
            cita_seleccionada = None
            for cita in citas_disponibles:
                if cita['fecha'] == fecha and cita['hora'] == hora:
                    cita_seleccionada = cita
                    break
            
            if not cita_seleccionada:
                return f"❌ La cita del {fecha} a las {hora} no está disponible"
        else:
            # Si no se especifica, usar la primera disponible
            cita_seleccionada = citas_disponibles[0]
        
        # Agregar a Hoja 1 y marcar como no disponible en Hoja 2
        sheets_tool.agregar_cita_agendada(
            paciente=paciente,
            medico=cita_seleccionada['medico'],
            especialidad=cita_seleccionada['especialidad'],
            fecha=cita_seleccionada['fecha'],
            hora=cita_seleccionada['hora'],
            telefono=telefono,
            email=email,
            fila_disponibilidad=cita_seleccionada['fila']
        )
        
        return f"""✅ ¡Cita agendada exitosamente!

👤 Paciente: {paciente}
👨‍⚕️ Médico: {cita_seleccionada['medico']}
🏥 Especialidad: {cita_seleccionada['especialidad']}
📅 Fecha: {cita_seleccionada['fecha']}
🕐 Hora: {cita_seleccionada['hora']}
📱 Teléfono: {telefono}
📧 Email: {email}

Se ha registrado en el sistema. ¡Gracias!"""
    except Exception as e:
        return f"❌ Error al agendar cita: {str(e)}"

def buscar_citas_paciente(nombre_paciente: str) -> str:
    """Busca todas las citas de un paciente específico"""
    try:
        datos = sheets_tool.read_sheet()
        if not datos or len(datos) < 2:
            return "No hay citas registradas"
        
        encabezados = datos[0]
        citas_encontradas = [cita for cita in datos[1:] if len(cita) > 2 and nombre_paciente.lower() in cita[2].lower()]
        
        if not citas_encontradas:
            return f"No se encontraron citas para {nombre_paciente}"
        
        resultado = f"🔍 Citas de {nombre_paciente}:\n\n"
        for cita in citas_encontradas:
            for j, valor in enumerate(cita):
                if j < len(encabezados):
                    resultado += f"  {encabezados[j]}: {valor}\n"
            resultado += "\n"
        return resultado
    except Exception as e:
        return f"Error al buscar citas: {str(e)}"

# Create the Medical Appointments Agent
agno_agent = Agent(
    name="Asistente de Citas Médicas",
    model=Claude(id="claude-haiku-4-5", api_key=os.getenv("ANTHROPIC_API_KEY")),
    # Add a database to the Agent
    db=SqliteDb(db_file="citas_medicas.db"),
    # System instructions for the agent
    instructions=[
        "Eres un asistente especializado en gestionar citas médicas.",
        "Tienes acceso directo a Google Sheets para leer citas disponibles.",
        "Cuando un paciente quiera agendar, primero pregunta qué especialidad necesita.",
        "Luego muestra las citas disponibles para esa especialidad.",
        "Finalmente, agenda la cita con los datos del paciente.",
        "Las columnas en la hoja son: Médico, Especialidad, Hora, Fecha, Estado",
        "Solo puedes agendar citas que tengan Estado='disponible'",
        "Siempre solicita: nombre, teléfono y email del paciente.",
        "Sé amable, profesional y ayuda con claridad.",
    ],
    # Add tools
    tools=[
        listar_especialidades, 
        listar_citas_disponibles, 
        agendar_cita,
        buscar_citas_paciente,
        leer_todas_las_citas
    ],
    # Add the previous session history to the context
    add_history_to_context=True,
    markdown=True,
)


# Create the AgentOS
agent_os = AgentOS(agents=[agno_agent])
# Get the FastAPI app for the AgentOS
app = agent_os.get_app()