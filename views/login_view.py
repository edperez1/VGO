import flet as ft

def get_login_view(on_login_attempt, page_ref: ft.Page):
    user_field = ft.TextField(
        label="Usuario", 
        prefix_icon=ft.Icons.PERSON, 
        width=300,
        border_radius=10
    )
    pass_field = ft.TextField(
        label="Contraseña", 
        password=True, 
        can_reveal_password=True, 
        width=300,
        border_radius=10
    )

    def handle_login_click(e):
        # 1. Limpiamos errores previos
        user_field.error_text = None
        
        # 2. Enviamos los datos al main.py para que el AuthManager haga su trabajo
        # IMPORTANTE: Pasamos los valores, no argumentos con nombre como 'role'
        if user_field.value and pass_field.value:
            on_login_attempt(user_field.value, pass_field.value)
        else:
            user_field.error_text = "Complete todos los campos"
            page_ref.update()

    return ft.Column(
        [
            ft.Icon(ft.Icons.LOCK, size=80, color=ft.Colors.BLUE_700),
            ft.Text("VGO SYSTEM", size=26, weight="bold"),
            user_field,
            pass_field,
            ft.ElevatedButton(
                "INGRESAR", 
                on_click=handle_login_click, 
                width=300,
                bgcolor=ft.Colors.BLUE_700,
                color=ft.Colors.WHITE
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True
    )