from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

VIEW_TIME_SUM = "time_sum"
VIEW_DAYS_FROM_NORM = "days_from_norm"
VIEW_TIME_MULTIPLY = "time_multiply"


class Sidebar(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, on_select: Callable[[str], None], initial_view: str) -> None:
        super().__init__(master, width=240, corner_radius=0)
        self.grid_propagate(False)

        self._on_select = on_select
        self._buttons: dict[str, ctk.CTkButton] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(99, weight=1)

        brand_label = ctk.CTkLabel(
            self,
            text="Godzinator",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
        )
        brand_label.grid(row=0, column=0, sticky="w", padx=20, pady=(26, 24))

        self._create_nav_button(1, VIEW_TIME_SUM, "Sumowanie czasu")
        self._create_nav_button(2, VIEW_DAYS_FROM_NORM, "Dni z normy")
        self._create_nav_button(3, VIEW_TIME_MULTIPLY, "Mnożenie czasu")

        self.set_active(initial_view)

    def _create_nav_button(self, row: int, view_id: str, text: str) -> None:
        button = ctk.CTkButton(
            self,
            text=text,
            height=42,
            anchor="w",
            corner_radius=10,
            fg_color="transparent",
            hover_color=("#e2e8f0", "#22262f"),
            text_color=("#1f2937", "#f3f4f6"),
            border_width=1,
            border_color=("#d1d5db", "#374151"),
            command=lambda selected=view_id: self._handle_select(selected),
        )
        button.grid(row=row, column=0, sticky="ew", padx=16, pady=6)
        self._buttons[view_id] = button

    def _handle_select(self, view_id: str) -> None:
        self._on_select(view_id)

    def set_active(self, view_id: str) -> None:
        for current_view_id, button in self._buttons.items():
            is_active = current_view_id == view_id
            if is_active:
                button.configure(
                    fg_color=("#1f6aa5", "#1f6aa5"),
                    hover_color=("#185381", "#185381"),
                    text_color="white",
                    border_width=0,
                )
            else:
                button.configure(
                    fg_color="transparent",
                    hover_color=("#e2e8f0", "#22262f"),
                    text_color=("#1f2937", "#f3f4f6"),
                    border_width=1,
                    border_color=("#d1d5db", "#374151"),
                )
