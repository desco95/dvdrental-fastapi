from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.database import get_db_cursor

router = APIRouter()

@router.get("/", response_model=dict)
async def list_customers(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """Listar todos los clientes"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                customer_id,
                first_name,
                last_name,
                email,
                active,
                store_id
            FROM customer
            ORDER BY last_name, first_name
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        customers = cursor.fetchall()
        
        # Contar total
        cursor.execute("SELECT COUNT(*) as count FROM customer")
        total = cursor.fetchone()['count']
        
        return {
            "success": True,
            "count": len(customers),
            "total": total,
            "data": customers
        }

@router.get("/{customer_id}", response_model=dict)
async def get_customer(customer_id: int):
    """Obtener un cliente por ID"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                c.customer_id,
                c.first_name,
                c.last_name,
                c.email,
                c.active,
                c.store_id,
                a.address,
                a.phone,
                ci.city,
                co.country
            FROM customer c
            LEFT JOIN address a ON c.address_id = a.address_id
            LEFT JOIN city ci ON a.city_id = ci.city_id
            LEFT JOIN country co ON ci.country_id = co.country_id
            WHERE c.customer_id = %s
        """, (customer_id,))
        
        customer = cursor.fetchone()
        
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        return {
            "success": True,
            "data": customer
        }