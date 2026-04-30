from netmiko import ConnectHandler
import time

class OLTEngine:
    def __init__(self, ip):
        self.host = ip
        self.connection = None
        self.last_prompt = "" # Aquí guardaremos el nombre real de la OLT

    def connect(self, username, password):
        # --- MODO PRUEBA (Simulación local) ---
        if self.host == "127.0.0.1":
            if username == "admin" and password == "admin":
                self.last_prompt = "ZTE-Test#"
                return {"status": "success", "message": "MODO PRUEBA ACTIVO"}
            return {"status": "error", "message": "Credenciales inválidas"}

        # --- CONEXIÓN REAL (ZTE C320) ---
        device = {
            'device_type': 'zte_zxros_telnet',
            'host': self.host,
            'username': username,
            'password': password,
            'port': 23,
            'conn_timeout': 30, # Aumentado para OLTs lentas
        }
        
        try:
            self.connection = ConnectHandler(**device)
            # Capturamos el prompt inicial inmediatamente después de conectar
            self.last_prompt = self.connection.find_prompt()
            return {"status": "success", "message": f"Conectado a {self.last_prompt}"}
        except Exception as e:
            self.connection = None
            return {"status": "error", "message": f"Fallo de conexión: {str(e)}"}

    def send_command(self, cmd):
        """
        Envía un comando manual y devuelve la respuesta exacta de la OLT,
        incluyendo el nuevo prompt (ej: tecnico(config)#).
        """
        if self.host == "127.0.0.1":
            # Simulación de cambio de modo en modo prueba
            if "conf t" in cmd: self.last_prompt = "ZTE-Test(config)#"
            elif "exit" in cmd: self.last_prompt = "ZTE-Test#"
            return f"{cmd}\n[Respuesta Simulación OLT]\n{self.last_prompt}"

        if not self.connection:
            return "Error: Sesión Telnet cerrada."

        try:
            # send_command captura la respuesta hasta que aparece el nuevo prompt (# o >)
            output = self.connection.send_command(cmd, expect_string=r'[#>]')
            # Actualizamos nuestro registro del prompt
            self.last_prompt = self.connection.find_prompt()
            
            # Devolvemos la respuesta + el nuevo prompt para el Dashboard
            return f"{output}\n{self.last_prompt}"
        except Exception as e:
            return f"Error en comunicación: {str(e)}"

    def run_script(self, commands):
        """Ejecuta ráfagas de comandos (para activaciones automáticas)."""
        if self.host == "127.0.0.1":
            return {"status": "success", "log": "\n".join([f"SIM: {c}" for c in commands])}
            
        if not self.connection:
            return {"status": "error", "log": "Sin conexión."}
        
        try:
            # send_config_set es ideal para los scripts de configuración masiva
            output = self.connection.send_config_set(commands)
            self.last_prompt = self.connection.find_prompt()
            return {"status": "success", "log": output}
        except Exception as e:
            return {"status": "error", "log": str(e)}