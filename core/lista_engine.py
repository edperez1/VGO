class ListaEngine:
    def __init__(self):
        self.comandos_disponibles = [
            {"categoria": "Configuración", "comando": "configure terminal", "descripcion": "Acceso al modo de configuración global"},
            {"categoria": "Revisión", "comando": "show gpon onu unconfigured", "descripcion": "Muestra las ONU no configuradas en el sistema"},
            {"categoria": "Configuración", "comando": "interface gpon", "descripcion": "Entra a la interfaz de configuración de puertos PON"},
            {"categoria": "Revisión", "comando": "display board 0", "descripcion": "Muestra el estado e información de las tarjetas instaladas"},
            {"categoria": "Revisión", "comando": "display ont info", "descripcion": "Despliega la información de las ONT conectadas"},
            {"categoria": "Sistema", "comando": "quit", "descripcion": "Regresa al nivel anterior o sale de la sesión actual"}
        ]

    def obtener_lista(self) -> list:
        return self.comandos_disponibles

    def buscar_comandos(self, filtro: str, texto_busqueda: str = "") -> list:
        filtrados = []
        texto_busqueda = texto_busqueda.lower()
        
        for item in self.comandos_disponibles:
            # Filtro de categoría
            if filtro != "Todos" and item["categoria"] != filtro:
                continue
                
            # Filtro de texto
            if texto_busqueda and not (texto_busqueda in item["comando"].lower() or texto_busqueda in item["descripcion"].lower()):
                continue
                
            filtrados.append(item)
            
        return filtrados