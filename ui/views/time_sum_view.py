from __future__ import annotations

import uuid

import customtkinter as ctk

from time_utils import (
    calculate_time_expression,
    calculate_vacation_days,
    seconds_to_float_hours,
    time_to_seconds,
)
from ui.models import TimeRowState
from ui.utils.time_sum_helpers import (
    build_expression_payload,
    format_signed_seconds,
    is_complete_hhmmss,
    mask_hhmmss,
)
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
        self._days_result_var = ctk.StringVar(value="0.00")
        self._daily_norm_var = ctk.StringVar(value="08:00:00")
        self._daily_norm_quick_target = "07:35:00"
        self._clock_copy_after: str | None = None
        self._hours_copy_after: str | None = None

        self._build_rows_panel()
        self._build_results_panel()

        self.add_row()

    def _build_rows_panel(self) -> None:
        panel = ctk.CTkFrame(self, corner_radius=18)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=0)
        panel.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 6))
        header.grid_columnconfigure(0, weight=1)

        heading = ctk.CTkLabel(
            header,
            text="Sumowanie czasu",
            font=ctk.CTkFont(family="Segoe UI", size=30, weight="bold"),
        )
        heading.grid(row=0, column=0, sticky="w")

        norm_frame = ctk.CTkFrame(header, fg_color="transparent")
        norm_frame.grid(row=1, column=0, sticky="w", pady=(8, 0))
        norm_frame.grid_columnconfigure(1, weight=0)

        daily_norm_label = ctk.CTkLabel(
            norm_frame,
            text="Norma dobowa:",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=("#475569", "#94a3b8"),
        )
        daily_norm_label.grid(row=0, column=0, padx=(0, 8), sticky="e")

        self._daily_norm_entry = ctk.CTkEntry(
            norm_frame,
            width=124,
            height=34,
            textvariable=self._daily_norm_var,
            font=ctk.CTkFont(family="Segoe UI", size=14),
        )
        self._daily_norm_entry.grid(row=0, column=1, padx=(0, 8), sticky="e")
        self._daily_norm_entry.bind("<KeyRelease>", self._on_daily_norm_change)
        self._daily_norm_entry.bind("<FocusOut>", self._on_daily_norm_change)

        self._daily_norm_quick_button = ctk.CTkButton(
            norm_frame,
            width=86,
            height=34,
            text=self._daily_norm_quick_target,
            command=self._on_daily_norm_quick_toggle,
        )
        self._daily_norm_quick_button.grid(row=0, column=2, sticky="e")

        self._default_daily_norm_border_color = self._daily_norm_entry.cget("border_color")
        self._default_daily_norm_border_width = self._daily_norm_entry.cget("border_width")

        description = ctk.CTkLabel(
            panel,
            text="Każdy wiersz obsługuje mnożnik, aktywność i opis. Wynik aktualizuje się na żywo.",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=("#475569", "#94a3b8"),
            justify="left",
        )
        description.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 12))
        panel.bind(
            "<Configure>",
            lambda event: description.configure(wraplength=max(event.width - 44, 260)),
            add="+",
        )

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
        self._sync_daily_norm_quick_button()
        self._set_daily_norm_validation_state(False)

    def _build_results_panel(self) -> None:
        panel = ctk.CTkFrame(self, corner_radius=18, width=360)
        panel.grid(row=0, column=1, sticky="ns", padx=(12, 0), pady=0)
        panel.grid_propagate(False)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(7, weight=1)

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

        clock_row = ctk.CTkFrame(panel, fg_color="transparent")
        clock_row.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 10))
        clock_row.grid_columnconfigure(0, weight=1)

        clock_result = ctk.CTkLabel(
            clock_row,
            textvariable=self._clock_result_var,
            width=220,
            anchor="w",
            font=ctk.CTkFont(family="Consolas", size=44, weight="bold"),
        )
        clock_result.grid(row=0, column=0, sticky="w")

        self._copy_clock_button = ctk.CTkButton(
            clock_row,
            text="Kopiuj",
            width=90,
            height=30,
            command=self._copy_clock_result,
        )
        self._copy_clock_button.grid(row=0, column=1, sticky="e", padx=(8, 0))

        hours_title = ctk.CTkLabel(
            panel,
            text="Format dziesiętny",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=("#64748b", "#94a3b8"),
        )
        hours_title.grid(row=3, column=0, sticky="sw", padx=24)

        hours_row = ctk.CTkFrame(panel, fg_color="transparent")
        hours_row.grid(row=4, column=0, sticky="ew", padx=24, pady=(0, 24))
        hours_row.grid_columnconfigure(0, weight=1)

        hours_result = ctk.CTkLabel(
            hours_row,
            textvariable=self._hours_result_var,
            width=220,
            anchor="w",
            font=ctk.CTkFont(family="Consolas", size=32, weight="bold"),
        )
        hours_result.grid(row=0, column=0, sticky="w")

        self._copy_hours_button = ctk.CTkButton(
            hours_row,
            text="Kopiuj",
            width=90,
            height=30,
            command=self._copy_hours_result,
        )
        self._copy_hours_button.grid(row=0, column=1, sticky="e", padx=(8, 0))

        days_title = ctk.CTkLabel(
            panel,
            text="Liczba dni",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=("#64748b", "#94a3b8"),
        )
        days_title.grid(row=5, column=0, sticky="sw", padx=24)

        days_result = ctk.CTkLabel(
            panel,
            textvariable=self._days_result_var,
            width=300,
            anchor="w",
            font=ctk.CTkFont(family="Consolas", size=32, weight="bold"),
        )
        days_result.grid(row=6, column=0, sticky="nw", padx=24, pady=(0, 24))

    def add_row(self) -> None:
        row_id = uuid.uuid4().hex
        row_state = TimeRowState(row_id=row_id, multiplier="1", is_active=True)

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
        times, operators, multipliers, total_seconds = build_expression_payload(ordered_states)
        daily_norm_text = self._daily_norm_var.get()
        daily_norm_invalid = self._is_daily_norm_invalid(daily_norm_text)
        self._set_daily_norm_validation_state(daily_norm_invalid)

        days_value = 0.0
        if not daily_norm_invalid:
            days_value = calculate_vacation_days(total_seconds, daily_norm_text)

        try:
            calculate_time_expression(times, operators, multipliers)
        except Exception as error:
            print(f"[Godzinator] Calculation error: {error}")
            self._set_result_values(0, 0.0)
            return

        self._set_result_values(total_seconds, days_value)

    def _set_result_values(self, total_seconds: int, days_value: float) -> None:
        self._clock_result_var.set(format_signed_seconds(total_seconds))

        hours_value = seconds_to_float_hours(total_seconds)
        if abs(hours_value) < 0.005:
            hours_value = 0.0

        self._hours_result_var.set(f"{hours_value:.2f} h")
        self._days_result_var.set(f"{days_value:.2f}")

    def _on_daily_norm_change(self, _: object | None = None) -> None:
        current_value = self._daily_norm_entry.get()
        masked_value = mask_hhmmss(current_value)

        if current_value != masked_value:
            self._daily_norm_entry.delete(0, "end")
            self._daily_norm_entry.insert(0, masked_value)

        self._daily_norm_var.set(masked_value)
        self._sync_daily_norm_quick_button()
        self.recalculate()

    def _on_daily_norm_quick_toggle(self) -> None:
        self._daily_norm_entry.delete(0, "end")
        self._daily_norm_entry.insert(0, self._daily_norm_quick_target)
        self._daily_norm_var.set(self._daily_norm_quick_target)
        self._sync_daily_norm_quick_button()
        self.recalculate()

    def _sync_daily_norm_quick_button(self) -> None:
        current_value = self._daily_norm_var.get()
        if current_value == "08:00:00":
            self._daily_norm_quick_target = "07:35:00"
        elif current_value == "07:35:00":
            self._daily_norm_quick_target = "08:00:00"
        else:
            self._daily_norm_quick_target = "07:35:00"

        self._daily_norm_quick_button.configure(text=self._daily_norm_quick_target)

    def _set_daily_norm_validation_state(self, is_invalid: bool) -> None:
        if is_invalid:
            self._daily_norm_entry.configure(border_color=("#dc2626", "#f87171"), border_width=2)
            return

        self._daily_norm_entry.configure(
            border_color=self._default_daily_norm_border_color,
            border_width=self._default_daily_norm_border_width,
        )

    def _is_daily_norm_invalid(self, value: str) -> bool:
        if not is_complete_hhmmss(value):
            return True

        try:
            norm_seconds = time_to_seconds(value)
        except ValueError:
            return True

        return norm_seconds <= 0

    def _copy_clock_result(self) -> None:
        self._copy_to_clipboard(self._clock_result_var.get())
        self._show_copy_feedback("clock")

    def _copy_hours_result(self) -> None:
        self._copy_to_clipboard(self._hours_result_var.get())
        self._show_copy_feedback("hours")

    def _copy_to_clipboard(self, text: str) -> None:
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update_idletasks()

    def _show_copy_feedback(self, target: str) -> None:
        if target == "clock":
            button = self._copy_clock_button
            if self._clock_copy_after is not None:
                try:
                    self.after_cancel(self._clock_copy_after)
                except Exception:
                    pass
            button.configure(text="Skopiowano!")

            def _reset_clock_button() -> None:
                button.configure(text="Kopiuj")
                self._clock_copy_after = None

            self._clock_copy_after = self.after(1500, _reset_clock_button)
            return

        button = self._copy_hours_button
        if self._hours_copy_after is not None:
            try:
                self.after_cancel(self._hours_copy_after)
            except Exception:
                pass
        button.configure(text="Skopiowano!")

        def _reset_hours_button() -> None:
            button.configure(text="Kopiuj")
            self._hours_copy_after = None

        self._hours_copy_after = self.after(1500, _reset_hours_button)

    def _regrid_rows(self) -> None:
        for row_widget in self._rows.values():
            row_widget.grid_forget()

        for index, row_id in enumerate(self._row_order):
            self._rows[row_id].grid(row=index, column=0, sticky="ew", pady=(0, 8))

    def _on_row_change(self, row_id: str) -> None:
        if row_id in self._rows:
            self.recalculate()

    def _on_row_toggle(self, row_id: str) -> None:
        if row_id in self._rows:
            self.recalculate()

    def _on_row_remove(self, row_id: str) -> None:
        self.remove_row(row_id)
