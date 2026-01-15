from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from app.database import get_db_cursor

router = APIRouter()

@router.get("/unreturned-dvds", response_model=dict)
async def get_unreturned_dvds():
    """
    Obtener lista de DVDs que no han sido devueltos.
    Identifica rentas activas con posibles retrasos.
    """
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                r.rental_id,
                f.title as film_title,
                CONCAT(c.first_name, ' ', c.last_name) as customer_name,
                r.rental_date,
                r.rental_date + INTERVAL '1 day' * f.rental_duration as expected_return_date,
                EXTRACT(day FROM (CURRENT_DATE - (r.rental_date + INTERVAL '1 day' * f.rental_duration))) as days_overdue,
                c.email as customer_email,
                f.rental_rate
            FROM rental r
            JOIN inventory i ON r.inventory_id = i.inventory_id
            JOIN film f ON i.film_id = f.film_id
            JOIN customer c ON r.customer_id = c.customer_id
            WHERE r.return_date IS NULL
            ORDER BY r.rental_date ASC
        """)
        
        unreturned = cursor.fetchall()
        
        # Calcular estadísticas
        overdue_count = sum(1 for r in unreturned if r['days_overdue'] > 0)
        
        return {
            "success": True,
            "count": len(unreturned),
            "overdue_count": overdue_count,
            "generated_at": datetime.now().isoformat(),
            "data": unreturned
        }

@router.get("/most-rented", response_model=dict)
async def get_most_rented_films(limit: int = Query(default=10, ge=1, le=100)):
    """
    Obtener ranking de películas más rentadas.
    Incluye categoría, total de rentas y revenue generado.
    """
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                f.film_id,
                f.title,
                c.name as category,
                COUNT(r.rental_id) as total_rentals,
                f.rental_rate,
                COUNT(r.rental_id) * f.rental_rate as total_revenue
            FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            JOIN inventory i ON f.film_id = i.film_id
            JOIN rental r ON i.inventory_id = r.inventory_id
            GROUP BY f.film_id, f.title, c.name, f.rental_rate
            ORDER BY total_rentals DESC, total_revenue DESC
            LIMIT %s
        """, (limit,))
        
        most_rented = cursor.fetchall()
        
        return {
            "success": True,
            "count": len(most_rented),
            "generated_at": datetime.now().isoformat(),
            "data": most_rented
        }

@router.get("/staff-revenue", response_model=dict)
async def get_staff_revenue():
    """
    Calcular el total de ganancias generadas por cada miembro del staff.
    Incluye número de rentas, pagos y promedio.
    """
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                s.staff_id,
                CONCAT(s.first_name, ' ', s.last_name) as staff_name,
                s.email,
                COUNT(DISTINCT r.rental_id) as total_rentals,
                COUNT(p.payment_id) as total_payments,
                COALESCE(SUM(p.amount), 0) as total_revenue,
                COALESCE(AVG(p.amount), 0) as average_payment
            FROM staff s
            LEFT JOIN rental r ON s.staff_id = r.staff_id
            LEFT JOIN payment p ON r.rental_id = p.rental_id
            GROUP BY s.staff_id, s.first_name, s.last_name, s.email
            ORDER BY total_revenue DESC
        """)
        
        staff_revenue = cursor.fetchall()
        
        # Calcular totales globales
        total_revenue_all = sum(float(s['total_revenue']) for s in staff_revenue)
        
        return {
            "success": True,
            "count": len(staff_revenue),
            "total_revenue_all_staff": total_revenue_all,
            "generated_at": datetime.now().isoformat(),
            "data": staff_revenue
        }

@router.get("/staff-revenue/{staff_id}", response_model=dict)
async def get_staff_revenue_by_id(staff_id: int):
    """
    Obtener ganancias generadas por un miembro específico del staff.
    """
    with get_db_cursor() as cursor:
        # Verificar que el staff existe
        cursor.execute("""
            SELECT staff_id, CONCAT(first_name, ' ', last_name) as name
            FROM staff WHERE staff_id = %s
        """, (staff_id,))
        staff = cursor.fetchone()
        
        if not staff:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        
        # Obtener estadísticas
        cursor.execute("""
            SELECT 
                s.staff_id,
                CONCAT(s.first_name, ' ', s.last_name) as staff_name,
                s.email,
                COUNT(DISTINCT r.rental_id) as total_rentals,
                COUNT(p.payment_id) as total_payments,
                COALESCE(SUM(p.amount), 0) as total_revenue,
                COALESCE(AVG(p.amount), 0) as average_payment
            FROM staff s
            LEFT JOIN rental r ON s.staff_id = r.staff_id
            LEFT JOIN payment p ON r.rental_id = p.rental_id
            WHERE s.staff_id = %s
            GROUP BY s.staff_id, s.first_name, s.last_name, s.email
        """, (staff_id,))
        
        revenue = cursor.fetchone()
        
        # Obtener rentas recientes
        cursor.execute("""
            SELECT 
                r.rental_id,
                f.title as film_title,
                r.rental_date,
                r.return_date,
                p.amount as payment_amount
            FROM rental r
            JOIN inventory i ON r.inventory_id = i.inventory_id
            JOIN film f ON i.film_id = f.film_id
            LEFT JOIN payment p ON r.rental_id = p.rental_id
            WHERE r.staff_id = %s
            ORDER BY r.rental_date DESC
            LIMIT 10
        """, (staff_id,))
        
        recent_rentals = cursor.fetchall()
        
        return {
            "success": True,
            "staff": revenue,
            "recent_rentals": recent_rentals,
            "generated_at": datetime.now().isoformat()
        }

@router.get("/customer-rentals/{customer_id}", response_model=dict)
async def get_customer_rental_report(customer_id: int):
    """
    Reporte completo de rentas de un cliente.
    Alias del endpoint /api/rentals/customer/{customer_id}
    """
    with get_db_cursor() as cursor:
        # Verificar cliente
        cursor.execute("""
            SELECT customer_id, CONCAT(first_name, ' ', last_name) as name, email
            FROM customer WHERE customer_id = %s
        """, (customer_id,))
        customer = cursor.fetchone()
        
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Obtener rentas
        cursor.execute("""
            SELECT 
                r.rental_id,
                f.title as film_title,
                r.rental_date,
                r.return_date,
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
        
        # Calcular estadísticas
        total_spent = sum(float(r['payment_amount']) for r in rentals if r['payment_amount'])
        active_rentals = sum(1 for r in rentals if not r['return_date'])
        
        return {
            "success": True,
            "customer": customer,
            "total_rentals": len(rentals),
            "active_rentals": active_rentals,
            "total_spent": total_spent,
            "rentals": rentals,
            "generated_at": datetime.now().isoformat()
        }