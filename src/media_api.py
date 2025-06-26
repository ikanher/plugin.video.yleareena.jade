from __future__ import annotations
import os
from typing import TYPE_CHECKING, Optional

import requests  # type: ignore

try:
    import xbmcaddon  # type: ignore
except Exception:  # noqa: BLE001
    xbmcaddon = None  # type: ignore

if TYPE_CHECKING:  # pragma: no cover - hint for mypy
    import xbmcaddon  # type: ignore


class MediaAPI:
    def __init__(self, session: Optional[requests.Session] = None) -> None:
        self.session = session or requests.Session()
        self.app_id = self._get_app_id()
        self.app_key = self._get_app_key()
        self.quality = self._get_quality()

    def _get_app_id(self) -> str:
        if xbmcaddon is not None:
            value = xbmcaddon.Addon().getSettingString('app_id')
            if value:
                return value
        return os.getenv('YLE_APP_ID', 'player_static_prod')

    def _get_app_key(self) -> str:
        if xbmcaddon is not None:
            value = xbmcaddon.Addon().getSettingString('app_key')
            if value:
                return value
        return os.getenv('YLE_APP_KEY', '8930d72170e48303cf5f3867780d549b')

    def _get_quality(self) -> str:
        if xbmcaddon is not None:
            value = xbmcaddon.Addon().getSettingString('quality')
            if value:
                return value
        return os.getenv('YLE_STREAM_QUALITY', 'best')