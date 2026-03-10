"""
╔══════════════════════════════════════╗
║         GUAYABITA — DADOS            ║
║  2 dados · acumula puntos · tkinter  ║
╚══════════════════════════════════════╝

Reglas:
  - Lanza 2 dados cada turno
  - Se suman los valores al puntaje total
  - Para cuando quieras y guarda tu récord

Requisitos:
  Python 3.x con tkinter
  Linux:   sudo apt-get install python3-tk
  macOS:   brew install python-tk
  Windows: incluido con Python

Ejecutar:
  python guayabita.py
"""

import tkinter as tk
import random
import json
import os
import time

# ──────────────────────────────────────────────
#  CONSTANTES
# ──────────────────────────────────────────────
ARCHIVO_HS = os.path.join(os.path.expanduser("~"), ".guayabita_hs.json")

C = {
    "bg":        "#0d1117",
    "bg2":       "#161b22",
    "bg3":       "#21262d",
    "border":    "#30363d",
    "fg":        "#e6edf3",
    "fg2":       "#8b949e",
    "accent":    "#58a6ff",
    "green":     "#3fb950",
    "yellow":    "#e3b341",
    "red":       "#f85149",
    "dado_bg":   "#21262d",
    "dado_brd":  "#30363d",
    "dado_dot":  "#e6edf3",
    "btn_pri":   "#238636",
    "btn_sec":   "#21262d",
    "btn_red":   "#b62324",
}

PUNTOS_CARA = {
    1: [(36, 36)],
    2: [(18, 18), (54, 54)],
    3: [(18, 18), (36, 36), (54, 54)],
    4: [(18, 18), (54, 18), (18, 54), (54, 54)],
    5: [(18, 18), (54, 18), (36, 36), (18, 54), (54, 54)],
    6: [(18, 16), (54, 16), (18, 36), (54, 36), (18, 56), (54, 56)],
}


# ──────────────────────────────────────────────
#  HIGHSCORE
# ──────────────────────────────────────────────
def cargar_hs() -> int:
    try:
        with open(ARCHIVO_HS) as f:
            return json.load(f).get("hs", 0)
    except Exception:
        return 0

def guardar_hs(pts: int):
    with open(ARCHIVO_HS, "w") as f:
        json.dump({"hs": pts}, f)


