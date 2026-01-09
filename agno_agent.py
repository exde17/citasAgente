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
        
        # Formato legible
        encabezados = datos[0] if datos else []
        citas = datos[1:] if len(datos) > 1 else []
        
        resultado = f"Total de citas: {len(citas)}\n\n"
        for i, cita in enumerate(citas, 1):
            resultado += f"Cita {i}:\n"
            for j, valor in enumerate(cita):
                if j < len(encabezados):
                    resultado += f"  {encabezados[j]}: {valor}\n"
            resultado += "\n"
        return resultado
    except Exception as e:
        return f"Error al leer citas: {str(e)}"

def agregar_cita(fecha: str, hora: str, paciente: str, medico: str, 
                 especialidad: str, estado: str, telefono: str, email: str) -> str:
    """Agrega una nueva cita a la hoja de Google Sheets"""
    try:
        valores = [fecha, hora, paciente, medico, especialidad, estado, telefono, email]
        sheets_tool.write_row(valores)
        return f"✅ Cita agendada exitosamente para {paciente} el {fecha} a las {hora}"
    except Exception as e:
        return f"Error al agregar cita: {str(e)}"

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
        
        resultado = f"Citas de {nombre_paciente}:\n\n"
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
        "Tienes acceso directo a Google Sheets para leer y escribir citas.",
        "Ayudas a los pacientes a agendar, consultar y modificar sus citas.",
        "Siempre verifica la disponibilidad antes de asignar una cita.",
        "La hoja tiene estas columnas: Fecha, Hora, Paciente, Médico, Especialidad, Estado, Teléfono, Email",
    ],
    # Add tools
    tools=[leer_todas_las_citas, agregar_cita, buscar_citas_paciente],
    # Add the previous session history to the context
    add_history_to_context=True,
    markdown=True,
)


# Create the AgentOS
agent_os = AgentOS(agents=[agno_agent])
# Get the FastAPI app for the AgentOS
app = agent_os.get_app()