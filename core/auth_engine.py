"""
VGO - Auth Engine
Este módulo gestiona la seguridad y el Control de Acceso Basado en Roles (RBAC).
"""

class AuthManager:
    def __init__(self):
        # Base de datos local de usuarios (En un futuro podría ser SQL o JSON)
        self._users = {
            "tecnico": {
                "password": "tecn1c0.",
                "role": "tecnico",
                "permissions": {
                    "can_edit_vlans": False, # Solo usa las pre-cargadas
                    "default_vlan": "100",
                    "max_speed_profile": "100M"
                }
            },
            "admin": {
                "password": "admin",
                "role": "admin",
                "permissions": {
                    "can_edit_vlans": True, # Puede cambiar a cualquier VLAN
                    "default_vlan": "30",
                    "max_speed_profile": "FULL"
                }
            }
        }

    def authenticate(self, username, password):
        """
        Valida las credenciales y devuelve los datos del rol si es exitoso.
        """
        # Verificamos si el usuario existe en nuestro diccionario
        if username in self._users:
            user_data = self._users[username]
            # Validamos la contraseña
            if user_data["password"] == password:
                return {
                    "status": "success",
                    "role": user_data["role"],
                    "permissions": user_data["permissions"]
                }
        
        # Si algo falla, devolvemos error
        return {"status": "error", "message": "Credenciales inválidas"}

# --- BLOQUE DE PRUEBA INDEPENDIENTE ---
if __name__ == "__main__":
    auth = AuthManager()
    
    # Prueba 1: Técnico exitoso
    print("Probando Login Técnico...")
    resultado = auth.authenticate("tecnico", "tecn1c0.")
    print(f"Resultado: {resultado['status']} - Rol: {resultado.get('role')}")

    # Prueba 2: Fallo intencional
    print("\nProbando Login Erróneo...")
    fallo = auth.authenticate("admin", "12345")
    print(f"Resultado: {fallo['status']} - Msg: {fallo['message']}")