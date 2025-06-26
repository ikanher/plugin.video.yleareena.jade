from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field, ConfigDict

try:
    import xbmcaddon  # type: ignore
except Exception:  # pragma: no cover - Kodi environment only
    xbmcaddon = None  # type: ignore


class Item(BaseModel):
    id: str
    type: str
    mediaType: str
    version: int = Field(alias="_version")
    title: Optional[Dict[str, str]] = None
    description: Optional[Dict[str, str]] = None

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class ProgramSearch(BaseModel):
    data: List[Item]
    meta: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


class ProgramAPI:
    """Minimal wrapper for Yle Programs API V3."""

    BASE_URL = "https://programs.api.yle.fi"

    def __init__(
        self,
        *,
        app_id: Optional[str] = None,
        app_key: Optional[str] = None,
        client: Optional[httpx.Client] = None,
    ) -> None:
        self.app_id = app_id or self._get_app_id()
        self.app_key = app_key or self._get_app_key()
        self._client = client or httpx.Client(base_url=self.BASE_URL, timeout=3.0)
        self._own_client = client is None

    def _get_app_id(self) -> str:
        if xbmcaddon is not None:
            value = xbmcaddon.Addon().getSettingString("app_id")
            if value:
                return value
        return os.getenv("YLE_APP_ID", "player_static_prod")

    def _get_app_key(self) -> str:
        if xbmcaddon is not None:
            value = xbmcaddon.Addon().getSettingString("app_key")
            if value:
                return value
        return os.getenv("YLE_APP_KEY", "8930d72170e48303cf5f3867780d549b")

    def close(self) -> None:
        if self._own_client:
            self._client.close()

    def _params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        auth = {"app_id": self.app_id, "app_key": self.app_key}
        auth.update(params)
        return auth

    def search(self, q: str, **params: Any) -> ProgramSearch:
        """Search items."""
        resp = self._client.get("/v3/schema/v3/items", params=self._params({"q": q, **params}))
        resp.raise_for_status()
        return ProgramSearch.model_validate(resp.json())

    def get_item(self, item_id: str, **params: Any) -> Item:
        """Fetch a single item by id."""
        resp = self._client.get(f"/v3/schema/v3/items/{item_id}", params=self._params(params))
        resp.raise_for_status()
        payload = resp.json()
        if "data" in payload:
            payload = payload["data"]
        return Item.model_validate(payload)

    def __enter__(self) -> "ProgramAPI":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
