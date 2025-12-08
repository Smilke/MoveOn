from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


@router.get("/health", summary="Verifica se a API está no ar")
def health_check():
    return {"status": "ok"}


@router.get("/hello/{name}", summary="Cumprimenta a pessoa pelo nome")
def say_hello(name: str):
    return {"message": f"Olá, {name}!"}


@router.get("/soma", summary="Soma dois números inteiros")
def sum_numbers(a: int, b: int):
    return {"a": a, "b": b, "resultado": a + b}


class Item(BaseModel):
    name: str
    quantity: int

