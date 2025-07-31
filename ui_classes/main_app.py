# pos_size_calc/ui_classes/main_app.py

from kivy.app import App

from .root_ui import RootLayout
from .prompts import show_update_prompt
from ..assets.updater import download_assets
from ..services.startup import prewarm_rates,check_for_update




class MainApp(App):
    def build(self):
        return RootLayout()

    def on_start(self):
        # 1) Warm rates
        prewarm_rates()

        # 2) Check assets; if needed, prompt user on the main loop
        check_for_update(lambda result: 
            show_update_prompt(*result, download_assets) if result else None
        )