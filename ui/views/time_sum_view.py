from __future__ import annotations

import uuid

import customtkinter as ctk

from time_utils import calculate_time_expression, seconds_to_float_hours
from ui.models import TimeRowState
from ui.utils.time_sum_helpers import build_expression_payload, format_signed_seconds
from ui.widgets.time_row import TimeRowWidget


class TimeSumView(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass) -> None:
        super().__init__(master, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0, minsize=360)
        self.grid_rowconfigure(0, weight=1)

        self._rows: dict[str, TimeRowWidget] = {}
        self._row_order: list[str] = []

        self._clock_result_var = ctk.StringVar(value="00:00:00")
        self._hours_result_var = ctk.StringVar(value="0.00 h")

        self._build_rows_panel()
        self._build_results_panel()

        self.add_row()

    def _build_rows_panel(self) -> None:
        panel = ctk.CTkFrame(self, corner_radius=18)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=0)
        panel.grid_columnconfigure(0, weight=1)

        heading = ctk.CTkLabel(
            panel,
            text="Sumowanie czasu",
            font=ctk.CTkFont(family="Segoe UI", size=30, weight="bold"),
        )
        heading.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 4))

        description = ctk.CTkLabel(
            panel,
            text="Wpisuj pozycje w formacie HH:MM:SS, ustawiaj + lub - i obserwuj wynik na żywo.",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=("#475569", "#94a3b8"),
        )
        description.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 12))

        self._rows_scrollable = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        self._rows_scrollable.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 12))
        self._rows_scrollable.grid_columnconfigure(0, weight=1)

        footer = ctk.CTkFrame(panel, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 16))
        footer.grid_columnconfigure(0, weight=1)
        footer.grid_columnconfigure(1, weight=1)

        add_button = ctk.CTkButton(
            footer,
            text="Dodaj pozycję",
            height=38,
            command=self.add_row,
        )
        add_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        clear_button = ctk.CTkButton(
            footer,
            text="Wyczyść wszystko",
            height=38,
            fg_color="transparent",
            border_width=1,
            border_color=("#d1d5db", "#4b5563"),
            hover_color=("#fee2e2", "#7f1d1d"),
            text_color=("#991b1b", "#fecaca"),
            command=self.clear_all,
        )
        clear_button.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        panel.grid_rowconfigure(2, weight=1)

    def _build_results_panel(self) -> None:
        panel = ctk.CTkFrame(self, corner_radius=18, width=360)
        panel.grid(row=0, column=1, sticky="ns", padx=(12, 0), pady=0)
        panel.grid_propagate(False)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(5, weight=1)

        heading = ctk.CTkLabel(
            panel,
            text="Wynik",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
        )
        heading.grid(row=0, column=0, sticky="w", padx=24, pady=(24, 10))

        clock_title = ctk.CTkLabel(
            panel,
            text="Format zegarowy",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=("#64748b", "#94a3b8"),
        )
        clock_title.grid(row=1, column=0, sticky="w", padx=24)

        clock_result = ctk.CTkLabel(
            panel,
            textvariable=self._clock_result_var,
            width=300,
            anchor="w",
            font=ctk.CTkFont(family="Consolas", size=44, weight="bold"),
        )
        clock_result.grid(row=2, column=0, sticky="w", padx=24, pady=(0, 10))

        hours_title = ctk.CTkLabel(
            panel,
            text="Format dziesiętny",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=("#64748b", "#94a3b8"),
        )
        hours_title.grid(row=3, column=0, sticky="sw", padx=24)

        hours_result = ctk.CTkLabel(
            panel,
            textvariable=self._hours_result_var,
            width=300,
            anchor="w",
            font=ctk.CTkFont(family="Consolas", size=32, weight="bold"),
        )
        hours_result.grid(row=4, column=0, sticky="nw", padx=24, pady=(0, 24))

    def add_row(self) -> None:
        row_id = uuid.uuid4().hex
        row_state = TimeRowState(row_id=row_id)

        row_widget = TimeRowWidget(
            self._rows_scrollable,
            row_state=row_state,
            on_change=self._on_row_change,
            on_toggle=self._on_row_toggle,
            on_remove=self._on_row_remove,
        )

        self._rows[row_id] = row_widget
        self._row_order.append(row_id)

        self._regrid_rows()
        self.recalculate()

    def remove_row(self, row_id: str) -> None:
        row_widget = self._rows.pop(row_id, None)
        if row_widget is None:
            return

        row_widget.destroy()
        self._row_order = [current_id for current_id in self._row_order if current_id != row_id]

        if not self._row_order:
            self.add_row()
            return

        self._regrid_rows()
        self.recalculate()

    def clear_all(self) -> None:
        for row_id in list(self._row_order):
            self._rows[row_id].destroy()

        self._rows.clear()
        self._row_order.clear()

        self.add_row()

    def recalculate(self) -> None:
        ordered_states = [self._rows[row_id].state for row_id in self._row_order]
        times, operators, total_seconds = build_expression_payload(ordered_states)

        try:
            calculate_time_expression(times, operators)
        except Exception as error:
            print(f"[Godzinator] Calculation error: {error}")
            self._set_result_values(0)
            return

        self._set_result_values(total_seconds)

    def _set_result_values(self, total_seconds: int) -> None:
        self._clock_result_var.set(format_signed_seconds(total_seconds))

        hours_value = seconds_to_float_hours(total_seconds)
        if abs(hours_value) < 0.005:
            hours_value = 0.0

        self._hours_result_var.set(f"{hours_value:.2f} h")

    def _regrid_rows(self) -> None:
        for row_widget in self._rows.values():
            row_widget.grid_forget()

        for index, row_id in enumerate(self._row_order):
            self._rows[row_id].grid(row=index, column=0, sticky="ew", pady=(0, 8))

    def _on_row_change(self, row_id: str, value: str) -> None:
        row_widget = self._rows.get(row_id)
        if row_widget is None:
            return

        row_widget.state.value = value
        self.recalculate()

    def _on_row_toggle(self, row_id: str, operator: str) -> None:
        row_widget = self._rows.get(row_id)
        if row_widget is None:
            return

        row_widget.state.operator = operator
        self.recalculate()

    def _on_row_remove(self, row_id: str) -> None:
        self.remove_row(row_id)
