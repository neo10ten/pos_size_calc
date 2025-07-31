# ui_classes/primary_ui.py

from .shared_imports import *
from .scrollable_spinner import ScrollableSpinner
from ..assets import CURRENCIES,STANDARD_SET,OTHER_INSTRUMENTS

class PrimaryUI(BoxLayout):
    def __init__(self, controller, **kwargs):
        super().__init__(orientation="vertical", spacing=10, padding=10, **kwargs)
        self.controller = controller

        # Build GridLayout form, store references to self.acc_input, etc.
        form = GridLayout(cols=2, row_force_default=True,
                          row_default_height=40, spacing=5)

        # Account Balance
        form.add_widget(Label(text="Account Balance:"))
        self.acc_input = TextInput(multiline=False, input_filter="float")
        form.add_widget(self.acc_input)
        
        # Account Currency
        form.add_widget(Label(text="Account Currency:"))
        self.acc_curr = ScrollableSpinner(text="Select From: ", values=sorted(CURRENCIES))
        form.add_widget(self.acc_curr)
        
        # Allocation % of account
        form.add_widget(Label(text="Allocate % of Account:"))
        self.pct_input = TextInput(multiline=False, input_filter="float")
        form.add_widget(self.pct_input)

        # Stock Price
        form.add_widget(Label(text="Stock Price:"))
        self.price_input = TextInput(multiline=False, input_filter="float")
        form.add_widget(self.price_input)
        
        # Stock Currency
        form.add_widget(Label(text="Stock Currency:"))
        self.stock_curr = ScrollableSpinner(text="Select From: ", values=sorted(CURRENCIES))
        form.add_widget(self.stock_curr)
        
        # Stock Leverage
        form.add_widget(Label(text="Stock Leverage - Default 1:1:"))
        self.lev_input = TextInput(text="1.0", multiline=False, input_filter="float")
        form.add_widget(self.lev_input)

        # FX-Pair Spinner
        form.add_widget(Label(text="Or pick a predefined pair:"))
        self.pair_spinner = ScrollableSpinner(text="Select Pair", values=sorted(STANDARD_SET))
        self.pair_spinner.bind(text=self.on_pair_select)
        form.add_widget(self.pair_spinner)

        # Non-currency Instruments
        form.add_widget(Label(text="Other Instruments:"))
        # Will load from oanda_inst2.json in current version
        other_insts = OTHER_INSTRUMENTS
        self.other_inst_spinner = ScrollableSpinner(text="View Other Instruments", values=sorted(other_insts))
        form.add_widget(self.other_inst_spinner)
        
        # FX Rate field (auto‐populated or manual)
        form.add_widget(Label(text="FX Rate:"))
        if self.controller.online:
            hint_text = "Fetching..."
        else:
            hint_text = "Enter manually: "
        self.rate_input = TextInput(
            multiline=False, input_filter="float",
            hint_text=""
        )
        form.add_widget(self.rate_input)

        # Inline error + spacer
        self.error_label = Label(text="THIS IS AN ERROR LABEL", color=(1,0,0,1))
        form.add_widget(self.error_label)
        form.add_widget(Label())
        
        # Wrap form in ScrollView and add widget
        scroll = ScrollView(size_hint=(1,1))
        scroll.add_widget(form)
        self.add_widget(scroll)
        
        # Activate rate updater
        self.controller.start_rate_updates()
        
        # Add final calculate button to process form inputs
        self.calc_btn = Button(text="Calculate", size_hint_y=None, height=40)
        self.calc_btn.bind(on_release=self.on_calculate)
        self.add_widget(self.calc_btn)
        
        # Create result label and add
        self.result_label = Label(text="", size_hint_y=None, height=30)
        self.update_result
        self.add_widget(self.result_label)
    
    # Function to allocate b/q according to selection
    def on_pair_select(self, spinner, text):
        """Update base/quote and delegate rate fetch."""
        if len(text) == 6:
            self.acc_curr.text = text[:3]
            self.stock_curr.text = text[3:]
            self.controller.fetch_rate_once()
    
    # Function to update rate
    def update_rate(self,rate):
        # Controller calls to refresh FX rate field
        self.rate_input.text = f"{rate: .6f}"
    
    # Function to send values to controller for processing
    def on_calculate(self, _):
        """Gather inputs, then hand off to controller."""
        try:
            raw = {
                "account":      float(self.acc_input.text),
                "pct":          float(self.pct_input.text),
                "price":        float(self.price_input.text),
                "base":         self.acc_curr.text,
                "quote":        self.stock_curr.text,
                "manual_rate":  float(self.rate_input.text) if self.rate_input.text else None
            }
        except ValueError:
            self.show_error("Enter valid numbers in all fields.")
            return

        if self.controller.online:   ########     NEED TO CHANGE?????? here to end of func
            self.controller.start_calculation(raw)
        else:
            self.controller.prompt_manual_rate()

    # Function to update result after calculation runs
    def update_result(self, qty, rate):
        self.result_label.text = f"Qty: {qty}, Rate: {rate:.4f}"
        
    # Function prompt error if calculation fails
    def show_error(self, msg):
        Popup(title="Error",
              content=Label(text=msg),
              size_hint=(0.8,0.4)).open()
