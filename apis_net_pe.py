from typing import List, Optional
import logging
import requests



class ApisNetPe:

    BASE_URL = "https://api.apis.net.pe"

    def __init__(self, token: str = None) -> None:
        self.token = token

    def _get(self, path: str, params: dict):

        url = f"{self.BASE_URL}{path}"

        headers = {
            "Authorization": self.token, 
            "Referer": "https://apis.net.pe/api-tipo-cambio.html"
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 422:
            logging.warning(f"{response.url} - invalida parameter")
            logging.warning(response.text)
        elif response.status_code == 403:
            logging.warning(f"{response.url} - IP blocked")
        elif response.status_code == 429:
            logging.warning(f"{response.url} - Many requests add delay")
        elif response.status_code == 401:
            logging.warning(f"{response.url} - Invalid token or limited")
        else:
            logging.warning(f"{response.url} - Server Error status_code={response.status_code}")
        return None

    def get_person(self, dni: str) -> Optional[dict]:
        return self._get("/v1/dni", {"numero": dni})

    def get_company(self, ruc: str) -> Optional[dict]:
        return self._get("/v1/ruc", {"numero": ruc})

    def get_exchange_rate(self, date: str) -> dict:
        return self._get("/v1/tipo-cambio-sunat", {"fecha": date})

    def get_exchange_rate_today(self) -> dict:
        return self._get("/v1/tipo-cambio-sunat", {})

    def get_exchange_rate_for_month(self, month: int, year: int) -> List[dict]:
        return self._get("/v1/tipo-cambio-sunat", {"month": month, "year": year})
