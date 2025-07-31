from .utils import setup_logging
setup_logging()

from .ui_classes.main_app import MainApp

if __name__ == "__main__":
    MainApp().run()