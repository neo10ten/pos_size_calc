# ui_classes/prompts.py


from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup

# Function prompt version price update
def show_update_prompt(local, remote, on_confirm):
    txt = f"Assets v{remote} available (you have v{local}). Download?"
    layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
    layout.add_widget(Label(text=txt))

    btns = BoxLayout(size_hint_y=None, height=40, spacing=10)
    yes, no = Button(text="Yes"), Button(text="No")
    btns.add_widget(yes); btns.add_widget(no)
    layout.add_widget(btns)

    popup = Popup(title="Update Assets", content=layout, size_hint=(0.8, 0.4))
    yes.bind(on_release=lambda *_: (popup.dismiss(), on_confirm()))
    no.bind(on_release=popup.dismiss)
    popup.open()
    
# Function prompt error if calculation fails
def show_error(self, msg):
    
    layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
    layout.add_widget(Label(text=msg))
    
    btn = BoxLayout(size_hint_y=None, height=40, spacing=10)
    ok = Button(text="OK")
    btn.add_widget(ok)
    layout.add_widget(btn)
    
    popup = Popup(title="Error",
            content=layout,
            size_hint=(0.8,0.4))
    ok.bind(on_release=popup.dismiss)
    popup.open()

# Function to prommpt manual input for FX rate
def prompt_manual_rate(self):
    msg = "OFFLINE: \nPlease enter FX rate manually."
    layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
    layout.add_widget(Label(text=msg))
    
    btn = BoxLayout(size_hint_y=None, height=40, spacing=10)
    ok = Button(text="OK")
    btn.add_widget(ok)
    layout.add_widget(btn)
    
    popup = Popup(title="No Network Connection Detected",
            content=layout,
            size_hint=(0.8,0.4))
    ok.bind(on_release=popup.dismiss)
    popup.open()