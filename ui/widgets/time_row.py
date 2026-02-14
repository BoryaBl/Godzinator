from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from ui.models import TimeRowState
from ui.utils.time_sum_helpers import (
    is_valid_multiplier,
    mask_hhmmss,
    sanitize_multiplier_text,
)

OnRowChange = Callable[[str], None]
OnRowToggle = Callable[[str], None]
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

        self.grid_columnconfigure(4, weight=2)
        self.grid_columnconfigure(5, weight=1)

        self._active_var = ctk.BooleanVar(value=self.state.is_active)
        self._active_checkbox = ctk.CTkCheckBox(
            self,
            text="",
            width=24,
            variable=self._active_var,
            command=self._on_active_change,
        )
        self._active_checkbox.grid(row=0, column=0, padx=(0, 8), sticky="w")

        self._toggle_button = ctk.CTkButton(
            self,
            width=44,
            height=36,
            text=self.state.operator,
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self._toggle_operator,
        )
        self._toggle_button.grid(row=0, column=1, padx=(0, 8), sticky="w")

        self._multiplier_entry = ctk.CTkEntry(
            self,
            width=72,
            height=36,
            font=ctk.CTkFont(family="Segoe UI", size=14),
        )
        self._multiplier_entry.grid(row=0, column=2, padx=(0, 8), sticky="w")
        self._multiplier_entry.bind("<KeyRelease>", self._on_multiplier_interaction)
        self._multiplier_entry.bind("<FocusOut>", self._on_multiplier_interaction)

        multiply_label = ctk.CTkLabel(
            self,
            text="x",
            width=16,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=("#64748b", "#94a3b8"),
        )
        multiply_label.grid(row=0, column=3, padx=(0, 8), sticky="w")

        self._time_entry = ctk.CTkEntry(
            self,
            placeholder_text="00:00:00",
            height=36,
            font=ctk.CTkFont(family="Segoe UI", size=15),
        )
        self._time_entry.grid(row=0, column=4, sticky="ew", padx=(0, 8))
        self._time_entry.bind("<KeyRelease>", self._on_time_interaction)
        self._time_entry.bind("<FocusOut>", self._on_time_interaction)

        self._description_entry = ctk.CTkEntry(
            self,
            placeholder_text="Opis",
            height=36,
            font=ctk.CTkFont(family="Segoe UI", size=14),
        )
        self._description_entry.grid(row=0, column=5, sticky="ew", padx=(0, 8))
        self._description_entry.bind("<KeyRelease>", self._on_description_change)
        self._description_entry.bind("<FocusOut>", self._on_description_change)

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
        self._delete_button.grid(row=0, column=6, sticky="e")

        self._default_time_entry_border_color = self._time_entry.cget("border_color")
        self._default_time_entry_border_width = self._time_entry.cget("border_width")
        self._default_multiplier_border_color = self._multiplier_entry.cget("border_color")
        self._default_multiplier_border_width = self._multiplier_entry.cget("border_width")

        self._multiplier_entry.insert(0, self.state.multiplier)

        if self.state.value:
            self._time_entry.insert(0, self.state.value)

        if self.state.description:
            self._description_entry.insert(0, self.state.description)

        self._apply_operator_style()
        self._apply_active_visual_state()
        self._refresh_validation_state()

    def _toggle_operator(self) -> None:
        self.state.operator = "-" if self.state.operator == "+" else "+"
        self._apply_operator_style()
        self._apply_active_visual_state()
        self._on_toggle(self.state.row_id)

    def _remove_self(self) -> None:
        self._on_remove(self.state.row_id)

    def _on_active_change(self) -> None:
        self.state.is_active = bool(self._active_var.get())
        self._apply_active_visual_state()
        self._refresh_validation_state()
        self._on_change(self.state.row_id)

    def _on_time_interaction(self, _: object | None = None) -> None:
        current_value = self._time_entry.get()
        masked_value = mask_hhmmss(current_value)

        if current_value != masked_value:
            self._time_entry.delete(0, "end")
            self._time_entry.insert(0, masked_value)

        self.state.value = masked_value
        self._refresh_validation_state()
        self._on_change(self.state.row_id)

    def _on_multiplier_interaction(self, _: object | None = None) -> None:
        current_value = self._multiplier_entry.get()
        sanitized_value = sanitize_multiplier_text(current_value)

        if current_value != sanitized_value:
            self._multiplier_entry.delete(0, "end")
            self._multiplier_entry.insert(0, sanitized_value)

        self.state.multiplier = sanitized_value
        self._refresh_validation_state()
        self._on_change(self.state.row_id)

    def _on_description_change(self, _: object | None = None) -> None:
        self.state.description = self._description_entry.get()

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

    def _apply_active_visual_state(self) -> None:
        if self.state.is_active:
            self.configure(fg_color="transparent")
            self._description_entry.configure(text_color=("#111827", "#f3f4f6"))
            self._time_entry.configure(text_color=("#111827", "#f3f4f6"))
            self._multiplier_entry.configure(text_color=("#111827", "#f3f4f6"))
            self._delete_button.configure(text_color=("#991b1b", "#fecaca"))
            return

        self.configure(fg_color=("#f8fafc", "#1f2937"))
        self._description_entry.configure(text_color=("#94a3b8", "#94a3b8"))
        self._time_entry.configure(text_color=("#94a3b8", "#94a3b8"))
        self._multiplier_entry.configure(text_color=("#94a3b8", "#94a3b8"))
        self._delete_button.configure(text_color=("#94a3b8", "#94a3b8"))

    def _refresh_validation_state(self) -> None:
        time_invalid = self.state.is_active and self.state.is_started and not self.state.is_complete
        multiplier_invalid = self.state.is_active and not is_valid_multiplier(self.state.multiplier)

        self._set_time_validation_state(time_invalid)
        self._set_multiplier_validation_state(multiplier_invalid)

    def _set_time_validation_state(self, is_invalid: bool) -> None:
        if is_invalid:
            self._time_entry.configure(border_color=("#dc2626", "#f87171"), border_width=2)
            return

        self._time_entry.configure(
            border_color=self._default_time_entry_border_color,
            border_width=self._default_time_entry_border_width,
        )

    def _set_multiplier_validation_state(self, is_invalid: bool) -> None:
        if is_invalid:
            self._multiplier_entry.configure(border_color=("#dc2626", "#f87171"), border_width=2)
            return

        self._multiplier_entry.configure(
            border_color=self._default_multiplier_border_color,
            border_width=self._default_multiplier_border_width,
        )
