import tkinter as tk
from tkinter import filedialog, messagebox, font
import os
import re

class MicroCCompiler:
    def __init__(self, root):
        self.root = root
        self.root.title("MicroC Compiler - [Sin archivo]")
        self.root.geometry("1000x650")
        self.root.configure(bg="#1e1e1e")

        self.archivo_actual = None
        self.archivo_modificado = False
        self.modo_edicion = False

        self._construir_menu()
        self._construir_interfaz()
        self._actualizar_estado()

        self.root.protocol("WM_DELETE_WINDOW", self.salir)


    #  MENÚ PRINCIPAL
 
    def _construir_menu(self):
        menubar = tk.Menu(self.root, bg="#2d2d2d", fg="white",
                          activebackground="#0078d4", activeforeground="white",
                          borderwidth=0)

        menu_archivo = tk.Menu(menubar, tearoff=0, bg="#2d2d2d", fg="white",
                               activebackground="#0078d4", activeforeground="white")
        menu_archivo.add_command(label="  Nuevo        Ctrl+N", command=self.nuevo)
        menu_archivo.add_command(label="  Abrir...      Ctrl+A", command=self.abrir)
        menu_archivo.add_command(label="  Guardar      Ctrl+G", command=self.guardar)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="  Salir         Alt+F4", command=self.salir)
        menubar.add_cascade(label=" Archivo ", menu=menu_archivo)

        menu_editar = tk.Menu(menubar, tearoff=0, bg="#2d2d2d", fg="white",
                              activebackground="#0078d4", activeforeground="white")
        menu_editar.add_command(label="  Editar archivo", command=self.editar)
        menubar.add_cascade(label=" Editar ", menu=menu_editar)

        menu_compilar = tk.Menu(menubar, tearoff=0, bg="#2d2d2d", fg="white",
                                activebackground="#0078d4", activeforeground="white")
        menu_compilar.add_command(label="  Compilar      F5", command=self.compilar)
        menubar.add_cascade(label=" Compilar ", menu=menu_compilar)

        menu_ayuda = tk.Menu(menubar, tearoff=0, bg="#2d2d2d", fg="white",
                             activebackground="#0078d4", activeforeground="white")
        menu_ayuda.add_command(label="  Acerca de MicroC", command=self.ayuda)
        menubar.add_cascade(label=" Ayuda ", menu=menu_ayuda)

        self.root.config(menu=menubar)

        self.root.bind("<Control-n>", lambda e: self.nuevo())
        self.root.bind("<Control-a>", lambda e: self.abrir())
        self.root.bind("<Control-g>", lambda e: self.guardar())
        self.root.bind("<F5>",        lambda e: self.compilar())


    #  INTERFAZ PRINCIPAL

    def _construir_interfaz(self):
        toolbar = tk.Frame(self.root, bg="#2d2d2d", height=40)
        toolbar.pack(fill=tk.X, side=tk.TOP)

        btn_style = dict(bg="#6ad4e7", fg="white", relief="flat",
                         padx=10, pady=4, cursor="hand2",
                         activebackground="#005a9e", activeforeground="white",
                         font=("Segoe UI", 9))

        tk.Button(toolbar, text="📄 Nuevo",    command=self.nuevo,    **btn_style).pack(side=tk.LEFT, padx=(8,2), pady=5)
        tk.Button(toolbar, text="📂 Abrir",    command=self.abrir,    **btn_style).pack(side=tk.LEFT, padx=2,    pady=5)
        tk.Button(toolbar, text="💾 Guardar",  command=self.guardar,  **btn_style).pack(side=tk.LEFT, padx=2,    pady=5)
        tk.Button(toolbar, text="✏️ Editar",   command=self.editar,   **btn_style).pack(side=tk.LEFT, padx=2,    pady=5)
        tk.Button(toolbar, text="▶ Compilar", command=self.compilar, **btn_style).pack(side=tk.LEFT, padx=2,    pady=5)
        tk.Button(toolbar, text="🚪 Salir",    command=self.salir,
                  bg="#c0392b", fg="white", relief="flat", padx=10, pady=4,
                  cursor="hand2", activebackground="#922b21", activeforeground="white",
                  font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=8, pady=5)

        labels_frame = tk.Frame(self.root, bg="#1e1e1e")
        labels_frame.pack(fill=tk.X, padx=10, pady=(8, 0))

        tk.Label(labels_frame, text="📝  Código MicroC", bg="#1e1e1e", fg="#9cdcfe",
                 font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Label(labels_frame, text="⚙️  Resultados de Compilación", bg="#1e1e1e", fg="#9cdcfe",
                 font=("Segoe UI", 9, "bold")).pack(side=tk.RIGHT, padx=5)

        panel = tk.Frame(self.root, bg="#1e1e1e")
        panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        codigo_font = font.Font(family="Courier New", size=11)

        frame_codigo = tk.Frame(panel, bg="#252526", bd=1, relief="solid")
        frame_codigo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.numeros_linea = tk.Text(frame_codigo, width=4, bg="#1e1e1e", fg="#858585",
                                     state="disabled", font=codigo_font,
                                     bd=0, padx=4, pady=6, cursor="arrow")
        self.numeros_linea.pack(side=tk.LEFT, fill=tk.Y)

        self.textbox1 = tk.Text(frame_codigo, bg="#1e1e1e", fg="#d4d4d4",
                                insertbackground="white", font=codigo_font,
                                bd=0, padx=6, pady=6, undo=True,
                                state="disabled", wrap="none")
        self.textbox1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll1 = tk.Scrollbar(frame_codigo, command=self._scroll_codigo)
        scroll1.pack(side=tk.RIGHT, fill=tk.Y)
        self.textbox1.config(yscrollcommand=scroll1.set)

        self.textbox1.bind("<KeyRelease>", self._on_texto_cambiado)
        self.textbox1.bind("<MouseWheel>", self._actualizar_numeros)

        frame_resultado = tk.Frame(panel, bg="#252526", bd=1, relief="solid")
        frame_resultado.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.textbox2 = tk.Text(frame_resultado, bg="#0d1117", fg="#58a6ff",
                                font=("Courier New", 10), bd=0, padx=8, pady=8,
                                state="disabled", wrap="word")
        self.textbox2.pack(fill=tk.BOTH, expand=True)

        scroll2 = tk.Scrollbar(frame_resultado, command=self.textbox2.yview)
        scroll2.pack(side=tk.RIGHT, fill=tk.Y)
        self.textbox2.config(yscrollcommand=scroll2.set)

        self.barra_estado = tk.Label(self.root, text="Listo", bg="#007acc",
                                     fg="white", anchor="w", padx=10,
                                     font=("Segoe UI", 8))
        self.barra_estado.pack(fill=tk.X, side=tk.BOTTOM)

        self._log_resultado("╔══════════════════════════════════╗\n"
                            "║     MicroC Compiler v1.0         ║\n"
                            "║  Listo. Abra o cree un archivo.  ║\n"
                            "╚══════════════════════════════════╝\n")

    #  SCROLL SINCRONIZADO

    def _scroll_codigo(self, *args):
        self.textbox1.yview(*args)
        self.numeros_linea.yview(*args)

    def _actualizar_numeros(self, event=None):
        self.numeros_linea.config(state="normal")
        self.numeros_linea.delete("1.0", "end")
        lineas = int(self.textbox1.index("end-1c").split(".")[0])
        numeros = "\n".join(str(i) for i in range(1, lineas + 1))
        self.numeros_linea.insert("1.0", numeros)
        self.numeros_linea.config(state="disabled")

    #  HELPERS

    def _log_resultado(self, texto, limpiar=False):
        self.textbox2.config(state="normal")
        if limpiar:
            self.textbox2.delete("1.0", "end")
        self.textbox2.insert("end", texto + "\n")
        self.textbox2.see("end")
        self.textbox2.config(state="disabled")

    def _set_codigo(self, texto):
        self.textbox1.config(state="normal")
        self.textbox1.delete("1.0", "end")
        self.textbox1.insert("1.0", texto)
        if not self.modo_edicion:
            self.textbox1.config(state="disabled")
        self._actualizar_numeros()

    def _get_codigo(self):
        return self.textbox1.get("1.0", "end-1c")

    def _actualizar_titulo(self):
        if self.archivo_actual:
            modificado = " ●" if self.archivo_modificado else ""
            self.root.title(f"MicroC Compiler - {self.archivo_actual}{modificado}")
        else:
            self.root.title("MicroC Compiler - [Sin archivo]")

    def _actualizar_estado(self):
        modo = "✏️ Edición" if self.modo_edicion else "🔒 Solo lectura"
        archivo = os.path.basename(self.archivo_actual) if self.archivo_actual else "Sin archivo"
        self.barra_estado.config(text=f"  {modo}   |   {archivo}")

    def _on_texto_cambiado(self, event=None):
        self.archivo_modificado = True
        self._actualizar_titulo()
        self._actualizar_numeros()

    def _confirmar_guardar(self):
        if self.archivo_modificado:
            resp = messagebox.askyesnocancel(
                "Cambios sin guardar",
                "El archivo tiene cambios sin guardar.\n¿Desea guardarlos antes de continuar?"
            )
            if resp is None:
                return False
            elif resp:
                self.guardar()
        return True


    #  ANALIZADOR LÉXICO

    def _analizar_lexico(self, codigo):
        # Palabras reservadas de C
        palabras_reservadas = {
            'int', 'float', 'double', 'char', 'void', 'if', 'else', 'while',
            'for', 'do', 'return', 'main', 'printf', 'scanf', 'include',
            'define', 'switch', 'case', 'break', 'continue', 'struct',
            'long', 'short', 'unsigned', 'signed', 'const', 'static'
        }

        operadores_aritmeticos  = set('+-*/%')
        operadores_comparacion  = {'==', '!=', '>=', '<=', '>', '<'}
        operadores_asignacion   = {'=', '+=', '-=', '*=', '/=', '%='}
        operadores_logicos      = {'&&', '||', '!'}
        operadores_incremento   = {'++', '--'}

        # Paso 1: eliminar comentarios de bloque /* */
        codigo_limpio = re.sub(r'/\*.*?\*/', '', codigo, flags=re.DOTALL)
        # Paso 2: eliminar comentarios de línea //
        codigo_limpio = re.sub(r'//.*', '', codigo_limpio)
        # Paso 3: eliminar cadenas de texto entre comillas
        codigo_limpio = re.sub(r'".*?"', '""', codigo_limpio)

        tokens_reservadas   = []
        tokens_identif      = []
        tokens_numeros      = []
        tokens_op_arit      = []
        tokens_op_comp      = []
        tokens_op_asig      = []
        tokens_op_log       = []
        tokens_op_inc       = []
        tokens_simbolos     = []
        errores             = []

        simbolos_validos = set('{}()[];,.')

        # Tokenizar
        patron = r'[A-Za-z_]\w*|\d+\.\d+|\d+|==|!=|>=|<=|\+\+|--|&&|\|\||[+\-*/%=<>!&|]|[{}()\[\];,.]|".*?"|\S'
        lineas = codigo_limpio.split('\n')

        for num_linea, linea in enumerate(lineas, 1):
            tokens = re.findall(patron, linea)
            for token in tokens:
                if token in palabras_reservadas:
                    tokens_reservadas.append(token)
                elif re.fullmatch(r'[A-Za-z_]\w*', token):
                    tokens_identif.append(token)
                elif re.fullmatch(r'\d+(\.\d+)?', token):
                    tokens_numeros.append(token)
                elif token in operadores_incremento:
                    tokens_op_inc.append(token)
                elif token in operadores_comparacion:
                    tokens_op_comp.append(token)
                elif token in operadores_asignacion:
                    tokens_op_asig.append(token)
                elif token in operadores_logicos:
                    tokens_op_log.append(token)
                elif token in operadores_aritmeticos:
                    tokens_op_arit.append(token)
                elif token in simbolos_validos:
                    tokens_simbolos.append(token)
                elif token not in ('"',):
                    errores.append(f"  Línea {num_linea}: símbolo no reconocido '{token}'")

        # Construir reporte
        resultado = []
        resultado.append("-----------------------------------")
        resultado.append("        ANALIZADOR LÉXICO - MicroC    ")
        resultado.append("-----------------------------------")
        resultado.append("")

        resultado.append("📌 PASO 1: Eliminando comentarios...")
        comentarios = len(re.findall(r'//.*|/\*.*?\*/', codigo, flags=re.DOTALL))
        resultado.append(f"  Comentarios eliminados: {comentarios}")

        resultado.append("")
        resultado.append("📌 PASO 2: Eliminando espacios en blanco...")
        espacios = len(re.findall(r'\s+', codigo))
        resultado.append(f"  Grupos de espacios/tabs eliminados: {espacios}")

        resultado.append("")
        resultado.append("📌 PASO 3: Identificando tokens...")
        resultado.append("")

        resultado.append(f"Palabras Reservadas ({len(tokens_reservadas)}):")
        resultado.append(f"  {', '.join(sorted(set(tokens_reservadas))) if tokens_reservadas else 'Ninguna'}")

        resultado.append(f"\nIdentificadores ({len(tokens_identif)}):")
        resultado.append(f"  {', '.join(sorted(set(tokens_identif))) if tokens_identif else 'Ninguno'}")

        resultado.append(f"\n Números ({len(tokens_numeros)}):")
        resultado.append(f"  {', '.join(sorted(set(tokens_numeros))) if tokens_numeros else 'Ninguno'}")

        resultado.append(f"\nOperadores Aritméticos ({len(tokens_op_arit)}):")
        resultado.append(f"  {', '.join(sorted(set(tokens_op_arit))) if tokens_op_arit else 'Ninguno'}")

        resultado.append(f"\nOperadores de Comparación ({len(tokens_op_comp)}):")
        resultado.append(f"  {', '.join(sorted(set(tokens_op_comp))) if tokens_op_comp else 'Ninguno'}")

        resultado.append(f"\nOperadores de Asignación ({len(tokens_op_asig)}):")
        resultado.append(f"  {', '.join(sorted(set(tokens_op_asig))) if tokens_op_asig else 'Ninguno'}")

        resultado.append(f"\nOperadores Lógicos ({len(tokens_op_log)}):")
        resultado.append(f"  {', '.join(sorted(set(tokens_op_log))) if tokens_op_log else 'Ninguno'}")

        resultado.append(f"\nOperadores Incremento/Decremento ({len(tokens_op_inc)}):")
        resultado.append(f"  {', '.join(sorted(set(tokens_op_inc))) if tokens_op_inc else 'Ninguno'}")

        resultado.append(f"\n⬛ Símbolos especiales ({len(tokens_simbolos)}):")
        resultado.append(f"  {', '.join(sorted(set(tokens_simbolos))) if tokens_simbolos else 'Ninguno'}")

        total = (len(tokens_reservadas) + len(tokens_identif) + len(tokens_numeros) +
                 len(tokens_op_arit) + len(tokens_op_comp) + len(tokens_op_asig) +
                 len(tokens_op_log) + len(tokens_op_inc) + len(tokens_simbolos))

        resultado.append("")
        resultado.append("********************************************")
        resultado.append(f"TOTAL DE TOKENS: {total}")

        if errores:
            resultado.append("")
            resultado.append(f"⚠️  SÍMBOLOS NO RECONOCIDOS ({len(errores)}):")
            resultado.extend(errores)
        else:
            resultado.append("¡SIN ERRORES LEXICOS DETECTADOS!.")

        resultado.append("********************************************")

        return "\n".join(resultado)


    #  FUNCIONES PRINCIPALES

    def nuevo(self):
        if not self._confirmar_guardar():
            return
        self.archivo_actual = None
        self.archivo_modificado = False
        self.modo_edicion = True
        self.textbox1.config(state="normal")
        self._set_codigo("")
        self._actualizar_titulo()
        self._actualizar_estado()
        self._log_resultado("── Nuevo archivo creado ──")
        self.textbox1.focus()

    def abrir(self):
        if not self._confirmar_guardar():
            return
        ruta = filedialog.askopenfilename(
            title="Abrir archivo MicroC",
            filetypes=[("Archivos C", "*.c"), ("Todos los archivos", "*.*")]
        )
        if not ruta:
            return
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
            self.archivo_actual = ruta
            self.archivo_modificado = False
            self.modo_edicion = False
            self.textbox1.config(state="normal")
            self._set_codigo(contenido)
            self.textbox1.config(state="disabled")
            self._actualizar_titulo()
            self._actualizar_estado()
            self._log_resultado(f"── Archivo abierto: {ruta} ──")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")

    def guardar(self):
        if not self.archivo_actual:
            ruta = filedialog.asksaveasfilename(
                title="Guardar archivo MicroC",
                defaultextension=".c",
                filetypes=[("Archivos C", "*.c"), ("Todos los archivos", "*.*")]
            )
            if not ruta:
                return
            self.archivo_actual = ruta
        try:
            with open(self.archivo_actual, "w", encoding="utf-8") as f:
                f.write(self._get_codigo())
            self.archivo_modificado = False
            self._actualizar_titulo()
            self._actualizar_estado()
            self._log_resultado(f"── Archivo guardado: {self.archivo_actual} ──")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

    def editar(self):
        self.modo_edicion = True
        self.textbox1.config(state="normal")
        self._actualizar_estado()
        self._log_resultado("── Modo edición activado ──")
        self.textbox1.focus()

    def compilar(self):
        codigo = self._get_codigo().strip()
        if not codigo:
            self._log_resultado("⚠️  No hay código para analizar.", limpiar=True)
            return
        reporte = self._analizar_lexico(codigo)
        self._log_resultado(reporte, limpiar=True)

    def ayuda(self):
        self._log_resultado("══════════════════════════════════════\n"
                            "  AYUDA - MicroC Compiler\n"
                            "──────────────────────────────────────\n"
                            "  Nuevo:    Crear nuevo archivo\n"
                            "  Abrir:    Cargar archivo .C\n"
                            "  Guardar:  Guardar archivo .C\n"
                            "  Editar:   Habilitar edición\n"
                            "  Compilar: Ejecutar análisis léxico\n"
                            "  Salir:    Cerrar aplicación\n"
                            "══════════════════════════════════════", limpiar=True)

    def salir(self):
        if not self._confirmar_guardar():
            return
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MicroCCompiler(root)
    root.mainloop()