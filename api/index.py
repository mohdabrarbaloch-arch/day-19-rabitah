"""Vercel serverless entrypoint."""

from app.main import app

handler = app
