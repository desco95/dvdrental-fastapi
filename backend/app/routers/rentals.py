from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.schemas import RentalCreate, RentalResponse, SuccessResponse
from app.database import get_db_cursor

router = APIRouter()

@router.get("/", response_model=dict)
async def list_rentals(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """Listar todas las rentas"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                r.rental_id,
                r.rental_date,
                r.return_date,
                r.customer_id,
                r.staff_id,
                i.film_id,
                f.title as film_title,
                CONCAT(c.first_name, ' ', c.last_name) as customer_name,
                CONCAT(s.first_name, ' ', s.last_name) as staff_name,
                f.rental_duration,
                r.rental_date + INTERVAL '1 day' * f.rental_duration as expected_return_date
            FROM rental r
            JOIN inventory i ON r.inventory_id = i.inventory_id
            JOIN film f ON i.film_id = f.film_id
            JOIN customer c ON r.customer_id = c.customer_id
            JOIN staff s ON r.staff_id = s.staff_id
            ORDER BY r.rental_date DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        rentals = cursor.fetchall()
        
        # Contar total
        cursor.execute("SELECT COUNT(*) as count FROM rental")
        total = cursor.fetchone()['count']
        
        return {
            "success": True,
            "count": len(rentals),
            "total": total,
            "data": rentals
        }

@router.post("/", response_model=dict, status_code=201)
async def create_rental(rental: RentalCreate):
    """
    Crear una nueva renta.
    
    Requiere:
    - customer_id: ID del cliente
    - film_id: ID de la película
    - staff_id: ID del empleado
    """
    with get_db_cursor(commit=True) as cursor:
        # Verificar que el cliente existe
        cursor.execute("SELECT customer_id FROM customer WHERE customer_id = %s", (rental.customer_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Verificar que el staff existe
        cursor.execute("SELECT staff_id FROM staff WHERE staff_id = %s", (rental.staff_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        
        # Verificar que la película existe y obtener datos
        cursor.execute("""
            SELECT film_id, title, rental_rate, rental_duration 
            FROM film WHERE film_id = %s
        """, (rental.film_id,))
        film = cursor.fetchone()
        if not film:
            raise HTTPException(status_code=404, detail="Película no encontrada")
        
        # Buscar inventario disponible
        cursor.execute("""
            SELECT i.inventory_id 
            FROM inventory i
            WHERE i.film_id = %s
            AND i.inventory_id NOT IN (
                SELECT inventory_id 
                FROM rental 
                WHERE return_date IS NULL
            )
            LIMIT 1
        """, (rental.film_id,))
        
        inventory = cursor.fetchone()
        if not inventory:
            raise HTTPException(status_code=400, detail="No hay copias disponibles de esta película")
        
        # Crear la renta
        rental_date = datetime.now()
        expected_return = rental_date + timedelta(days=film['rental_duration'])
        
        cursor.execute("""
            INSERT INTO rental (rental_date, inventory_id, customer_id, staff_id)
            VALUES (%s, %s, %s, %s)
            RETURNING rental_id
        """, (rental_date, inventory['inventory_id'], rental.customer_id, rental.staff_id))
        
        result = cursor.fetchone()
        rental_id = result['rental_id']
        
        # Obtener datos completos de la renta creada
        cursor.execute("""
            SELECT 
                r.rental_id,
                r.rental_date,
                r.customer_id,
                i.film_id,
                r.staff_id,
                f.title as film_title,
                f.rental_rate,
                f.rental_duration,
                CONCAT(c.first_name, ' ', c.last_name) as customer_name,
                CONCAT(s.first_name, ' ', s.last_name) as staff_name
            FROM rental r
            JOIN inventory i ON r.inventory_id = i.inventory_id
            JOIN film f ON i.film_id = f.film_id
            JOIN customer c ON r.customer_id = c.customer_id
            JOIN staff s ON r.staff_id = s.staff_id
            WHERE r.rental_id = %s
        """, (rental_id,))
        
        rental_data = cursor.fetchone()
        rental_data['expected_return_date'] = expected_return.isoformat()
        
        return {
            "success": True,
            "message": "Renta creada exitosamente",
            "data": rental_data
        }

@router.put("/{rental_id}/return", response_model=dict)
async def return_rental(rental_id: int):
    """Marcar una renta como devuelta"""
    with get_db_cursor(commit=True) as cursor:
        # Verificar que la renta existe
        cursor.execute("""
            SELECT r.rental_id, r.rental_date, r.return_date, 
                   f.rental_rate, f.rental_duration
            FROM rental r
            JOIN inventory i ON r.inventory_id = i.inventory_id
            JOIN film f ON i.film_id = f.film_id
            WHERE r.rental_id = %s
        """, (rental_id,))
        
        rental = cursor.fetchone()
        if not rental:
            raise HTTPException(status_code=404, detail="Renta no encontrada")
        
        if rental['return_date']:
            raise HTTPException(status_code=400, detail="Esta renta ya fue devuelta")
        
        # Actualizar fecha de devolución
        return_date = datetime.now()
        cursor.execute("""
            UPDATE rental 
            SET return_date = %s 
            WHERE rental_id = %s
        """, (return_date, rental_id))
        
        # Calcular días rentados y monto
        days_rented = (return_date - rental['rental_date']).days
        total_amount = float(rental['rental_rate']) * max(days_rented, 1)
        
        # Crear pago
        cursor.execute("""
            INSERT INTO payment (customer_id, staff_id, rental_id, amount, payment_date)
            SELECT customer_id, staff_id, rental_id, %s, %s
            FROM rental WHERE rental_id = %s
        """, (total_amount, return_date, rental_id))
        
        return {
            "success": True,
            "message": "Devolución procesada exitosamente",
            "data": {
                "rental_id": rental_id,
                "return_date": return_date.isoformat(),
                "days_rented": days_rented,
                "total_amount": total_amount
            }
        }

@router.delete("/{rental_id}", response_model=dict)
async def cancel_rental(rental_id: int):
    """Cancelar una renta (solo si no ha sido devuelta)"""
    with get_db_cursor(commit=True) as cursor:
        # Verificar que existe y obtener datos
        cursor.execute("""
            SELECT r.rental_id, r.return_date,
                   f.title as film_title,
                   CONCAT(c.first_name, ' ', c.last_name) as customer_name,
                   CONCAT(s.first_name, ' ', s.last_name) as staff_name
            FROM rental r
            JOIN inventory i ON r.inventory_id = i.inventory_id
            JOIN film f ON i.film_id = f.film_id
            JOIN customer c ON r.customer_id = c.customer_id
            JOIN staff s ON r.staff_id = s.staff_id
            WHERE r.rental_id = %s
        """, (rental_id,))
        
        rental = cursor.fetchone()
        if not rental:
            raise HTTPException(status_code=404, detail="Renta no encontrada")
        
        if rental['return_date']:
            raise HTTPException(status_code=400, detail="No se puede cancelar una renta ya devuelta")
        
        # Eliminar la renta
        cursor.execute("DELETE FROM rental WHERE rental_id = %s", (rental_id,))
        
        return {
            "success": True,
            "message": "Renta cancelada exitosamente",
            "data": {
                "rental_id": rental_id,
                "film": {"title": rental['film_title']},
                "customer": {"name": rental['customer_name']},
                "staff": {"name": rental['staff_name']}
            }
        }

@router.get("/customer/{customer_id}", response_model=dict)
async def get_customer_rentals(customer_id: int):
    """Obtener todas las rentas de un cliente"""
    with get_db_cursor() as cursor:
        # Verificar que el cliente existe
        cursor.execute("""
            SELECT customer_id, CONCAT(first_name, ' ', last_name) as name
            FROM customer WHERE customer_id = %s
        """, (customer_id,))
        customer = cursor.fetchone()
        
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Obtener rentas
        cursor.execute("""
            SELECT 
                r.rental_id,
                r.rental_date,
                r.return_date,
                f.title as film_title,
                f.rental_rate,
                p.amount as payment_amount,
                CASE 
                    WHEN r.return_date IS NOT NULL 
                    THEN EXTRACT(day FROM (r.return_date - r.rental_date))
                    ELSE NULL
                END as days_rented
            FROM rental r
            JOIN inventory i ON r.inventory_id = i.inventory_id
            JOIN film f ON i.film_id = f.film_id
            LEFT JOIN payment p ON r.rental_id = p.rental_id
            WHERE r.customer_id = %s
            ORDER BY r.rental_date DESC
        """, (customer_id,))
        
        rentals = cursor.fetchall()
        
        return {
            "success": True,
            "customer": customer,
            "total_rentals": len(rentals),
            "rentals": rentals
        }