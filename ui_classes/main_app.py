# ui_classes/main_app.py

from kivy.app import App

from .root_ui import RootLayout
from ..services.startup import prewarm_rates,version_update_check
from ..services.previous_prices import save_previous_prices


class MainApp(App):
    def build(self):
        return RootLayout()

    def on_start(self):

        # 1) Check for updated asset verions
        version_update_check()
        
        # 2) Warm rates
        prewarm_rates()
    
    def on_stop(self):
        
        # NEEDS FIXING TO PASS PRICES FROM WHEREVER HELD ON RUNTIME???
        
        # Save prices to cache for use on next open when offline
        save_previous_prices()