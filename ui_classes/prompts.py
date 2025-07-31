# pos_size_calc/ui_classes/prompts.py

from . import BoxLayout, Label, Button, Popup

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