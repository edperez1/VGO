import sys
import os
import flet as ft

# Aseguramos la ruta para poder importar el módulo 'core'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.complete_engine import CompleteEngine

def get_dashboard_view(page: ft.Page, ir_a_activacion, logout):
    olt = page.session_data.get("olt_engine")
    engine = CompleteEngine()
    
    prompt_inicial = "OLT#"
    if olt and hasattr(olt, 'last_prompt') and olt.last_prompt:
        prompt_inicial = olt.last_prompt

    state = {"prompt": prompt_inicial}

    def manejar_teclado(e: ft.KeyboardEvent):
        if e.key == "Arrow Right" or e.key == "Tab":
            valor_actual = txt_comando_directo.value.strip()
            if valor_actual:
                sugerencia = engine.get_progressive_options(valor_actual)
                if sugerencia:
                    txt_comando_directo.value = sugerencia
                    txt_comando_directo.focus()
                    page.update()
                    
        elif e.key == "Arrow Up":
            comando_anterior = engine.get_previous_command()
            if comando_anterior:
                txt_comando_directo.value = comando_anterior
                page.update()
        elif e.key == "Arrow Down":
            comando_siguiente = engine.get_next_command()
            txt_comando_directo.value = comando_siguiente
            page.update()
        
    page.on_keyboard_event = manejar_teclado

    def enviar_comando_manual(e):
        comando = txt_comando_directo.value.strip()
        if not comando:
            return

        engine.add_to_history(comando)
        consola_output.value += f"\n{state['prompt']}{comando}"

        try:
            if olt:
                respuesta_raw = olt.send_command(comando)
                consola_output.value += f"\n{respuesta_raw}"
                
                lineas = respuesta_raw.splitlines()
                if lineas:
                    state["prompt"] = lineas[-1].strip()
            else:
                consola_output.value += "\n% Error: No connection to OLT."
        except Exception as ex:
            consola_output.value += f"\n% Exception: {str(ex)}"

        txt_comando_directo.value = ""
        txt_comando_directo.label = f"Escriba comando ({state['prompt']})..."
        consola_output.update()
        page.update()

    def limpiar_terminal(e):
        consola_output.value = f"--- VGO TERMINAL (NITIDO) ---\n{state['prompt']}"
        consola_output.update()
        
    def ejecutar_comando_rapido(comando_texto):
        txt_comando_directo.value = comando_texto
        enviar_comando_manual(None)

    consola_output = ft.TextField(
        value=f"--- VGO TERMINAL ACTIVA ---\n{state['prompt']}",
        multiline=True,
        read_only=True,
        bgcolor=ft.Colors.BLACK,
        color=ft.Colors.GREEN_400,
        text_size=13,
        text_style=ft.TextStyle(font_family="Consolas"),
        expand=True,
        border=ft.InputBorder.NONE,
    )

    txt_comando_directo = ft.TextField(
        label=f"Escriba comando ({state['prompt']})...",
        expand=True,
        on_submit=enviar_comando_manual,
        text_style=ft.TextStyle(font_family="Consolas"),
    )

    estilo_boton = ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), padding=20)

    grid_botones = ft.Column([
        ft.Row([
            ft.FilledButton("MODO ACTIVACIÓN", icon=ft.Icons.ADD_CIRCLE, on_click=ir_a_activacion, style=estilo_boton, expand=True),
            ft.FilledButton("SHOW UNCFG", icon=ft.Icons.SEARCH, on_click=lambda e: ejecutar_comando_rapido("show gpon onu unconfigured"), style=estilo_boton, expand=True),
        ], spacing=10),
        ft.Row([
            ft.FilledButton("CONF T", icon=ft.Icons.SETTINGS, on_click=lambda e: ejecutar_comando_rapido("configure terminal"), style=estilo_boton, expand=True),
            ft.FilledButton("LISTA COMANDOS", icon=ft.Icons.LIST_ALT, on_click=lambda e: ejecutar_comando_rapido("show"), style=estilo_boton, expand=True),
        ], spacing=10),
    ], spacing=10, width=600)

    return ft.Container(
        padding=20,
        expand=True,
        content=ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("VGO DASHBOARD", size=28, weight="bold"),
                    ft.Text("Gestión de Redes protocolo telnet POO", color=ft.Colors.GREY_500),
                ], expand=True),
                ft.IconButton(ft.Icons.LOGOUT, on_click=logout, icon_color=ft.Colors.RED_400),
            ]),
            ft.Divider(),
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text("ESTADO OLT", weight="bold", color=ft.Colors.BLUE_400),
                        ft.Text(f"IP: {page.session_data.get('olt_ip', '0.0.0.0')}"),
                        ft.Row([ft.Icon(ft.Icons.CIRCLE, color=ft.Colors.GREEN, size=10), ft.Text("ONLINE")], spacing=5),
                    ]),
                    padding=20, border=ft.border.all(1, ft.Colors.BLUE_GREY_800), border_radius=10, width=250
                ),
                grid_botones
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text("TERMINAL CLI", weight="bold", size=14),
            ft.Column([
                ft.Container(
                    content=consola_output,
                    expand=True,
                    bgcolor=ft.Colors.BLACK,
                    border_radius=10,
                    border=ft.border.all(1, ft.Colors.BLUE_GREY_800),
                ),
                ft.Row([
                    txt_comando_directo,
                    ft.IconButton(ft.Icons.DELETE_SWEEP_OUTLINED, icon_color=ft.Colors.RED_400, on_click=limpiar_terminal, tooltip="Limpiar Terminal"),
                    ft.IconButton(ft.Icons.SEND, icon_color=ft.Colors.BLUE, on_click=enviar_comando_manual),
                ])
            ], expand=True)
        ], spacing=20)
    )