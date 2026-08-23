from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class NetworkEvent(BaseModel):
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None

    src_port: Optional[int] = None
    dst_port: Optional[int] = None

    proto: Optional[str] = None
    service: Optional[str] = None

    duration: Optional[float] = None

    src_bytes: Optional[int] = None
    dst_bytes: Optional[int] = None

    attack_type: Optional[str] = None

    timestamp: Optional[str] = None
