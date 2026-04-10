"""Route handlers for model registry"""

from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()


@router.get("/models")
async def list_models():
    """List all registered models"""
    return {
        "models": [],
        "total": 0,
        "status": "coming_soon",
    }


@router.post("/models/register")
async def register_model(model_data: dict):
    """Register a new model"""
    return {
        "message": "Model registered",
        "status": "coming_soon",
    }


@router.get("/models/{model_name}")
async def get_model(model_name: str):
    """Get specific model details"""
    return {
        "model_name": model_name,
        "status": "coming_soon",
    }


@router.get("/models/{model_name}/versions")
async def get_model_versions(model_name: str):
    """Get all versions of a model"""
    return {
        "model_name": model_name,
        "versions": [],
        "status": "coming_soon",
    }


@router.post("/models/{model_name}/promote")
async def promote_model(model_name: str, version: str, stage: str):
    """Promote model to a new stage"""
    return {
        "model_name": model_name,
        "version": version,
        "stage": stage,
        "status": "coming_soon",
    }
