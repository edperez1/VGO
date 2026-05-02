import flet as ft
from core.olt_engine import OLTEngine
from views.login_view import get_login_view
from views.dashboard_view import get_dashboard_view
from views.activacion_view import get_activacion_view

def main(page: ft.Page):
    # --- CONFIGURACIÓN DE PÁGINA ---
    page.title = "VGO - Velocity GPON Orchestrator"
    # Aumentamos el ancho para que la nueva consola se vea bien
    page.window_width = 1200 
    page.window_height = 850
    page.theme_mode = ft.ThemeMode.DARK
    
    # Diseño centrado inicial
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Mantenemos tu estructura de datos original
    page.session_data = {"olt_ip": None, "olt_engine": None, "role": None}

    # --- FUNCIONES DE NAVEGACIÓN ---
    
    def ir_a_activacion(e):
        page.clean()
        page.add(get_activacion_view(page, volver_al_dashboard))
        page.update()

    def volver_al_dashboard(e=None):
        page.clean()
        page.add(generar_dashboard_con_menu())
        page.update()

    def handle_logout(e):
        """Lógica para cerrar sesión y limpiar datos"""
        page.session_data["role"] = None
        page.clean()
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        mostrar_pantalla_inicial()
        page.update()

    # --- NUEVA FUNCIÓN DE DESCONEXIÓN DE OLT ---
    def disconnect_olt(e):
        """Lógica para limpiar por completo la conexión y el overlay de Flet"""
        page.session_data["olt_ip"] = None
        page.session_data["olt_engine"] = None
        page.session_data["role"] = None
        
        # Limpiamos todos los elementos en pantalla y en la memoria del overlay
        page.clean()
        page.overlay.clear()
        
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        mostrar_pantalla_inicial()
        page.update()

    def generar_dashboard_con_menu():
        """
        CORRECCIÓN: Ahora pasamos 'page', 'ir_a_activacion' y 'logout'
        para que coincida con la nueva vista del Dashboard.
        """
        return get_dashboard_view(
            page=page, 
            ir_a_activacion=ir_a_activacion, 
            logout=handle_logout
        )

    def handle_login(username, password):
        # Mantenemos tu lógica de conexión original
        res = page.session_data["olt_engine"].connect(username, password)
        
        if res["status"] == "success":
            page.session_data["role"] = username
            page.clean()
            page.vertical_alignment = ft.MainAxisAlignment.START
            page.add(generar_dashboard_con_menu())
            page.update()   
        else:
            snack = ft.SnackBar(ft.Text(res["message"]), bgcolor=ft.Colors.RED_700, open=True)
            page.overlay.append(snack)
            page.update()

    def start_conn(e):
        if ip_input.value:
            page.session_data["olt_ip"] = ip_input.value
            page.session_data["olt_engine"] = OLTEngine(ip_input.value)
            page.clean()
            
            # Asegúrate de que login_view reciba los parámetros correctos
            page.add(get_login_view(handle_login, page))
            
            # Botón de desconexión integrado de forma segura
            page.add(
                ft.Container(
                    content=ft.TextButton(
                        "← Cambiar IP de la OLT", 
                        on_click=disconnect_olt,
                        style=ft.ButtonStyle(color=ft.Colors.GREY_400)
                    ),
                    margin=ft.margin.only(top=10)
                )
            )
            page.update()

    # --- PANTALLA DE INICIO ---
    def mostrar_pantalla_inicial():
        global ip_input
        ip_input = ft.TextField(label="IP OLT", value="127.0.0.1", width=300)
        
        page.add(
            ft.Column([
                ft.Icon(ft.Icons.ROUTER, size=50, color=ft.Colors.BLUE),
                ft.Text("CONEXIÓN OLT", size=20, weight="bold"),
                ip_input,
                # Usamos FilledButton para eliminar el DeprecationWarning en Flet 0.80+
                ft.FilledButton("Establecer Enlace", on_click=start_conn)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

    mostrar_pantalla_inicial()

if __name__ == "__main__":
    # Usamos run() para compatibilidad con las últimas versiones
    ft.run(main)