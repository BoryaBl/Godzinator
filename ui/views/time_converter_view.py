from __future__ import annotations

from collections.abc import Iterable

import customtkinter as ctk

from time_utils import seconds_to_time
from ui.utils.time_converter_helpers import (
    format_float_compact,
    parse_complete_clock_to_seconds,
    parse_non_negative_float,
    round_half_up_non_negative,
    sanitize_decimal_input,
)
from ui.utils.time_sum_helpers import mask_hhmmss


class TimeConverterView(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass) -> None:
        super().__init__(master, fg_color="transparent")

        self._is_updating = False

        self._seconds_var = ctk.StringVar(value="")
        self._minutes_var = ctk.StringVar(value="")
        self._hours_var = ctk.StringVar(value="")
        self._clock_var = ctk.StringVar(value="")

        self._entries: dict[str, ctk.CTkEntry] = {}
        self._entry_default_border: dict[str, tuple[str | tuple[str, str], int]] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_ui()

    def _build_ui(self) -> None:
        card = ctk.CTkFrame(self, corner_radius=18)
        card.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        card.grid_columnconfigure(0, weight=0)
        card.grid_columnconfigure(1, weight=1)
        card.grid_rowconfigure(6, weight=1)

        heading = ctk.CTkLabel(
            card,
            text="Konwerter czasu",
            font=ctk.CTkFont(family="Segoe UI", size=34, weight="bold"),
        )
        heading.grid(row=0, column=0, columnspan=2, sticky="w", padx=28, pady=(24, 8))

        description = ctk.CTkLabel(
            card,
            text="Wpisz wartość w dowolnym polu, a pozostałe zostaną przeliczone automatycznie.",
            font=ctk.CTkFont(family="Segoe UI", size=15),
            text_color=("#475569", "#94a3b8"),
            justify="left",
        )
        description.grid(row=1, column=0, columnspan=2, sticky="w", padx=28, pady=(0, 20))

        self._create_row(
            card,
            row=2,
            key="seconds",
            label="Sekundy",
            variable=self._seconds_var,
            handler=self._on_seconds_change,
        )
        self._create_row(
            card,
            row=3,
            key="minutes",
            label="Minuty",
            variable=self._minutes_var,
            handler=self._on_minutes_change,
        )
        self._create_row(
            card,
            row=4,
            key="hours",
            label="Godziny dziesiętne",
            variable=self._hours_var,
            handler=self._on_hours_change,
        )
        self._create_row(
            card,
            row=5,
            key="clock",
            label="Format zegarowy (HH:MM:SS)",
            variable=self._clock_var,
            handler=self._on_clock_change,
        )

    def _create_row(
        self,
        card: ctk.CTkFrame,
        row: int,
        key: str,
        label: str,
        variable: ctk.StringVar,
        handler,
    ) -> None:
        label_widget = ctk.CTkLabel(
            card,
            text=label,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
        )
        label_widget.grid(row=row, column=0, sticky="w", padx=(28, 14), pady=8)

        entry = ctk.CTkEntry(
            card,
            textvariable=variable,
            height=38,
            font=ctk.CTkFont(family="Segoe UI", size=15),
        )
        entry.grid(row=row, column=1, sticky="ew", padx=(0, 28), pady=8)
        entry.bind("<KeyRelease>", handler)
        entry.bind("<FocusOut>", handler)

        border_color = entry.cget("border_color")
        border_width = entry.cget("border_width")

        self._entries[key] = entry
        self._entry_default_border[key] = (border_color, border_width)

    def _set_entry_invalid(self, key: str, is_invalid: bool) -> None:
        entry = self._entries[key]
        if is_invalid:
            entry.configure(border_color=("#dc2626", "#f87171"), border_width=2)
            return

        border_color, border_width = self._entry_default_border[key]
        entry.configure(border_color=border_color, border_width=border_width)

    def _clear_all_validation_states(self) -> None:
        for key in self._entries:
            self._set_entry_invalid(key, False)

    def _set_vars_programmatically(self, updates: Iterable[tuple[ctk.StringVar, str]]) -> None:
        self._is_updating = True
        try:
            for variable, value in updates:
                variable.set(value)
        finally:
            self._is_updating = False

    def _clear_all_fields(self) -> None:
        self._set_vars_programmatically(
            [
                (self._seconds_var, ""),
                (self._minutes_var, ""),
                (self._hours_var, ""),
                (self._clock_var, ""),
            ]
        )
        self._clear_all_validation_states()

    def _update_all_fields(self, base_seconds: int, preserve: tuple[str, str] | None = None) -> None:
        values = {
            "seconds": str(base_seconds),
            "minutes": format_float_compact(base_seconds / 60),
            "hours": format_float_compact(base_seconds / 3600),
            "clock": seconds_to_time(base_seconds),
        }

        if preserve is not None:
            preserve_key, preserve_value = preserve
            if preserve_key in values:
                values[preserve_key] = preserve_value

        updates = [
            (self._seconds_var, values["seconds"]),
            (self._minutes_var, values["minutes"]),
            (self._hours_var, values["hours"]),
            (self._clock_var, values["clock"]),
        ]
        self._set_vars_programmatically(updates)
        self._clear_all_validation_states()

    def _handle_numeric_input(self, key: str, variable: ctk.StringVar, factor: int) -> None:
        if self._is_updating:
            return

        raw = variable.get()
        sanitized, had_invalid_chars = sanitize_decimal_input(raw)

        if raw != sanitized:
            self._set_vars_programmatically([(variable, sanitized)])
            self.after_idle(lambda key=key: self._entries[key].icursor("end"))

        if sanitized == "":
            self._clear_all_fields()
            self._set_entry_invalid(key, had_invalid_chars)
            return

        parsed_value = parse_non_negative_float(sanitized)
        if parsed_value is None:
            self._set_entry_invalid(key, True)
            return

        base_seconds = round_half_up_non_negative(parsed_value * factor)
        self._update_all_fields(base_seconds, preserve=(key, sanitized))

        if had_invalid_chars:
            self._set_entry_invalid(key, True)

    def _on_seconds_change(self, _: object | None = None) -> None:
        self._handle_numeric_input("seconds", self._seconds_var, 1)

    def _on_minutes_change(self, _: object | None = None) -> None:
        self._handle_numeric_input("minutes", self._minutes_var, 60)

    def _on_hours_change(self, _: object | None = None) -> None:
        self._handle_numeric_input("hours", self._hours_var, 3600)

    def _on_clock_change(self, _: object | None = None) -> None:
        if self._is_updating:
            return

        raw = self._clock_var.get()
        masked = mask_hhmmss(raw)
        had_invalid_chars = raw != masked

        if raw != masked:
            self._set_vars_programmatically([(self._clock_var, masked)])
            self.after_idle(lambda: self._entries["clock"].icursor("end"))

        if masked == "":
            self._clear_all_fields()
            self._set_entry_invalid("clock", had_invalid_chars)
            return

        base_seconds = parse_complete_clock_to_seconds(masked)
        if base_seconds is None:
            self._set_entry_invalid("clock", True)
            return

        self._update_all_fields(base_seconds)
        self.after_idle(lambda: self._entries["clock"].icursor("end"))

        if had_invalid_chars:
            self._set_entry_invalid("clock", True)
