from __future__ import annotations
import os
from typing import Optional

try:
    import httpx
except ImportError:  # pragma: no cover
    httpx = None
    import requests
from pydantic import BaseModel


class Playout(BaseModel):
    url: str
    drm: bool = False
    protocol: str
    language: Optional[str] = None


class MediaAPI:
    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        app_id: Optional[str] = None,
        app_key: Optional[str] = None,
        http: Optional[object] = None,
    ) -> None:
        self.base_url = base_url or os.getenv('YLE_MEDIA_BASE_URL', 'https://media.api.yle.fi')
        self.app_id = app_id or os.getenv('YLE_APP_ID', 'player_static_prod')
        self.app_key = app_key or os.getenv('YLE_APP_KEY', '8930d72170e48303cf5f3867780d549b')
        if httpx:
            self._http_get = (http or httpx.Client(timeout=3.0)).get
        else:  # pragma: no cover
            self._http_get = requests.get

    def get_playout(self, item_id: str, protocol: str = 'HLS') -> Optional[Playout]:
        url = f'{self.base_url}/v2/{item_id}/playouts.json'
        params = {
            'app_id': self.app_id,
            'app_key': self.app_key,
            'protocol': protocol,
        }
        try:
            r = self._http_get(url, params=params, timeout=3.0)
            if httpx:
                r.raise_for_status()
            elif r.status_code >= 400:  # pragma: no cover
                raise requests.HTTPError(response=r)
        except Exception:  # pragma: no cover
            return None
        data = r.json().get('data')
        if isinstance(data, list):
            info = data[0] if data else None
        else:
            info = data
        if not info or 'url' not in info:
            return None
        return Playout(
            url=info.get('url', ''),
            drm=bool(info.get('drm')),
            protocol=info.get('protocol', protocol),
            language=info.get('language'),
        )
