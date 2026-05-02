import flet as ft
import pyperclip
from core.activacion_engine import ActivacionEngine

def get_activacion_view(page: ft.Page, funcion_volver):
    
    # --- LÓGICA DE GENERACIÓN ---
    def generar_texto_script():
        interfaz = txt_interfaz.value if txt_interfaz.value else "1/2/2"
        onu_id = txt_id.value if txt_id.value else "70"
        sn = txt_sn.value if txt_sn.value else "GPON00000000"
        nombre = txt_nombre.value if txt_nombre.value else "NOMBRE_CLIENTE"
        vlan = txt_vlan.value if txt_vlan.value else "30"
        tipo = txt_modelo.value if txt_modelo.value else "WK-3802AWC"
        
        # Leemos el valor de los megas ingresados (por defecto 100M como tu estructura original)
        megas_subida = txt_megas_subida.value if txt_megas_subida.value else "100"
        megas_bajada = txt_megas_bajada.value if txt_megas_bajada.value else "100"

        return f"""interface gpon-olt_{interfaz}
  onu {onu_id} type {tipo} sn {sn}
!
interface gpon-onu_{interfaz}:{onu_id}
  name {nombre}
  tcont 1 name San-Ramon profile T-DBA-{megas_subida}M
  gemport 1 unicast tcont 1 dir both
  gemport 1 traffic-limit upstream DBA-{megas_subida}M downstream DBA-{megas_bajada}M
  switchport mode hybrid vport 1
  service-port 1 vport 1 user-vlan {vlan} vlan {vlan}
!
pon-onu-mng gpon-onu_{interfaz}:{onu_id}
  service Internet gemport 1 vlan {vlan}  
  wan-ip 1 mode dhcp vlan-profile vlan{vlan} host 1  
  security-mng 1 state enable mode permit protocol web https
  interface video video_0/1 power-control enable
!"""

    def actualizar_script(e=None):
        script_display.value = generar_texto_script()
        try:
            script_display.update()
        except:
            pass 

    # --- CONTROLES DE ENTRADA ---
    txt_interfaz = ft.TextField(label="Interfaz (Slot/Port)", value="1/2/2", on_change=actualizar_script)
    txt_id = ft.TextField(label="ONU ID", value="70", on_change=actualizar_script)
    txt_modelo = ft.TextField(
        label="Tipo de ONU", 
        value="WK-3802AWC", 
        hint_text="ZTE-F660, WK..., etc.",
        on_change=actualizar_script
    )
    txt_sn = ft.TextField(label="Serial Number (SN)", value="GPON00522610", on_change=actualizar_script)
    txt_nombre = ft.TextField(label="Nombre Cliente", value="Jairo Orlando Alegrias Rojas", on_change=actualizar_script)
    txt_vlan = ft.TextField(label="VLAN", value="30", on_change=actualizar_script)
    
    # NUEVOS CAMPOS: Para ver el ancho de banda T-DBA en el script en tiempo real
    txt_megas_subida = ft.TextField(
        label="Megas de Subida", 
        value="100", 
        on_change=actualizar_script
    )
    txt_megas_bajada = ft.TextField(
        label="Megas de Bajada", 
        value="100", 
        on_change=actualizar_script
    )

    # --- EDITOR DE SCRIPT (Grande y Ancho) ---
    script_display = ft.TextField(
        label="Script",
        value=generar_texto_script(),
        multiline=True,
        min_lines=22,
        max_lines=25,
        bgcolor=ft.Colors.BLACK,
        color=ft.Colors.GREEN_400,
        text_size=13,
        expand=True,
        text_style=ft.TextStyle(font_family="Consolas"),
    )

    def copiar_script(e):
        script_texto = script_display.value
        try:
            pyperclip.copy(script_texto)
        except Exception:
            page.clipboard.set(script_texto)
            page.clipboard.update()

        snack = ft.SnackBar(
            content=ft.Text("Script de activación copiado al portapapeles"), 
            bgcolor=ft.Colors.BLUE_GREY_800, 
            open=True
        )
        page.overlay.append(snack)
        page.update()

    # --- DISEÑO FINAL ---
    return ft.Container(
        padding=20,
        expand=True,
        content=ft.Column([
            ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=funcion_volver),
                ft.Text("MÓDULO DE ACTIVACIÓN - NITIDO", size=22, weight="bold"),
            ]),
            ft.Row([
                # Formulario Izquierda
                ft.Column([
                    ft.Text("DATOS DE CONFIGURACIÓN", color=ft.Colors.BLUE_400, weight="bold"),
                    txt_interfaz,
                    txt_id,
                    txt_modelo,
                    txt_sn,
                    txt_nombre,
                    txt_vlan,
                    ft.Text("ANCHO DE BANDA (T-DBA)", color=ft.Colors.ORANGE_400, weight="bold"),
                    txt_megas_subida,
                    txt_megas_bajada,
                ], width=280, spacing=10),
                
                # Script Derecha
                ft.Column([
                    script_display,
                    ft.FilledButton(
                        "COPIAR SCRIPT", 
                        icon=ft.Icons.COPY,
                        height=50,
                        width=1000,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.GREEN_700, 
                            color=ft.Colors.WHITE
                        ),
                        on_click=copiar_script,
                    )
                ], expand=True, spacing=10)
            ], expand=True, vertical_alignment=ft.CrossAxisAlignment.START)
        ], spacing=20)
    )