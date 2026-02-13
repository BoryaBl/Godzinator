import customtkinter as ctk

from ui.app import GodzinatorApp


def run_app() -> None:
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    app = GodzinatorApp()
    app.mainloop()
