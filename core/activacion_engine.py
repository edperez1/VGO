class ActivacionEngine:
    @staticmethod
    def generar_script_zte(datos):
        """
        Toma un diccionario con interfaz, id, sn, vlan y nombre,
        y devuelve una lista de comandos lista para la OLT.
        """
        # Estructura base del script de Nitido
        script = [
            "conf t",
            f"interface gpon-olt_{datos['interfaz']}",
            f"onu {datos['onu_id']} type {datos['modelo']} sn {datos['sn']}",
            "exit",
            f"interface gpon-onu_{datos['interfaz']}:{datos['onu_id']}",
            f"name {datos['nombre']}",
            f"tcont 1 profile {datos['perfil_up']}",
            "gemport 1 name DATA tcont 1",
            f"service-port 1 vport 1 user-vlan {datos['vlan']} vlan {datos['vlan']}",
            "write" # Siempre guardamos para evitar pérdidas
        ]
        return script