from . import Spinner, Window, ScrollView


class ScrollableSpinner(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_dropdown_height = Window.height * 0.6

    def _create_dropdown(self):
        dropdown = super()._create_dropdown()
        orig = dropdown.container
        scroll = ScrollView(
            size_hint=(1, None),
            height=self.max_dropdown_height,
            scroll_type=['bars','content'],
            bar_width='10dp'
        )
        scroll.add_widget(orig)
        dropdown.container = scroll
        return dropdown