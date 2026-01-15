from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.database import get_db_cursor

router = APIRouter()

@router.get("/", response_model=dict)
async def list_staff(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """Listar todos los empleados"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                staff_id, 
                first_name, 
                last_name, 
                email, 
                active,
                store_id
            FROM staff
            ORDER BY last_name, first_name
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        staff = cursor.fetchall()
        
        # Contar total
        cursor.execute("SELECT COUNT(*) as count FROM staff")
        total = cursor.fetchone()['count']
        
        return {
            "success": True,
            "count": len(staff),
            "total": total,
            "data": staff
        }

@router.get("/{staff_id}", response_model=dict)
async def get_staff(staff_id: int):
    """Obtener un empleado por ID"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                s.staff_id,
                s.first_name,
                s.last_name,
                s.email,
                s.active,
                s.store_id,
                a.address,
                a.phone,
                c.city,
                co.country
            FROM staff s
            LEFT JOIN address a ON s.address_id = a.address_id
            LEFT JOIN city c ON a.city_id = c.city_id
            LEFT JOIN country co ON c.country_id = co.country_id
            WHERE s.staff_id = %s
        """, (staff_id,))
        
        staff = cursor.fetchone()
        
        if not staff:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        
        return {
            "success": True,
            "data": staff
        }