# ──────────────────────────────────────────────
#  APLICACIÓN
# ──────────────────────────────────────────────
class Guayabita:
    def __init__(self, root: tk.Tk):
        self.root     = root
        self.root.title("🎲 Guayabita")
        self.root.configure(bg=C["bg"])
        self.root.resizable(False, False)

        self.hs       = cargar_hs()
        self.puntaje  = 0
        self.rondas   = 0
        self.dados    = [1, 1]
        self.animando = False
        self.historial= []   # lista de (d1, d2, suma)

        self._construir_ui()
        self.root.bind("<Return>", lambda e: self._lanzar())
        self.root.bind("<Escape>", lambda e: self._terminar())

    # ── UI ────────────────────────────────────
    def _construir_ui(self):
        # ── Header ───────────────────────────
        hdr = tk.Frame(self.root, bg=C["bg2"], pady=10, padx=20)
        hdr.pack(fill="x")

        tk.Label(hdr, text="🎲 GUAYABITA",
                 font=("Courier New", 15, "bold"),
                 bg=C["bg2"], fg=C["yellow"]).pack(side="left")

        self.lbl_hs = tk.Label(
            hdr, text=f"🏆 {self.hs}",
            font=("Courier New", 11),
            bg=C["bg2"], fg=C["yellow"]
        )
        self.lbl_hs.pack(side="right")

        # ── Puntaje grande ────────────────────
        pframe = tk.Frame(self.root, bg=C["bg"], pady=20)
        pframe.pack()

        tk.Label(pframe, text="PUNTAJE",
                 font=("Courier New", 10),
                 bg=C["bg"], fg=C["fg2"]).pack()

        self.lbl_puntaje = tk.Label(
            pframe, text="0",
            font=("Courier New", 54, "bold"),
            bg=C["bg"], fg=C["accent"]
        )
        self.lbl_puntaje.pack()

        self.lbl_rondas = tk.Label(
            pframe, text="Ronda 0",
            font=("Courier New", 10),
            bg=C["bg"], fg=C["fg2"]
        )
        self.lbl_rondas.pack()

        # ── Dados ─────────────────────────────
        dframe = tk.Frame(self.root, bg=C["bg"], pady=10)
        dframe.pack()

        self.canvas_dados = []
        for i in range(2):
            cv = tk.Canvas(
                dframe, width=100, height=100,
                bg=C["dado_bg"],
                highlightthickness=3,
                highlightbackground=C["dado_brd"]
            )
            cv.pack(side="left", padx=20)
            self.canvas_dados.append(cv)

        self._dibujar_dados()

        # ── Resultado del lanzamiento ─────────
        self.lbl_resultado = tk.Label(
            self.root, text="Presiona LANZAR para comenzar",
            font=("Courier New", 11),
            bg=C["bg"], fg=C["fg2"]
        )
        self.lbl_resultado.pack(pady=(8, 4))

        # ── Botones ───────────────────────────
        bframe = tk.Frame(self.root, bg=C["bg"], pady=10)
        bframe.pack()

        self.btn_lanzar = tk.Button(
            bframe, text="🎲  LANZAR",
            font=("Courier New", 13, "bold"),
            bg=C["btn_pri"], fg="#ffffff",
            activebackground="#2ea043", activeforeground="#ffffff",
            relief="flat", cursor="hand2",
            padx=28, pady=10,
            command=self._lanzar
        )
        self.btn_lanzar.pack(side="left", padx=10)

        self.btn_parar = tk.Button(
            bframe, text="🛑  PARAR",
            font=("Courier New", 13, "bold"),
            bg=C["btn_red"], fg="#ffffff",
            activebackground="#ff6b6b", activeforeground="#ffffff",
            relief="flat", cursor="hand2",
            padx=28, pady=10,
            command=self._terminar,
            state="disabled"
        )
        self.btn_parar.pack(side="left", padx=10)

        # ── Separador ─────────────────────────
        tk.Frame(self.root, bg=C["border"], height=1).pack(
            fill="x", padx=16, pady=(14, 0))

        # ── Historial ─────────────────────────
        hst_frame = tk.Frame(self.root, bg=C["bg"], padx=16, pady=8)
        hst_frame.pack(fill="x")

        tk.Label(hst_frame, text="HISTORIAL DE RONDAS",
                 font=("Courier New", 9, "bold"),
                 bg=C["bg"], fg=C["fg2"]).pack(anchor="w")

        # Canvas con scroll
        self.canvas_hst = tk.Canvas(
            hst_frame, height=160, bg=C["bg2"],
            highlightthickness=1,
            highlightbackground=C["border"]
        )
        sb = ttk_scrollbar = tk.Scrollbar(
            hst_frame, orient="vertical",
            command=self.canvas_hst.yview
        )
        self.frame_hst = tk.Frame(self.canvas_hst, bg=C["bg2"])
        self.frame_hst.bind(
            "<Configure>",
            lambda e: self.canvas_hst.configure(
                scrollregion=self.canvas_hst.bbox("all"))
        )
        self.canvas_hst.create_window((0, 0), window=self.frame_hst, anchor="nw")
        self.canvas_hst.configure(yscrollcommand=sb.set)
        self.canvas_hst.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # ── Atajos ────────────────────────────
        tk.Label(
            self.root,
            text="[ENTER] Lanzar   [ESC] Parar",
            font=("Courier New", 8),
            bg=C["bg"], fg=C["fg2"]
        ).pack(pady=8)

    # ── DADOS ─────────────────────────────────
    def _dibujar_dados(self):
        for cv, val in zip(self.canvas_dados, self.dados):
            cv.delete("all")
            for px, py in PUNTOS_CARA[val]:
                cv.create_oval(
                    px - 9, py - 9, px + 9, py + 9,
                    fill=C["dado_dot"], outline=""
                )

    # ── LANZAR ────────────────────────────────
    def _lanzar(self):
        if self.animando:
            return
        self.animando = True
        self.btn_lanzar.configure(state="disabled")
        self.btn_parar.configure(state="disabled")
        self._animar(pasos=10)

    def _animar(self, pasos: int):
        if pasos > 0:
            self.dados = [random.randint(1, 6), random.randint(1, 6)]
            self._dibujar_dados()
            self.root.after(55, lambda: self._animar(pasos - 1))
        else:
            self._finalizar_lanzamiento()

    def _finalizar_lanzamiento(self):
        d1, d2   = self.dados
        suma     = d1 + d2
        self.puntaje += suma
        self.rondas  += 1
        self.historial.append((d1, d2, suma))

        # Highlight color del resultado
        color = C["green"] if suma >= 8 else C["fg"]

        self.lbl_puntaje.configure(text=str(self.puntaje))
        self.lbl_rondas.configure(text=f"Ronda {self.rondas}")
        self.lbl_resultado.configure(
            text=f"Dados: {d1} + {d2} = {suma} pts  →  total {self.puntaje}",
            fg=color
        )

        # Borde verde/rojo según resultado
        brd = C["green"] if suma >= 8 else C["accent"]
        for cv in self.canvas_dados:
            cv.configure(highlightbackground=brd)

        self._agregar_historial(d1, d2, suma)

        self.animando = False
        self.btn_lanzar.configure(state="normal")
        self.btn_parar.configure(state="normal")

    # ── HISTORIAL ─────────────────────────────
    def _agregar_historial(self, d1: int, d2: int, suma: int):
        fila = tk.Frame(self.frame_hst, bg=C["bg2"], pady=3, padx=10)
        fila.pack(fill="x", pady=1)

        tk.Label(fila,
                 text=f"#{self.rondas:>3}",
                 font=("Courier New", 9),
                 bg=C["bg2"], fg=C["fg2"],
                 width=4).pack(side="left")

        tk.Label(fila,
                 text=f"  [{d1}] + [{d2}]",
                 font=("Courier New", 10, "bold"),
                 bg=C["bg2"], fg=C["fg"]).pack(side="left")

        color = C["green"] if suma >= 8 else C["fg2"]
        tk.Label(fila,
                 text=f"= {suma:>2} pts",
                 font=("Courier New", 10),
                 bg=C["bg2"], fg=color).pack(side="left", padx=8)

        tk.Label(fila,
                 text=f"acum: {self.puntaje}",
                 font=("Courier New", 9),
                 bg=C["bg2"], fg=C["fg2"]).pack(side="right")

        # Auto-scroll al final
        self.canvas_hst.update_idletasks()
        self.canvas_hst.yview_moveto(1.0)

    # ── TERMINAR ──────────────────────────────
    def _terminar(self):
        if self.rondas == 0:
            return

        nuevo_hs = False
        if self.puntaje > self.hs:
            self.hs = self.puntaje
            guardar_hs(self.hs)
            nuevo_hs = True
            self.lbl_hs.configure(text=f"🏆 {self.hs}")

        # Ventana resultado
        dlg = tk.Toplevel(self.root)
        dlg.title("¡Juego terminado!")
        dlg.configure(bg=C["bg"])
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.geometry("340x280")
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width()  - 340) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 280) // 2
        dlg.geometry(f"+{x}+{y}")

        tk.Label(dlg, text="🎲", font=("", 44),
                 bg=C["bg"]).pack(pady=(18, 4))

        tk.Label(dlg, text="¡PARTIDA TERMINADA!",
                 font=("Courier New", 14, "bold"),
                 bg=C["bg"], fg=C["yellow"]).pack()

        tk.Label(dlg, text=f"Puntaje final: {self.puntaje}",
                 font=("Courier New", 16, "bold"),
                 bg=C["bg"], fg=C["accent"]).pack(pady=6)

        tk.Label(dlg, text=f"Rondas jugadas: {self.rondas}",
                 font=("Courier New", 10),
                 bg=C["bg"], fg=C["fg2"]).pack()

        prom = self.puntaje / self.rondas if self.rondas else 0
        tk.Label(dlg, text=f"Promedio por ronda: {prom:.1f} pts",
                 font=("Courier New", 10),
                 bg=C["bg"], fg=C["fg2"]).pack()

        if nuevo_hs:
            tk.Label(dlg, text="🏆 ¡Nuevo récord personal!",
                     font=("Courier New", 11, "bold"),
                     bg=C["bg"], fg=C["green"]).pack(pady=6)
        else:
            tk.Label(dlg, text=f"Récord: {self.hs} pts",
                     font=("Courier New", 10),
                     bg=C["bg"], fg=C["fg2"]).pack(pady=4)

        def jugar_nuevo():
            dlg.destroy()
            self.puntaje   = 0
            self.rondas    = 0
            self.dados     = [1, 1]
            self.historial = []
            self.lbl_puntaje.configure(text="0")
            self.lbl_rondas.configure(text="Ronda 0")
            self.lbl_resultado.configure(
                text="Presiona LANZAR para comenzar", fg=C["fg2"])
            for cv in self.canvas_dados:
                cv.configure(highlightbackground=C["dado_brd"])
            self._dibujar_dados()
            self.btn_parar.configure(state="disabled")
            for w in self.frame_hst.winfo_children():
                w.destroy()

        tk.Button(
            dlg, text="↺  Jugar de nuevo",
            font=("Courier New", 11, "bold"),
            bg=C["btn_pri"], fg="#ffffff",
            activebackground="#2ea043",
            relief="flat", cursor="hand2",
            padx=20, pady=8,
            command=jugar_nuevo
        ).pack(pady=14)


# ──────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────
def main():
    root = tk.Tk()
    root.geometry("480x660")
    app = Guayabita(root)
    root.mainloop()

if __name__ == "__main__":
    main()
