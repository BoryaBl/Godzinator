from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from ui.models import TimeRowState
from ui.utils.time_sum_helpers import mask_hhmmss

OnRowChange = Callable[[str, str], None]
OnRowToggle = Callable[[str, str], None]
OnRowRemove = Callable[[str], None]


class TimeRowWidget(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTkBaseClass,
        row_state: TimeRowState,
        on_change: OnRowChange,
        on_toggle: OnRowToggle,
        on_remove: OnRowRemove,
    ) -> None:
        super().__init__(master, fg_color="transparent")

        self.state = row_state
        self._on_change = on_change
        self._on_toggle = on_toggle
        self._on_remove = on_remove

        self.grid_columnconfigure(1, weight=1)

        self._toggle_button = ctk.CTkButton(
            self,
            width=44,
            height=36,
            text=self.state.operator,
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self._toggle_operator,
        )
        self._toggle_button.grid(row=0, column=0, padx=(0, 10), sticky="w")

        self._time_entry = ctk.CTkEntry(
            self,
            placeholder_text="00:00:00",
            height=36,
            font=ctk.CTkFont(family="Segoe UI", size=15),
        )
        self._time_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self._time_entry.bind("<KeyRelease>", self._on_entry_interaction)
        self._time_entry.bind("<FocusOut>", self._on_entry_interaction)

        self._delete_button = ctk.CTkButton(
            self,
            width=36,
            height=36,
            text="X",
            fg_color="transparent",
            border_width=1,
            border_color=("#d1d5db", "#4b5563"),
            hover_color=("#fee2e2", "#7f1d1d"),
            text_color=("#991b1b", "#fecaca"),
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._remove_self,
        )
        self._delete_button.grid(row=0, column=2, sticky="e")

        self._default_entry_border_color = self._time_entry.cget("border_color")
        self._default_entry_border_width = self._time_entry.cget("border_width")

        self._apply_operator_style()
        self._set_validation_state(False)

        if self.state.value:
            self._time_entry.insert(0, self.state.value)

    def _toggle_operator(self) -> None:
        self.state.operator = "-" if self.state.operator == "+" else "+"
        self._apply_operator_style()
        self._on_toggle(self.state.row_id, self.state.operator)

    def _remove_self(self) -> None:
        self._on_remove(self.state.row_id)

    def _on_entry_interaction(self, _: object | None = None) -> None:
        current_value = self._time_entry.get()
        masked_value = mask_hhmmss(current_value)

        if current_value != masked_value:
            self._time_entry.delete(0, "end")
            self._time_entry.insert(0, masked_value)

        self.state.value = masked_value
        self._set_validation_state(self.state.is_started and not self.state.is_complete)
        self._on_change(self.state.row_id, masked_value)

    def _apply_operator_style(self) -> None:
        if self.state.operator == "+":
            self._toggle_button.configure(
                text="+",
                fg_color=("#22c55e", "#15803d"),
                hover_color=("#16a34a", "#166534"),
                text_color="white",
            )
        else:
            self._toggle_button.configure(
                text="-",
                fg_color=("#ef4444", "#dc2626"),
                hover_color=("#dc2626", "#b91c1c"),
                text_color="white",
            )

    def _set_validation_state(self, is_invalid: bool) -> None:
        if is_invalid:
            self._time_entry.configure(border_color=("#dc2626", "#f87171"), border_width=2)
            return

        self._time_entry.configure(
            border_color=self._default_entry_border_color,
            border_width=self._default_entry_border_width,
        )
