#!/usr/bin/env python3
"""Yerel RAG web ürününü tek süreçte çalıştır."""

from __future__ import annotations

import uvicorn

from web_api import create_app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
