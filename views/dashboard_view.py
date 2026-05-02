import sys
import os
import time
import flet as ft
import pyperclip
import re

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
    
    # Determinamos el prompt inicial
    prompt_inicial = "OLT#"
    if olt and hasattr(olt, 'last_prompt') and olt.last_prompt:
        prompt_inicial = olt.last_prompt

    state = {"prompt": prompt_inicial}

    # --- CONTROLES DE LA UI ---
    txt_temp_view = ft.Text(f"TEMPERATURA: {page.session_data.get('olt_temp', '...')}")
    txt_voltaje_view = ft.Text(f"VOLTAJE: {page.session_data.get('olt_voltaje', '...')}")
    txt_onus_view = ft.Text(f"ONUS ACTIVAS: {page.session_data.get('olt_onus', '...')}")
    txt_modelo_view = ft.Text(f"MODELO: {page.session_data.get('olt_modelo', '...')}")
    
    olt_ip = page.session_data.get('olt_ip', '0.0.0.0')
    olt_tarjetas = page.session_data.get('olt_cards', '---')

    # --- LÓGICA DE ACTUALIZACIÓN AJUSTADA ---

    def actualizar_datos_tecnicos():
        """Actualiza los valores y refresca la página completa"""
        try:
            if olt:
                datos = olt.obtener_datos_tiempo_real()
                txt_temp_view.value = f"TEMPERATURA: {datos['temp']}"
                txt_voltaje_view.value = f"VOLTAJE: {datos['voltaje']}"
                txt_onus_view.value = f"ONUS ACTIVAS: {datos['onus']}"
                txt_modelo_view.value = f"MODELO: {datos['modelo']}"
                
                # Refresca toda la página de golpe
                page.update()
        except Exception as ex:
            consola_output.value += f"\n% Error al actualizar datos técnicos: {repr(ex)}"
            page.update()

    def manejar_teclado(e: ft.KeyboardEvent):
        if e.key is None:
            return
            
        if e.key in ["Arrow Right", "Tab"]:
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
            if not linea_limpia: continue
            try:
                if olt:
                    respuesta = olt.send_command(linea_limpia)
                    resultados.append(f"{state['prompt']}{linea_limpia}\n{respuesta}")
                    time.sleep(0.1)
            except Exception as ex:
                resultados.append(f"{state['prompt']}{linea_limpia}\n% Exception: {repr(ex)}")
        return "\n".join(resultados)

    def enviar_comando_manual(e=None):
        global ultima_respuesta_consola
        entrada = txt_comando_directo.value.strip()
        if not entrada: return

        if "\n" in entrada or "\r" in entrada:
            consola_output.value += f"\n--- PROCESANDO SCRIPT MULTILÍNEA ---"
            if olt:
                resultado = enviar_script_multilinea(entrada)
                consola_output.value += f"\n{resultado}"
            else:
                consola_output.value += "\n% Error: No hay conexión activa con la OLT."
        else:
            engine.add_to_history(entrada)
            consola_output.value += f"\n{state['prompt']}{entrada}"
            try:
                if olt:
                    respuesta_raw = olt.send_command(entrada)
                    consola_output.value += f"\n{respuesta_raw}"
                    
                    # Detección de prompt avanzada
                    for linea in respuesta_raw.splitlines():
                        if re.search(r"(ZTE.*[>#])$", linea.strip()):
                            state["prompt"] = linea.strip()
                            break
                    
                    actualizar_datos_tecnicos()
                else:
                    consola_output.value += "\n% Error: No hay conexión activa con la OLT."
            except Exception as ex:
                consola_output.value += f"\n% Exception: {repr(ex)}"

        txt_comando_directo.value = ""
        txt_comando_directo.label = f"Escriba comando ({state['prompt']})..."
        ultima_respuesta_consola = consola_output.value
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
        
        txt_busqueda = ft.TextField(label="Buscar comando...", icon=ft.Icons.SEARCH, width=350)
        dd_categoria = ft.Dropdown(
            label="Categoría", width=200, value="Todos",
            options=[ft.dropdown.Option("Todos"), ft.dropdown.Option("Configuración"), ft.dropdown.Option("Revisión"), ft.dropdown.Option("Sistema")]
        )
        contenedor_lista = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

        def actualizar_lista(e=None):
            contenedor_lista.controls.clear()
            datos = lista_engine.buscar_comandos(filtro=dd_categoria.value, texto_busqueda=txt_busqueda.value)
            for idx, item in enumerate(datos, 1):
                contenedor_lista.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(f"[{idx}] {item['categoria']}", weight="bold", color=ft.Colors.BLUE_400, size=12),
                                ft.Text(item['descripcion'], color=ft.Colors.GREY_300, size=15),
                            ], expand=True),
                            ft.Container(
                                content=ft.Text(f"{item['comando']}", font_family="Consolas", color=ft.Colors.GREEN_400),
                                bgcolor=ft.Colors.BLACK, padding=10, border_radius=8, width=300
                            ),
                            ft.IconButton(icon=ft.Icons.COPY, on_click=lambda e, c=item['comando']: copiar_al_portapapeles(c))
                        ]),
                        padding=12, border=ft.border.all(1, ft.Colors.BLUE_GREY_700), border_radius=10, margin=ft.margin.only(bottom=8)
                    )
                )
            page.update()

        txt_busqueda.on_change = actualizar_lista
        dd_categoria.on_change = actualizar_lista
        actualizar_lista()

        page.add(
            ft.Container(
                padding=20, expand=True,
                content=ft.Column([
                    ft.Row([ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: volver_al_dashboard_desde_lista()), ft.Text("MÓDULO DE COMANDOS - NITIDO", size=20, weight="bold")]),
                    ft.Divider(),
                    ft.Row([txt_busqueda, dd_categoria], spacing=15),
                    contenedor_lista
                ])
            )
        )

    def copiar_al_portapapeles(comando: str):
        page.set_clipboard(comando)
        snack = ft.SnackBar(content=ft.Text("Copiado al portapapeles"), open=True)
        page.overlay.append(snack)
        page.update()

    def volver_al_dashboard_desde_lista(e=None):
        page.clean()
        page.add(get_dashboard_view(page, ir_a_activacion, logout))

    # --- CONFIGURACIÓN DE VISTA ---
    valor_consola = f"--- VGO TERMINAL ACTIVA ---\n{state['prompt']}"
    if ultima_respuesta_consola is not None:
        valor_consola = ultima_respuesta_consola

    consola_output = ft.TextField(
        value=valor_consola, multiline=True, read_only=True,
        bgcolor=ft.Colors.BLACK, color=ft.Colors.GREEN_400,
        text_size=13, text_style=ft.TextStyle(font_family="Consolas"),
        expand=True, border=ft.InputBorder.NONE,
    )

    txt_comando_directo = ft.TextField(
        label=f"Escriba comando ({state['prompt']})...",
        expand=True, on_submit=enviar_comando_manual,
        text_style=ft.TextStyle(font_family="Consolas"),
    )

    grid_botones = ft.Column([
        ft.FilledButton("MODO ACTIVACIÓN", icon=ft.Icons.ADD_CIRCLE, on_click=ir_a_activacion, width=250),
        ft.FilledButton("LISTA COMANDOS", icon=ft.Icons.LIST_ALT, on_click=ir_a_lista_comandos, width=250),
    ], spacing=12)

    # Nota: Se eliminó la llamada a actualizar_datos_tecnicos() aquí para evitar errores de renderizado.

    return ft.Container(
        padding=20, expand=True,
        content=ft.Column([
            ft.Row([
                ft.Column([ft.Text("VGO DASHBOARD", size=28, weight="bold"), ft.Text("Gestión de Redes protocol telnet POO", color=ft.Colors.GREY_500)], expand=True),
                ft.IconButton(ft.Icons.LOGOUT, on_click=logout, icon_color=ft.Colors.RED_400),
            ]),
            ft.Divider(),
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Column([
                                ft.Text("ESTADO OLT", weight="bold", color=ft.Colors.BLUE_400, size=14),
                                ft.Text(f"IP: {olt_ip}"),
                                txt_modelo_view,
                                ft.Row([ft.Icon(ft.Icons.CIRCLE, color=ft.Colors.GREEN, size=10), ft.Text("ONLINE")], spacing=5),
                            ], width=260),
                            ft.VerticalDivider(width=1, color=ft.Colors.BLUE_GREY_800),
                            ft.Column([
                                ft.Text("DATOS TÉCNICOS EN TIEMPO REAL", weight="bold", color=ft.Colors.ORANGE_400, size=12),
                                ft.Text(f"SLOTS: {olt_tarjetas}"),
                                txt_temp_view, txt_voltaje_view, txt_onus_view,
                            ], width=270)
                        ], spacing=15)
                    ]),
                    padding=15, border=ft.border.all(1, ft.Colors.BLUE_GREY_800), border_radius=10, expand=True,
                ),
                grid_botones
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text("TERMINAL CLI", weight="bold", size=14),
            ft.Column([
                ft.Container(content=consola_output, expand=True, bgcolor=ft.Colors.BLACK, border_radius=10),
                ft.Row([txt_comando_directo, ft.IconButton(ft.Icons.DELETE_SWEEP_OUTLINED, on_click=limpiar_terminal), ft.IconButton(ft.Icons.SEND, on_click=enviar_comando_manual)])
            ], expand=True)
        ], spacing=20)
    )