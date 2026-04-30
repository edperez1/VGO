"""
VGO - Script Engine
Generador de comandos CLI para OLT ZTE C320.
"""

class ScriptEngine:
    def __init__(self):
        # Plantillas de comandos base para la ZTE C320
        self.templates = {
            "add_onu": "pon-onu-mng gpon-onu_{interface}:{onu_id}",
            "service_port": "service-port 1 vport 1 user-vlan {vlan} vlan {vlan}",
            "description": "description {client_name}",
            "sn_bind": "onu {onu_id} type {onu_type} sn {sn_serial}"
        }

    def generate_activation_script(self, data):
        """
        Toma un diccionario con: interface, onu_id, sn, name, vlan, type
        y devuelve una lista de strings con los comandos finales.
        """
        script = []
        
        # 1. Entrar al modo de configuración de la interfaz
        # Suponiendo que la interface viene como '1/2/1'
        script.append(f"interface gpon-olt_{data['interface']}")
        
        # 2. Registrar el SN de la ONU
        script.append(
            self.templates["sn_bind"].format(
                onu_id=data['onu_id'],
                onu_type=data.get('type', 'ZTE-F660'), # Tipo por defecto
                sn_serial=data['sn']
            )
        )
        script.append("exit")
        
        # 3. Configurar el flujo de datos (MNG)
        script.append(
            self.templates["add_onu"].format(
                interface=data['interface'],
                onu_id=data['onu_id']
            )
        )
        
        # 4. Asignar la VLAN y Nombre del cliente
        script.append(self.templates["description"].format(client_name=data['name']))
        script.append(self.templates["service_port"].format(vlan=data['vlan']))
        script.append("exit")
        
        return script

# --- BLOQUE DE PRUEBA INDEPENDIENTE ---
if __name__ == "__main__":
    engine = ScriptEngine()
    
    # Datos de prueba similares a los que enviará el Dashboard
    mock_data = {
        "interface": "1/2/1",
        "onu_id": "3",
        "sn": "GPON00522610",
        "name": "Jairo_Alegrias",
        "vlan": "100",
        "type": "ZTE-G"
    }
    
    comandos = engine.generate_activation_script(mock_data)
    
    print("--- SCRIPT GENERADO PARA VGO ---")
    for cmd in comandos:
        print(f"DEBUG: {cmd}")