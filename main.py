import flet as ft
import requests

# --- Updated to your specific laptop IP ---
SERVER_URL = "http://10.179.209.62:5000"

def main(page: ft.Page):
    # 1. Setup the Mobile Screen Dimensions
    page.window.width = 380
    page.window.height = 700
    page.title = "Smart Farm App"
    page.theme_mode = "light"
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # --- UI COMPONENTS FOR ALL SCREENS ---
    title = ft.Text("🌱 Smart Farm OS", size=28, weight="bold", color=ft.Colors.TEAL_700)
    
    # ==========================================
    # SCREEN 1: MAIN MENU
    # ==========================================
    def go_live(e):
        home_screen.visible = False
        manual_screen.visible = False
        live_screen.visible = True
        page.update()
        fetch_live_data() # Fetch data immediately when opening live screen

    def go_manual(e):
        home_screen.visible = False
        live_screen.visible = False
        manual_screen.visible = True
        page.update()

    home_screen = ft.Column(
        visible=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text("Select Operating Mode", size=18, color=ft.Colors.GREY_700),
            ft.Divider(height=20, color="transparent"),
            ft.Container(
                content=ft.Column([
                    ft.Text("📡 Live Hardware Mode", size=20, weight="bold", color=ft.Colors.TEAL_700),
                    ft.Text("Monitor real-time ESP32 data", size=14, color=ft.Colors.GREY_600)
                ]),
                padding=20, bgcolor=ft.Colors.CYAN_50, border_radius=10, 
                border=ft.border.all(2, ft.Colors.TEAL_400),
                on_click=go_live, ink=True, width=320
            ),
            ft.Divider(height=15, color="transparent"),
            ft.Container(
                content=ft.Column([
                    ft.Text("💻 Manual Override", size=20, weight="bold", color=ft.Colors.ORANGE_800),
                    ft.Text("Test AI logic safely", size=14, color=ft.Colors.GREY_600)
                ]),
                padding=20, bgcolor=ft.Colors.ORANGE_50, border_radius=10, 
                border=ft.border.all(2, ft.Colors.ORANGE_400),
                on_click=go_manual, ink=True, width=320
            ),
        ]
    )

    # ==========================================
    # NAVIGATION LOGIC (Back Button)
    # ==========================================
    def go_home(e):
        live_screen.visible = False
        manual_screen.visible = False
        home_screen.visible = True
        page.update()

    back_btn = ft.ElevatedButton("← Back to Menu", on_click=go_home, color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_GREY_400)

    # ==========================================
    # SCREEN 2: LIVE HARDWARE MODE
    # ==========================================
    live_temp = ft.Text("-- °C", size=24, weight="bold")
    live_hum = ft.Text("-- %", size=24, weight="bold")
    live_moist = ft.Text("-- %", size=24, weight="bold")
    live_status = ft.Text("Waiting for connection...", size=16, weight="bold", text_align=ft.TextAlign.CENTER)
    
    live_card = ft.Container(content=live_status, padding=15, bgcolor=ft.Colors.GREY_200, border_radius=8, width=320)

    def fetch_live_data(e=None):
        live_status.value = "Fetching data..."
        page.update()
        try:
            response = requests.get(f"{SERVER_URL}/live-status")
            data = response.json()
            
            if data.get('status') == 'success':
                d = data['data']
                live_temp.value = f"{d['temperature']} °C"
                live_hum.value = f"{d['humidity']} %"
                live_moist.value = f"{d['moisture']} %"
                
                if d['pump_action'] == 1:
                    live_status.value = "🚿 STATUS: WATERING REQUIRED"
                    live_status.color = ft.Colors.GREEN_900
                    live_card.bgcolor = ft.Colors.GREEN_200
                else:
                    live_status.value = "✅ STATUS: NORMAL (No Water Needed)"
                    live_status.color = ft.Colors.BLUE_GREY_900
                    live_card.bgcolor = ft.Colors.BLUE_GREY_100
            else:
                live_status.value = "⏳ Waiting for Firebase logs..."
        except Exception:
            live_status.value = "❌ Error: Cannot connect to server"
            live_status.color = ft.Colors.RED_900
            live_card.bgcolor = ft.Colors.RED_100
        page.update()

    live_screen = ft.Column(
        visible=False,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            back_btn,
            ft.Divider(height=10, color="transparent"),
            ft.Text("📡 Live Hardware Status", size=22, weight="bold", color=ft.Colors.TEAL_600),
            ft.Row([
                ft.Container(content=ft.Column([ft.Text("Temp", color=ft.Colors.GREY_600), live_temp]), bgcolor=ft.Colors.GREY_100, padding=15, border_radius=8, expand=1),
                ft.Container(content=ft.Column([ft.Text("Hum", color=ft.Colors.GREY_600), live_hum]), bgcolor=ft.Colors.GREY_100, padding=15, border_radius=8, expand=1),
            ]),
            ft.Row([
                ft.Container(content=ft.Column([ft.Text("Moisture", color=ft.Colors.GREY_600), live_moist]), bgcolor=ft.Colors.GREY_100, padding=15, border_radius=8, expand=1),
            ]),
            ft.ElevatedButton("🔄 Refresh Live Data", on_click=fetch_live_data, color=ft.Colors.WHITE, bgcolor=ft.Colors.TEAL_500, width=320),
            live_card
        ]
    )

    # ==========================================
    # SCREEN 3: MANUAL OVERRIDE MODE
    # ==========================================
    temp_text = ft.Text("Temperature: 30 °C", weight="bold")
    hum_text = ft.Text("Humidity: 50 %", weight="bold")
    moist_text = ft.Text("Soil Moisture: 40 %", weight="bold")

    def update_temp(e):
        temp_text.value = f"Temperature: {int(e.control.value)} °C"
        page.update()
    def update_hum(e):
        hum_text.value = f"Humidity: {int(e.control.value)} %"
        page.update()
    def update_moist(e):
        moist_text.value = f"Soil Moisture: {int(e.control.value)} %"
        page.update()

    temp_slider = ft.Slider(min=0, max=50, value=30, on_change=update_temp, active_color=ft.Colors.ORANGE_600)
    hum_slider = ft.Slider(min=0, max=100, value=50, on_change=update_hum, active_color=ft.Colors.ORANGE_600)
    moist_slider = ft.Slider(min=0, max=100, value=40, on_change=update_moist, active_color=ft.Colors.ORANGE_600)

    manual_status = ft.Text("Adjust sliders and run prediction.", size=16, weight="bold", text_align=ft.TextAlign.CENTER)
    manual_card = ft.Container(content=manual_status, padding=15, bgcolor=ft.Colors.GREY_200, border_radius=8, width=320)

    def ask_ai(e):
        t = temp_slider.value
        h = hum_slider.value
        m = moist_slider.value

        manual_status.value = "Running AI logic..."
        page.update()

        try:
            # Send POST request matching our new server setup
            payload = {"temperature": t, "humidity": h, "moisture": m}
            response = requests.post(f"{SERVER_URL}/manual-predict", json=payload)
            data = response.json()

            if data.get('status') == 'success':
                manual_status.value = f"AI Decision: {data['message']}"
                if data['prediction'] == 1:
                    manual_status.color = ft.Colors.GREEN_900
                    manual_card.bgcolor = ft.Colors.GREEN_200
                else:
                    manual_status.color = ft.Colors.BLUE_GREY_900
                    manual_card.bgcolor = ft.Colors.BLUE_GREY_100
        except Exception as ex:
            manual_status.value = "❌ Error: Cannot connect to server"
            manual_status.color = ft.Colors.RED_900
            manual_card.bgcolor = ft.Colors.RED_100
        page.update()

    check_btn = ft.ElevatedButton("🧠 Run AI Prediction", on_click=ask_ai, width=320, color=ft.Colors.WHITE, bgcolor=ft.Colors.ORANGE_700)

    manual_screen = ft.Column(
        visible=False,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            back_btn,
            ft.Divider(height=10, color="transparent"),
            ft.Text("💻 Manual AI Testing", size=22, weight="bold", color=ft.Colors.ORANGE_800),
            temp_text, temp_slider,
            hum_text, hum_slider,
            moist_text, moist_slider,
            check_btn,
            ft.Divider(height=5, color="transparent"),
            manual_card
        ]
    )

    # 4. Add the Base Components to the Page
    page.add(
        title,
        ft.Divider(height=10, color="transparent"),
        home_screen,
        live_screen,
        manual_screen
    )

ft.app(target=main)