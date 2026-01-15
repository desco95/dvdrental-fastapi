from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.schemas import Film
from app.database import get_db_cursor

router = APIRouter()

@router.get("/", response_model=dict)
async def list_films(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """Listar todas las películas"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                film_id, title, description, release_year,
                rental_rate, length, rating
            FROM film
            ORDER BY title
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        films = cursor.fetchall()
        
        # Contar total
        cursor.execute("SELECT COUNT(*) as count FROM film")
        total = cursor.fetchone()['count']
        
        return {
            "success": True,
            "count": len(films),
            "total": total,
            "data": films
        }

@router.get("/{film_id}", response_model=dict)
async def get_film(film_id: int):
    """Obtener una película por ID"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                f.film_id, f.title, f.description, f.release_year,
                f.rental_rate, f.length, f.rating,
                c.name as category,
                array_agg(DISTINCT CONCAT(a.first_name, ' ', a.last_name)) as actors
            FROM film f
            LEFT JOIN film_category fc ON f.film_id = fc.film_id
            LEFT JOIN category c ON fc.category_id = c.category_id
            LEFT JOIN film_actor fa ON f.film_id = fa.film_id
            LEFT JOIN actor a ON fa.actor_id = a.actor_id
            WHERE f.film_id = %s
            GROUP BY f.film_id, c.name
        """, (film_id,))
        
        film = cursor.fetchone()
        
        if not film:
            raise HTTPException(status_code=404, detail="Película no encontrada")
        
        return {
            "success": True,
            "data": film
        }

@router.get("/search", response_model=dict)
async def search_films(title: str = Query(..., min_length=1)):
    """Buscar películas por título"""
    with get_db_cursor() as cursor:
        search_pattern = f"%{title}%"
        cursor.execute("""
            SELECT 
                film_id, title, description, release_year,
                rental_rate, length, rating
            FROM film
            WHERE title ILIKE %s
            ORDER BY title
            LIMIT 50
        """, (search_pattern,))
        
        films = cursor.fetchall()
        
        return {
            "success": True,
            "count": len(films),
            "data": films
        }

@router.get("/category/{category_name}", response_model=dict)
async def get_films_by_category(category_name: str):
    """Obtener películas por categoría"""
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT 
                f.film_id, f.title, f.description, f.release_year,
                f.rental_rate, f.length, f.rating,
                c.name as category
            FROM film f
            JOIN film_category fc ON f.film_id = fc.film_id
            JOIN category c ON fc.category_id = c.category_id
            WHERE LOWER(c.name) = LOWER(%s)
            ORDER BY f.title
        """, (category_name,))
        
        films = cursor.fetchall()
        
        return {
            "success": True,
            "category": category_name,
            "count": len(films),
            "data": films
        }