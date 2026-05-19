"""Web scraper for Syosset Fire Department website."""

import logging
import urllib.request
import urllib.error
from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)

ALARMS_URL = "https://www.syossetfd.org/control/losapiframe.php"
# The alarms iframe only serves content when a Referer from the main site is present
_REFERER = "https://www.syossetfd.org/indexBottom.php"

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


class SyossetFDScraper:
    """Scraper for Syosset FD alarms."""

    def fetch_alarms(self) -> list[dict]:
        """Fetch and parse recent alarms from the Syosset FD website."""
        html = self._fetch_url(ALARMS_URL)
        if not html:
            _LOGGER.error("Failed to fetch Syosset FD content from %s", ALARMS_URL)
            return []

        alarms = self._parse_alarms(html)
        _LOGGER.debug("Parsed %d alarms from Syosset FD website", len(alarms))
        return alarms

    def _parse_alarms(self, html: str) -> list[dict]:
        """Parse alarms from HTML using BeautifulSoup."""
        soup = BeautifulSoup(html, "html.parser")
        alarms = []

        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            if len(rows) < 2:
                continue

            # Build header list from the first row
            header_cells = rows[0].find_all(["th", "td"])
            headers = [
                cell.get_text(separator=" ", strip=True)
                    .lower()
                    .replace("/", "_")
                    .replace(" ", "_")
                for cell in header_cells
            ]

            # Skip tables that look like navigation or layout (no useful headers)
            if not headers or all(h == "" for h in headers):
                continue

            candidate_rows = []
            for row in rows[1:]:
                cells = row.find_all(["td", "th"])
                if not cells:
                    continue
                values = [cell.get_text(separator=" ", strip=True) for cell in cells]
                if not any(values):
                    continue
                # Zip with headers; pad with indexed keys if row is wider than headers
                alarm: dict[str, str] = {}
                for i, val in enumerate(values):
                    key = headers[i] if i < len(headers) else f"col_{i}"
                    alarm[key] = val
                candidate_rows.append(alarm)

            if candidate_rows:
                alarms = candidate_rows
                # Prefer the table that produced the most rows (the alarms table)
                # but stop at the first non-empty table so we don't keep overwriting
                break

        return alarms

    def _fetch_url(self, url: str) -> str | None:
        """Fetch URL and return decoded HTML, or None on error."""
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": _USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": _REFERER,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                return response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as err:
            _LOGGER.error("HTTP %s fetching %s", err.code, url)
        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Error fetching %s: %s", url, err)
        return None
