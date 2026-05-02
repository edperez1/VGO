class ListaEngine:
    def __init__(self):
        self.comandos_disponibles = [
            # --- Configuración ---
            {"categoria": "Configuración", "comando": "configure terminal", "descripcion": "Acceso al modo de configuración global"},
            {"categoria": "Configuración", "comando": "interface gpon", "descripcion": "Entra a la interfaz de configuración de puertos PON"},
            {"categoria": "Configuración", "comando": "interface vlan", "descripcion": "Configura interfaces VLAN"},
            {"categoria": "Configuración", "comando": "write memory", "descripcion": "Guarda la configuración en memoria"},
            {"categoria": "Configuración", "comando": "exit", "descripcion": "Salir del modo actual"},
            {"categoria": "Configuración", "comando": "quit", "descripcion": "Regresa al nivel anterior o cierra sesión"},
            
            # --- Revisión / Monitoreo ---
            {"categoria": "Revisión", "comando": "show version", "descripcion": "Muestra la versión del sistema"},
            {"categoria": "Revisión", "comando": "show running-config", "descripcion": "Muestra la configuración en ejecución"},
            {"categoria": "Revisión", "comando": "show gpon onu unconfigured", "descripcion": "Muestra las ONU no configuradas en el sistema"},
            {"categoria": "Revisión", "comando": "show gpon onu state", "descripcion": "Muestra el estado de las ONU conectadas"},
            {"categoria": "Revisión", "comando": "show card", "descripcion": "Muestra información de las tarjetas instaladas"},
            {"categoria": "Revisión", "comando": "show system-group", "descripcion": "Muestra información general del sistema"},
            {"categoria": "Revisión", "comando": "show interface brief", "descripcion": "Muestra un resumen de las interfaces"},
            {"categoria": "Revisión", "comando": "show vlan summary", "descripcion": "Muestra el resumen de VLANs"},
            {"categoria": "Revisión", "comando": "show mac", "descripcion": "Muestra la tabla de direcciones MAC"},
            {"categoria": "Revisión", "comando": "show cpu", "descripcion": "Muestra el uso de CPU"},
            {"categoria": "Revisión", "comando": "show memory", "descripcion": "Muestra el uso de memoria"},
            {"categoria": "Revisión", "comando": "show process", "descripcion": "Muestra procesos activos"},
            {"categoria": "Revisión", "comando": "show log", "descripcion": "Muestra los registros del sistema"},
            {"categoria": "Revisión", "comando": "show users", "descripcion": "Muestra usuarios conectados"},
            {"categoria": "Revisión", "comando": "show ntp", "descripcion": "Muestra estado de sincronización NTP"},
            {"categoria": "Revisión", "comando": "show snmp", "descripcion": "Muestra configuración SNMP"},
            {"categoria": "Revisión", "comando": "show qos", "descripcion": "Muestra configuración de QoS"},
            {"categoria": "Revisión", "comando": "show traffic", "descripcion": "Muestra estadísticas de tráfico"},
            
            # --- Sistema ---
            {"categoria": "Sistema", "comando": "display board 0", "descripcion": "Muestra el estado e información de las tarjetas instaladas"},
            {"categoria": "Sistema", "comando": "display ont info", "descripcion": "Despliega la información de las ONT conectadas"},
            {"categoria": "Sistema", "comando": "reload", "descripcion": "Reinicia el sistema"},
            {"categoria": "Sistema", "comando": "ping", "descripcion": "Prueba de conectividad con otro dispositivo"},
            {"categoria": "Sistema", "comando": "traceroute", "descripcion": "Traza la ruta hacia un destino"},
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
