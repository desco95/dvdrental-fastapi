#!/usr/bin/env python3
"""
DVD Rental Desktop Application
Aplicación de escritorio para gestionar rentas de DVDs
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
from datetime import datetime
from typing import Optional, Dict, List

class DVDRentalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DVD Rental Manager")
        self.root.geometry("1200x800")
        
        # Configuración API
        self.api_url = tk.StringVar(value="http://localhost:8000")
        self.connected = False
        
        # Configurar estilo
        self.setup_style()
        
        # Crear interfaz
        self.create_widgets()
        
        # Probar conexión inicial
        self.test_connection()
    
    def setup_style(self):
        """Configurar estilos de la aplicación"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores
        style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
    
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar conexión
        self.create_connection_frame(main_frame)
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Crear pestañas
        self.create_films_tab()
        self.create_customers_tab()
        self.create_rentals_tab()
        self.create_reports_tab()
        
        # Configurar redimensionamiento
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
    
    def create_connection_frame(self, parent):
        """Frame de configuración de conexión"""
        conn_frame = ttk.LabelFrame(parent, text="Conexión API", padding="10")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(conn_frame, text="URL:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(conn_frame, textvariable=self.api_url, width=40).grid(row=0, column=1, padx=5)
        
        ttk.Button(conn_frame, text="Probar Conexión", 
                  command=self.test_connection).grid(row=0, column=2, padx=5)
        
        self.status_label = ttk.Label(conn_frame, text="No conectado", style='Error.TLabel')
        self.status_label.grid(row=0, column=3, padx=10)
    
    def create_films_tab(self):
        """Pestaña de películas"""
        films_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(films_frame, text="Películas")
        
        # Búsqueda
        search_frame = ttk.Frame(films_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(search_frame, text="Buscar:").grid(row=0, column=0)
        self.film_search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.film_search_var, width=30).grid(row=0, column=1, padx=5)
        ttk.Button(search_frame, text="Buscar", command=self.search_films).grid(row=0, column=2)
        ttk.Button(search_frame, text="Listar Todos", command=self.list_all_films).grid(row=0, column=3, padx=5)
        
        # Treeview
        columns = ('ID', 'Título', 'Año', 'Duración', 'Tarifa', 'Rating')
        self.films_tree = ttk.Treeview(films_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.films_tree.heading(col, text=col)
            self.films_tree.column(col, width=100)
        
        self.films_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(films_frame, orient=tk.VERTICAL, command=self.films_tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.films_tree.configure(yscrollcommand=scrollbar.set)
        
        films_frame.columnconfigure(0, weight=1)
        films_frame.rowconfigure(1, weight=1)
    
    def create_customers_tab(self):
        """Pestaña de clientes"""
        customers_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(customers_frame, text="Clientes")
        
        # Botones
        btn_frame = ttk.Frame(customers_frame)
        btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(btn_frame, text="Listar Clientes", 
                  command=self.list_customers).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Ver Detalles", 
                  command=self.view_customer_details).grid(row=0, column=1, padx=5)
        
        # Treeview
        columns = ('ID', 'Nombre', 'Apellido', 'Email', 'Activo')
        self.customers_tree = ttk.Treeview(customers_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.customers_tree.heading(col, text=col)
            self.customers_tree.column(col, width=150)
        
        self.customers_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(customers_frame, orient=tk.VERTICAL, command=self.customers_tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.customers_tree.configure(yscrollcommand=scrollbar.set)
        
        customers_frame.columnconfigure(0, weight=1)
        customers_frame.rowconfigure(1, weight=1)
    
    def create_rentals_tab(self):
        """Pestaña de rentas"""
        rentals_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(rentals_frame, text="Rentas")
        
        # Frame superior para crear renta
        create_frame = ttk.LabelFrame(rentals_frame, text="Nueva Renta", padding="10")
        create_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(create_frame, text="ID Cliente:").grid(row=0, column=0, sticky=tk.W)
        self.rental_customer_id = tk.StringVar()
        ttk.Entry(create_frame, textvariable=self.rental_customer_id, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(create_frame, text="ID Película:").grid(row=0, column=2, padx=(10,0), sticky=tk.W)
        self.rental_film_id = tk.StringVar()
        ttk.Entry(create_frame, textvariable=self.rental_film_id, width=10).grid(row=0, column=3, padx=5)
        
        ttk.Label(create_frame, text="ID Staff:").grid(row=0, column=4, padx=(10,0), sticky=tk.W)
        self.rental_staff_id = tk.StringVar(value="1")
        ttk.Entry(create_frame, textvariable=self.rental_staff_id, width=10).grid(row=0, column=5, padx=5)
        
        ttk.Button(create_frame, text="Crear Renta", 
                  command=self.create_rental).grid(row=0, column=6, padx=10)
        
        # Botones de acción
        btn_frame = ttk.Frame(rentals_frame)
        btn_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(btn_frame, text="Listar Rentas", 
                  command=self.list_rentals).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Devolver", 
                  command=self.return_rental).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Cancelar", 
                  command=self.cancel_rental).grid(row=0, column=2, padx=5)
        
        # Treeview
        columns = ('ID', 'Película', 'Cliente', 'Fecha Renta', 'Fecha Dev.', 'Staff')
        self.rentals_tree = ttk.Treeview(rentals_frame, columns=columns, show='headings', height=18)
        
        for col in columns:
            self.rentals_tree.heading(col, text=col)
            self.rentals_tree.column(col, width=150)
        
        self.rentals_tree.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(rentals_frame, orient=tk.VERTICAL, command=self.rentals_tree.yview)
        scrollbar.grid(row=2, column=1, sticky=(tk.N, tk.S))
        self.rentals_tree.configure(yscrollcommand=scrollbar.set)
        
        rentals_frame.columnconfigure(0, weight=1)
        rentals_frame.rowconfigure(2, weight=1)
    
    def create_reports_tab(self):
        """Pestaña de reportes"""
        reports_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(reports_frame, text="Reportes")
        
        # Botones
        btn_frame = ttk.Frame(reports_frame)
        btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(btn_frame, text="DVDs No Devueltos", 
                  command=self.report_unreturned).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Más Rentadas", 
                  command=self.report_most_rented).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Ganancias Staff", 
                  command=self.report_staff_revenue).grid(row=0, column=2, padx=5)
        
        # Área de texto para resultados
        self.report_text = scrolledtext.ScrolledText(reports_frame, height=30, width=100)
        self.report_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        reports_frame.columnconfigure(0, weight=1)
        reports_frame.rowconfigure(1, weight=1)
    
    # === Métodos de API ===
    
    def api_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Optional[Dict]:
        """Hacer petición a la API"""
        try:
            url = f"{self.api_url.get()}{endpoint}"
            
            if method == 'GET':
                response = requests.get(url, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=10)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error API", f"Error al conectar con la API:\n{str(e)}")
            return None
    
    def test_connection(self):
        """Probar conexión con la API"""
        result = self.api_request('/health')
        if result:
            self.connected = True
            self.status_label.config(text="✓ Conectado", style='Success.TLabel')
        else:
            self.connected = False
            self.status_label.config(text="✗ No conectado", style='Error.TLabel')
    
    def list_all_films(self):
        """Listar todas las películas"""
        result = self.api_request('/api/films?limit=100')
        if result and 'data' in result:
            self.films_tree.delete(*self.films_tree.get_children())
            for film in result['data']:
                self.films_tree.insert('', 'end', values=(
                    film.get('film_id', ''),
                    film.get('title', ''),
                    film.get('release_year', ''),
                    film.get('length', ''),
                    film.get('rental_rate', ''),
                    film.get('rating', '')
                ))
    
    def search_films(self):
        """Buscar películas por título"""
        search_term = self.film_search_var.get()
        if not search_term:
            messagebox.showwarning("Advertencia", "Ingrese un término de búsqueda")
            return
        
        result = self.api_request(f'/api/films/search?title={search_term}')
        if result and 'data' in result:
            self.films_tree.delete(*self.films_tree.get_children())
            for film in result['data']:
                self.films_tree.insert('', 'end', values=(
                    film.get('film_id', ''),
                    film.get('title', ''),
                    film.get('release_year', ''),
                    film.get('length', ''),
                    film.get('rental_rate', ''),
                    film.get('rating', '')
                ))
    
    def list_customers(self):
        """Listar clientes"""
        result = self.api_request('/api/customers?limit=100')
        if result and 'data' in result:
            self.customers_tree.delete(*self.customers_tree.get_children())
            for customer in result['data']:
                self.customers_tree.insert('', 'end', values=(
                    customer.get('customer_id', ''),
                    customer.get('first_name', ''),
                    customer.get('last_name', ''),
                    customer.get('email', ''),
                    'Sí' if customer.get('active') else 'No'
                ))
    
    def view_customer_details(self):
        """Ver detalles de cliente seleccionado"""
        selection = self.customers_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un cliente")
            return
        
        customer_id = self.customers_tree.item(selection[0])['values'][0]
        result = self.api_request(f'/api/customers/{customer_id}')
        if result:
            info = json.dumps(result, indent=2, ensure_ascii=False)
            messagebox.showinfo("Detalles del Cliente", info)
    
    def list_rentals(self):
        """Listar rentas"""
        result = self.api_request('/api/rentals?limit=100')
        if result and 'data' in result:
            self.rentals_tree.delete(*self.rentals_tree.get_children())
            for rental in result['data']:
                self.rentals_tree.insert('', 'end', values=(
                    rental.get('rental_id', ''),
                    rental.get('film_title', ''),
                    rental.get('customer_name', ''),
                    rental.get('rental_date', '')[:10] if rental.get('rental_date') else '',
                    rental.get('return_date', '')[:10] if rental.get('return_date') else 'Pendiente',
                    rental.get('staff_name', '')
                ))
    
    def create_rental(self):
        """Crear nueva renta"""
        try:
            customer_id = int(self.rental_customer_id.get())
            film_id = int(self.rental_film_id.get())
            staff_id = int(self.rental_staff_id.get())
        except ValueError:
            messagebox.showerror("Error", "IDs deben ser números")
            return
        
        data = {
            'customer_id': customer_id,
            'film_id': film_id,
            'staff_id': staff_id
        }
        
        result = self.api_request('/api/rentals', method='POST', data=data)
        if result:
            messagebox.showinfo("Éxito", "Renta creada exitosamente")
            self.list_rentals()
            self.rental_customer_id.set('')
            self.rental_film_id.set('')
    
    def return_rental(self):
        """Devolver renta seleccionada"""
        selection = self.rentals_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una renta")
            return
        
        rental_id = self.rentals_tree.item(selection[0])['values'][0]
        result = self.api_request(f'/api/rentals/{rental_id}/return', method='PUT')
        if result:
            messagebox.showinfo("Éxito", "Renta devuelta exitosamente")
            self.list_rentals()
    
    def cancel_rental(self):
        """Cancelar renta seleccionada"""
        selection = self.rentals_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una renta")
            return
        
        rental_id = self.rentals_tree.item(selection[0])['values'][0]
        if messagebox.askyesno("Confirmar", "¿Cancelar esta renta?"):
            result = self.api_request(f'/api/rentals/{rental_id}', method='DELETE')
            if result:
                messagebox.showinfo("Éxito", "Renta cancelada exitosamente")
                self.list_rentals()
    
    def report_unreturned(self):
        """Reporte de DVDs no devueltos"""
        result = self.api_request('/api/reports/unreturned-dvds')
        if result:
            self.report_text.delete('1.0', tk.END)
            self.report_text.insert('1.0', "=== DVDs NO DEVUELTOS ===\n\n")
            self.report_text.insert(tk.END, f"Total: {result.get('count', 0)}\n")
            self.report_text.insert(tk.END, f"Con retraso: {result.get('overdue_count', 0)}\n\n")
            
            for item in result.get('data', []):
                self.report_text.insert(tk.END, f"Película: {item.get('film_title')}\n")
                self.report_text.insert(tk.END, f"Cliente: {item.get('customer_name')}\n")
                self.report_text.insert(tk.END, f"Fecha renta: {item.get('rental_date', '')[:10]}\n")
                self.report_text.insert(tk.END, f"Días retraso: {item.get('days_overdue', 0)}\n")
                self.report_text.insert(tk.END, "-" * 50 + "\n")
    
    def report_most_rented(self):
        """Reporte de películas más rentadas"""
        result = self.api_request('/api/reports/most-rented?limit=20')
        if result:
            self.report_text.delete('1.0', tk.END)
            self.report_text.insert('1.0', "=== PELÍCULAS MÁS RENTADAS ===\n\n")
            
            for i, item in enumerate(result.get('data', []), 1):
                self.report_text.insert(tk.END, f"{i}. {item.get('title')}\n")
                self.report_text.insert(tk.END, f"   Categoría: {item.get('category')}\n")
                self.report_text.insert(tk.END, f"   Total rentas: {item.get('total_rentals')}\n")
                self.report_text.insert(tk.END, f"   Revenue: ${item.get('total_revenue')}\n\n")
    
    def report_staff_revenue(self):
        """Reporte de ganancias por staff"""
        result = self.api_request('/api/reports/staff-revenue')
        if result:
            self.report_text.delete('1.0', tk.END)
            self.report_text.insert('1.0', "=== GANANCIAS POR STAFF ===\n\n")
            self.report_text.insert(tk.END, f"Total general: ${result.get('total_revenue_all_staff', 0)}\n\n")
            
            for item in result.get('data', []):
                self.report_text.insert(tk.END, f"{item.get('staff_name')}\n")
                self.report_text.insert(tk.END, f"  Email: {item.get('email')}\n")
                self.report_text.insert(tk.END, f"  Rentas: {item.get('total_rentals')}\n")
                self.report_text.insert(tk.END, f"  Pagos: {item.get('total_payments')}\n")
                self.report_text.insert(tk.END, f"  Revenue: ${item.get('total_revenue')}\n")
                self.report_text.insert(tk.END, f"  Promedio: ${item.get('average_payment')}\n")
                self.report_text.insert(tk.END, "-" * 50 + "\n")

def main():
    root = tk.Tk()
    app = DVDRentalApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()