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
    
    def read_sheet(self, range_name: str = "A:H") -> List[List[str]]:
        """Lee datos de la hoja de cálculo"""
        result = self.sheet.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range_name
        ).execute()
        return result.get('values', [])
    
    def write_row(self, values: List[str], range_name: str = "A:H") -> Dict[str, Any]:
        """Escribe una fila en la hoja de cálculo"""
        body = {'values': [values]}
        result = self.sheet.values().append(
            spreadsheetId=self.spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        return result
    
    def update_row(self, row_number: int, values: List[str], range_name: str = "A") -> Dict[str, Any]:
        """Actualiza una fila específica"""
        range_to_update = f"{range_name}{row_number}:H{row_number}"
        body = {'values': [values]}
        result = self.sheet.values().update(
            spreadsheetId=self.spreadsheet_id,
            range=range_to_update,
            valueInputOption='RAW',
            body=body
        ).execute()
        return result
    
    def find_rows(self, column_index: int, search_value: str) -> List[int]:
        """Encuentra filas que contengan un valor específico en una columna"""
        values = self.read_sheet()
        matching_rows = []
        for i, row in enumerate(values):
            if len(row) > column_index and row[column_index] == search_value:
                matching_rows.append(i + 1)  # +1 porque las filas empiezan en 1
        return matching_rows
