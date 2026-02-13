from __future__ import annotations

import customtkinter as ctk


class PlaceholderView(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, title: str, description: str) -> None:
        super().__init__(master, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        card = ctk.CTkFrame(self, corner_radius=18)
        card.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)

        heading = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=36, weight="bold"),
        )
        heading.grid(row=0, column=0, sticky="w", padx=28, pady=(28, 8))

        subtitle = ctk.CTkLabel(
            card,
            text=description,
            font=ctk.CTkFont(family="Segoe UI", size=18),
            text_color=("#475569", "#94a3b8"),
        )
        subtitle.grid(row=1, column=0, sticky="w", padx=28, pady=(0, 20))
