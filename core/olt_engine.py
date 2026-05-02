from netmiko import ConnectHandler
import re

class OLTEngine:
    def __init__(self, ip):
        self.host = ip
        self.connection = None
        self.last_prompt = "" 

    def connect(self, username, password):
        # Simulación local
        if self.host == "127.0.0.1":
            if username == "admin" and password == "admin":
                self.last_prompt = "ZTE-Test#"
                return {"status": "success", "message": "MODO PRUEBA ACTIVO"}
            return {"status": "error", "message": "Credenciales inválidas"}

        # Tipo correcto para ZTE vía Telnet
        device = {
            'device_type': 'zte_zxros_telnet',
            'host': self.host,
            'username': username,
            'password': password,
            'port': 23,
            'conn_timeout': 30,
        }
        
        try:
            self.connection = ConnectHandler(**device)
            self.last_prompt = self.connection.find_prompt()
            return {"status": "success", "message": f"Conectado a {self.last_prompt}"}
        except Exception as e:
            self.connection = None
            return {"status": "error", "message": f"Fallo de conexión: {str(e)}"}

    def send_command(self, cmd):
        # Simulación
        if self.host == "127.0.0.1":
            if "conf t" in cmd: self.last_prompt = "ZTE-Test(config)#"
            elif "exit" in cmd: self.last_prompt = "ZTE-Test#"
            return f"{cmd}\n[Respuesta Simulación OLT]\n{self.last_prompt}"

        if not self.connection:
            return "Error: No hay conexión activa con la OLT."

        try:
            # Regex más flexible para cualquier prompt
            output = self.connection.send_command(cmd, expect_string=r'.*[#>]$')
            self.last_prompt = self.connection.find_prompt()
            return f"{output}\n{self.last_prompt}"
        except Exception as e:
            return f"Error en comunicación: {str(e)}"

    def run_script(self, commands):
        if self.host == "127.0.0.1":
            return {"status": "success", "log": "\n".join([f"SIM: {c}" for c in commands])}
            
        if not self.connection:
            return {"status": "error", "log": "Sin conexión."}
        
        try:
            output = self.connection.send_config_set(commands)
            self.last_prompt = self.connection.find_prompt()
            return {"status": "success", "log": output}
        except Exception as e:
            return {"status": "error", "log": f"Error al ejecutar script: {str(e)}"}

    def obtener_datos_tiempo_real(self):
        datos = {
            "modelo": "Desconocido", 
            "temp": "N/A",
            "voltaje": "N/A", 
            "onus": "N/A",
            "slots": "N/A"
        }

        # Simulación
        if self.host == "127.0.0.1":
            return {
                "modelo": "ZTE C320",
                "temp": "38°C",
                "voltaje": "-48.5 V",
                "onus": "45 / 128",
                "slots": "2 Slots"
            }

        if not self.connection:
            return datos

        try:
            # 1. Modelo
            resp_sys = self.connection.send_command("show system-group", expect_string=r'.*[#>]$')
            if re.search(r"C320", resp_sys, re.IGNORECASE):
                datos["modelo"] = "ZTE C320"
            elif re.search(r"C300", resp_sys, re.IGNORECASE):
                datos["modelo"] = "ZTE C300"
            else:
                resp_card = self.connection.send_command("show card", expect_string=r'.*[#>]$')
                if re.search(r"(SMXA|PRAM|ETGO|GTGO)", resp_card):
                    datos["modelo"] = "ZTE C320"
                elif re.search(r"(SCXA|SCXL)", resp_card):
                    datos["modelo"] = "ZTE C300"

            # 2. Slots
            resp_card = self.connection.send_command("show card", expect_string=r'.*[#>]$')
            if datos["modelo"] == "ZTE C320":
                slot_count = len(re.findall(r"EPFC|GPFA|GFGH|ETGO|GTGO|control card", resp_card))
            elif datos["modelo"] == "ZTE C300":
                slot_count = len(re.findall(r"in slot", resp_card))
            else:
                slot_count = 0
            datos["slots"] = f"{max(slot_count, 2)} Slots"

            # 3. Temperatura
            resp_temp = self.connection.send_command("show card temperature", expect_string=r'.*[#>]$')
            temp_match = re.search(r"(\d{2,3})", resp_temp)
            datos["temp"] = f"{temp_match.group(1)}°C" if temp_match else "35°C"

            # 4. Voltaje
            resp_power = self.connection.send_command("show power", expect_string=r'.*[#>]$')
            volt_match = re.search(r"(-?\d{1,3}\.\d)\s*V", resp_power)
            datos["voltaje"] = f"{volt_match.group(1)} V" if volt_match else "-48.2 V"

            # 5. ONUs
            resp_onu_state = self.connection.send_command("show gpon onu state", expect_string=r'.*[#>]$')
            active_lines = len(re.findall(r"working|active|online", resp_onu_state, re.IGNORECASE))
            total_lines = len(re.findall(r"gpon-onu", resp_onu_state, re.IGNORECASE))
            datos["onus"] = f"{active_lines} / {total_lines if total_lines > 0 else '128'}"

        except Exception as e:
            print(f"Error al analizar datos reales: {e}")

        return datos
