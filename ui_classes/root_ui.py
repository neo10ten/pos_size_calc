# ui_classes/root_ui.py

from .shared_imports import BoxLayout, Label, Button
from .primary_ui_2 import PrimaryUI
from ..tool_classes.main_controller import Controller



class RootLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        
        # Generate controllers
        controller = Controller()
        
        # Generate UIs
        self.header = Label(text="Position Sizer",size_hint_y=None, height=40)
        self.primary = PrimaryUI(controller=controller,size_hint_y=1)
        self.footer = Button(text="Browse All Pairs",size_hint_y=None, height=40)

        # Add widgets to Layout
        self.add_widget(self.header)
        self.add_widget(self.primary)
        self.add_widget(self.footer)