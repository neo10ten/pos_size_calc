# pos_size_calc/__main__.py

from .config.core.logging_config import configure_logging
from .ui_classes.main_app import MainApp


if __name__ == "__main__":
    
    # Run loggin set up
    configure_logging()
    
    
    # Call run of main App.
    MainApp().run()