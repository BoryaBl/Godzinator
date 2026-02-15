from __future__ import annotations

import customtkinter as ctk

from ui.sidebar import (
    VIEW_TIME_CONVERTER,
    VIEW_TIME_MULTIPLY,
    VIEW_TIME_SUM,
    Sidebar,
)
from ui.views.placeholder_view import PlaceholderView
from ui.views.time_converter_view import TimeConverterView
from ui.views.time_sum_view import TimeSumView


class GodzinatorApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Godzinator")
        self.geometry("1140x700")
        self.minsize(900, 560)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, on_select=self.show_view, initial_view=VIEW_TIME_SUM)
        self.sidebar.grid(row=0, column=0, sticky="nsw", padx=(0, 8), pady=0)

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=16)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self._view_cache: dict[str, ctk.CTkFrame] = {}
        self._current_view_id = ""

        self.show_view(VIEW_TIME_SUM)

    def show_view(self, view_id: str) -> None:
        if view_id == self._current_view_id:
            self.sidebar.set_active(view_id)
            return

        view = self._get_or_create_view(view_id)

        for child in self.content.winfo_children():
            child.grid_forget()

        view.grid(row=0, column=0, sticky="nsew")
        self._current_view_id = view_id
        self.sidebar.set_active(view_id)

    def _get_or_create_view(self, view_id: str) -> ctk.CTkFrame:
        cached = self._view_cache.get(view_id)
        if cached is not None:
            return cached

        if view_id == VIEW_TIME_SUM:
            view: ctk.CTkFrame = TimeSumView(self.content)
        elif view_id == VIEW_TIME_CONVERTER:
            view = TimeConverterView(self.content)
        elif view_id == VIEW_TIME_MULTIPLY:
            view = PlaceholderView(
                self.content,
                title="Mnożenie czasu",
                description="Ten widok jest w przygotowaniu.",
            )
        else:
            view = PlaceholderView(
                self.content,
                title="Nieznany widok",
                description="Wybrany widok nie istnieje.",
            )

        self._view_cache[view_id] = view
        return view
