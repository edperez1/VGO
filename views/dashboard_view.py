import sys
import os
import time
import flet as ft
import pyperclip

# Aseguramos la ruta para poder importar el módulo 'core'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.complete_engine import CompleteEngine
from core.lista_engine import ListaEngine

ultima_respuesta_consola = None

def get_dashboard_view(page: ft.Page, ir_a_activacion, logout):
    global ultima_respuesta_consola
    
    olt = page.session_data.get("olt_engine")
    engine = CompleteEngine()
    lista_engine = ListaEngine()
    
    prompt_inicial = "OLT#"
    if olt and hasattr(olt, 'last_prompt') and olt.last_prompt:
        prompt_inicial = olt.last_prompt

    state = {"prompt": prompt_inicial}

    # Datos técnicos en tiempo real
    olt_ip = page.session_data.get('olt_ip', '10.20.30.2')
    olt_modelo = page.session_data.get('olt_modelo', 'ZTE C300')
    olt_tarjetas = page.session_data.get('olt_cards', '2 Slots')
    olt_temp = page.session_data.get('olt_temp', '38°C')
    olt_voltaje = page.session_data.get('olt_voltaje', '-48.5 V')
    olt_onus = page.session_data.get('olt_onus', '45 / 128')
    
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

    def enviar_script_multilinea(script_texto):
        lineas = script_texto.splitlines()
        resultados = []
        
        for linea in lineas:
            linea_limpia = linea.strip()
            if not linea_limpia:
                continue
            
            try:
                respuesta = olt.send_command(linea_limpia)
                resultados.append(f"OLT#{linea_limpia}\n{respuesta}")
                time.sleep(0.1)
            except Exception as ex:
                resultados.append(f"OLT#{linea_limpia}\n% Exception: {str(ex)}")
                break
                
        return "\n".join(resultados)

    def enviar_comando_manual(e):
        global ultima_respuesta_consola
        entrada = txt_comando_directo.value.strip()
        if not entrada:
            return

        if "\n" in entrada or "\r" in entrada:
            consola_output.value += f"\n--- PROCESANDO SCRIPT MULTILÍNEA ---"
            try:
                if olt:
                    resultado = enviar_script_multilinea(entrada)
                    consola_output.value += f"\n{resultado}"
                else:
                    consola_output.value += "\n% Error: No connection to OLT (Simulación)."
            except Exception as ex:
                consola_output.value += f"\n% Exception: {str(ex)}"
        else:
            engine.add_to_history(entrada)
            consola_output.value += f"\n{state['prompt']}{entrada}"
            
            try:
                if olt:
                    respuesta_raw = olt.send_command(entrada)
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
        
        ultima_respuesta_consola = consola_output.value
        consola_output.update()
        page.update()

    def limpiar_terminal(e):
        global ultima_respuesta_consola
        consola_output.value = f"--- VGO TERMINAL (NITIDO) ---\n{state['prompt']}"
        ultima_respuesta_consola = consola_output.value
        consola_output.update()

    def ir_a_lista_comandos(e):
        global ultima_respuesta_consola
        if consola_output.value:
            ultima_respuesta_consola = consola_output.value

        page.clean()
        
        txt_busqueda = ft.TextField(
            label="Buscar comando o descripción...", 
            icon=ft.Icons.SEARCH,
            width=350
        )
        
        dd_categoria = ft.Dropdown(
            label="Categoría",
            width=200,
            value="Todos",
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("Configuración"),
                ft.dropdown.Option("Revisión"),
                ft.dropdown.Option("Sistema"),
            ]
        )
        
        contenedor_lista = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

        def actualizar_lista(e=None):
            contenedor_lista.controls.clear()
            
            datos = lista_engine.buscar_comandos(
                filtro=dd_categoria.value,
                texto_busqueda=txt_busqueda.value
            )
            
            for idx, item in enumerate(datos, 1):
                contenedor_lista.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(f"[{idx}] {item['categoria']}", weight="bold", color=ft.Colors.BLUE_400, size=12),
                                ft.Text(item['descripcion'], color=ft.Colors.GREY_300, size=15),
                            ], expand=True, alignment=ft.MainAxisAlignment.CENTER),
                            
                            ft.Container(
                                content=ft.Text(f"{item['comando']}", font_family="Consolas", color=ft.Colors.GREEN_400),
                                bgcolor=ft.Colors.BLACK,
                                padding=10,
                                border_radius=8,
                                border=ft.border.all(1, ft.Colors.BLUE_GREY_800),
                                width=300
                            ),
                            
                            ft.IconButton(
                                icon=ft.Icons.COPY, 
                                icon_color=ft.Colors.BLUE_300, 
                                tooltip="Copiar comando",
                                on_click=lambda e, c=item['comando']: copiar_al_portapapeles(c)
                            )
                        ]),
                        padding=12,
                        border=ft.border.all(1, ft.Colors.BLUE_GREY_700),
                        border_radius=10,
                        margin=ft.margin.only(bottom=8)
                    )
                )
            page.update()

        txt_busqueda.on_change = actualizar_lista
        dd_categoria.on_change = actualizar_lista
        
        actualizar_lista()

        page.add(
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK, 
                            icon_color=ft.Colors.WHITE,
                            on_click=lambda e: volver_al_dashboard_desde_lista()
                        ),
                        ft.Text("MÓDULO DE COMANDOS - NITIDO", size=20, weight="bold", color=ft.Colors.WHITE)
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Divider(),
                    
                    ft.Row([
                        txt_busqueda,
                        dd_categoria
                    ], alignment=ft.MainAxisAlignment.START, spacing=15),
                    ft.Divider(),
                    
                    contenedor_lista
                ], spacing=15)
            )
        )
        page.update()

    def copiar_al_portapapeles(comando: str):
        try:
            pyperclip.copy(comando)
        except Exception:
            page.clipboard.set(comando)
            page.clipboard.update()

        snack = ft.SnackBar(
            content=ft.Text(f"Copiado al portapapeles"), 
            bgcolor=ft.Colors.BLUE_GREY_800, 
            open=True
        )
        page.overlay.append(snack)
        page.update()

    def volver_al_dashboard_desde_lista(e=None):
        page.clean()
        page.add(get_dashboard_view(page, ir_a_activacion, logout))
        page.update()

    valor_consola = f"--- VGO TERMINAL ACTIVA ---\n{state['prompt']}"
    if ultima_respuesta_consola is not None:
        valor_consola = ultima_respuesta_consola

    consola_output = ft.TextField(
        value=valor_consola,
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

    # Botones unificados y estandarizados con el mismo tamaño y padding
    estilo_boton = ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=8), 
        padding=18
    )

    grid_botones = ft.Column([
        ft.FilledButton(
            "MODO ACTIVACIÓN", 
            icon=ft.Icons.ADD_CIRCLE, 
            on_click=ir_a_activacion, 
            style=estilo_boton, 
            width=250
        ),
        ft.FilledButton(
            "LISTA COMANDOS", 
            icon=ft.Icons.LIST_ALT, 
            on_click=ir_a_lista_comandos, 
            style=estilo_boton, 
            width=250
        ),
    ], spacing=12)

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
            
            # Fila superior unificada
            ft.Row([
                # Contenedor fusionado (Estado y Datos en una sola caja)
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Column([
                                ft.Text("ESTADO OLT", weight="bold", color=ft.Colors.BLUE_400, size=14),
                                ft.Text(f"IP: {olt_ip}"),
                                ft.Text(f"MODELO: {olt_modelo}"),
                                ft.Row([ft.Icon(ft.Icons.CIRCLE, color=ft.Colors.GREEN, size=10), ft.Text("ONLINE")], spacing=5),
                            ], width=260, spacing=5),
                            
                            ft.VerticalDivider(width=1, color=ft.Colors.BLUE_GREY_800),
                            
                            ft.Column([
                                ft.Text("DATOS TÉCNICOS EN TIEMPO REAL", weight="bold", color=ft.Colors.ORANGE_400, size=12),
                                ft.Text(f"SLOTS: {olt_tarjetas}"),
                                ft.Text(f"TEMPERATURA: {olt_temp}"),
                                ft.Text(f"VOLTAJE: {olt_voltaje}"),
                                ft.Text(f"ONUS ACTIVAS: {olt_onus}"),
                            ], width=270, spacing=4)
                        ], vertical_alignment=ft.CrossAxisAlignment.START, spacing=15)
                    ]),
                    padding=15, 
                    border=ft.border.all(1, ft.Colors.BLUE_GREY_800), 
                    border_radius=10, 
                    expand=True,
                ),
                
                # Botones Estandarizados a la derecha
                ft.Container(
                    content=grid_botones, 
                    padding=5
                )
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