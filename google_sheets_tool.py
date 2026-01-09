from typing import List, Dict, Any
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import json


class GoogleSheetsTool:
    """Tool para interactuar con Google Sheets"""
    
    def __init__(self, credentials_file: str, spreadsheet_id: str):
        self.spreadsheet_id = spreadsheet_id
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.creds = Credentials.from_service_account_file(
            credentials_file, scopes=self.scopes
        )
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.sheet = self.service.spreadsheets()
    
    def read_sheet(self, sheet_name: str = "Hoja 2", range_name: str = "A:H") -> List[List[str]]:
        """Lee datos de una hoja específica de cálculo"""
        full_range = f"'{sheet_name}'!{range_name}"
        result = self.sheet.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=full_range
        ).execute()
        return result.get('values', [])
    
    def write_row(self, values: List[str], sheet_name: str = "Hoja 1", range_name: str = "A:H") -> Dict[str, Any]:
        """Escribe una fila en una hoja específica"""
        full_range = f"'{sheet_name}'!{range_name}"
        body = {'values': [values]}
        result = self.sheet.values().append(
            spreadsheetId=self.spreadsheet_id,
            range=full_range,
            valueInputOption='RAW',
            body=body
        ).execute()
        return result
    
    def update_row(self, row_number: int, values: List[str], sheet_name: str = "Hoja 2", range_name: str = "A") -> Dict[str, Any]:
        """Actualiza una fila específica en una hoja"""
        full_range = f"'{sheet_name}'!{range_name}{row_number}:H{row_number}"
        body = {'values': [values]}
        result = self.sheet.values().update(
            spreadsheetId=self.spreadsheet_id,
            range=full_range,
            valueInputOption='RAW',
            body=body
        ).execute()
        return result
    
    def find_rows(self, column_index: int, search_value: str, sheet_name: str = "Hoja 2") -> List[int]:
        """Encuentra filas que contengan un valor específico en una columna"""
        values = self.read_sheet(sheet_name=sheet_name)
        matching_rows = []
        for i, row in enumerate(values):
            if len(row) > column_index and row[column_index] == search_value:
                matching_rows.append(i + 1)
        return matching_rows
    
    def get_especialidades_disponibles(self) -> List[str]:
        """Obtiene lista de especialidades únicas de Hoja 2"""
        datos = self.read_sheet(sheet_name="Hoja 2")
        especialidades = set()
        if len(datos) > 1:
            for fila in datos[1:]:
                if len(fila) > 1:  # Columna B = Especialidad
                    especialidades.add(fila[1])
        return sorted(list(especialidades))
    
    def get_citas_disponibles(self, especialidad: str = None) -> List[Dict[str, str]]:
        """Obtiene todas las citas disponibles de Hoja 2, opcionalmente filtradas por especialidad"""
        datos = self.read_sheet(sheet_name="Hoja 2")
        if len(datos) < 2:
            return []
        
        encabezados = datos[0]
        citas_disponibles = []
        
        for i, fila in enumerate(datos[1:], start=2):
            if len(fila) >= len(encabezados):
                try:
                    estado_idx = encabezados.index('Estado')
                    especialidad_idx = encabezados.index('Especialidad')
                    
                    estado = fila[estado_idx] if estado_idx < len(fila) else ""
                    espec = fila[especialidad_idx] if especialidad_idx < len(fila) else ""
                    
                    if estado.lower() == 'disponible':
                        if especialidad is None or espec.lower() == especialidad.lower():
                            cita = {
                                'fila': i,
                                'medico': fila[0] if len(fila) > 0 else "",
                                'especialidad': espec,
                                'hora': fila[2] if len(fila) > 2 else "",
                                'fecha': fila[3] if len(fila) > 3 else "",
                                'estado': estado
                            }
                            citas_disponibles.append(cita)
                except ValueError:
                    continue
        
        return citas_disponibles
    
    def agregar_cita_agendada(self, paciente: str, medico: str, especialidad: str, 
                             fecha: str, hora: str, telefono: str, email: str) -> bool:
        """Agrega una cita agendada a Hoja 1"""
        try:
            valores = [fecha, hora, paciente, medico, especialidad, "Confirmada", telefono, email]
            self.write_row(valores, sheet_name="Hoja 1", range_name="A:H")
            return True
        except Exception as e:
            print(f"Error al agregar cita agendada: {e}")
        return False
