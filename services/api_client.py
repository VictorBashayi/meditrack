# Owned by Mohammed Usman
"""
services/api_client.py
----------------------
API client for MediTrack's two external public data sources.

Owner: Mohammed Usman
Branch: feature/api-integration

This is the ONLY place in the project where requests is called.
Pages never import requests directly — they call APIClient methods instead.

APIs used:
    1. disease.sh  — https://disease.sh/
       Free, no key required. Provides real-time global disease statistics.

    2. OpenFDA     — https://api.fda.gov/drug/
       Free US government API, no key required. Provides drug label data,
       adverse event reports, and active recall notices.
"""

import requests

from exceptions.custom_exceptions import APIError

_DISEASE_SH_BASE = "https://disease.sh/v3/covid-19"
_OPENFDA_DRUG_BASE = "https://api.fda.gov/drug"
_TIMEOUT = 10


class APIClient:
    """
    Handles all outbound HTTP calls to disease.sh and OpenFDA.

    Usage (from a page):
    --------------------
        from services.api_client import APIClient
        from exceptions.custom_exceptions import APIError

        client = APIClient()

        try:
            stats = client.get_disease_stats("covid-19")
        except APIError as e:
            st.warning(str(e))

    All methods raise APIError on any failure. The calling page
    is responsible for catching it and showing a graceful fallback.
    """

    # ------------------------------------------------------------------
    # Internal helper
    # ------------------------------------------------------------------

    def _get(self, url: str, params: dict | None = None) -> dict | list:
        """
        Perform a GET request and return the parsed JSON body.

        Raises
        ------
        APIError on timeout, HTTP error, connection failure, or bad JSON.
        """
        try:
            response = requests.get(url, params=params, timeout=_TIMEOUT)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            raise APIError(
                "The request timed out. Check your internet connection and try again."
            )
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "unknown"
            raise APIError(
                f"The API returned an error (HTTP {status}). "
                "This may be temporary — please try again shortly."
            )
        except requests.exceptions.ConnectionError:
            raise APIError(
                "Could not connect to the external API. "
                "Check your internet connection."
            )
        except requests.exceptions.RequestException as e:
            raise APIError(f"An unexpected network error occurred: {e}")
        except ValueError:
            raise APIError(
                "The API returned a response that could not be read. "
                "Please try again."
            )

    # ------------------------------------------------------------------
    # disease.sh methods
    # ------------------------------------------------------------------

    def get_disease_stats(self, disease: str) -> dict:
        """
        Fetch real-time global statistics for a named disease.

        Parameters
        ----------
        disease : Name of the disease. e.g. "covid-19"

        Returns
        -------
        dict with keys: disease, cases, deaths, recovered, active, source

        Raises
        ------
        APIError
            If the request fails or the disease has no available data.
        """
        clean = disease.strip().lower()

        if "covid" in clean:
            url = f"{_DISEASE_SH_BASE}/all"
            data = self._get(url)
            return {
                "disease": "COVID-19",
                "cases": data.get("cases"),
                "deaths": data.get("deaths"),
                "recovered": data.get("recovered"),
                "active": data.get("active"),
                "source": "disease.sh — Johns Hopkins University",
            }

        raise APIError(
            f"Real-time statistics for '{disease}' are not available. "
            "disease.sh currently provides live data for COVID-19. "
            "For other diseases, consult the WHO or CDC directly."
        )

    def get_country_covid_stats(self, country: str) -> dict:
        """
        Fetch COVID-19 statistics for a specific country.

        Useful when a patient's travel history lists a country and staff
        want to see current outbreak severity in that region.

        Parameters
        ----------
        country : Country name or ISO code. e.g. "Nigeria", "US", "GB"

        Returns
        -------
        dict with keys: country, cases, deaths, recovered, active, critical, source

        Raises
        ------
        APIError
            If the country is not found or the request fails.
        """
        url = f"{_DISEASE_SH_BASE}/countries/{country.strip()}"
        data = self._get(url)
        return {
            "country": data.get("country", country),
            "cases": data.get("cases"),
            "deaths": data.get("deaths"),
            "recovered": data.get("recovered"),
            "active": data.get("active"),
            "critical": data.get("critical"),
            "source": "disease.sh — Johns Hopkins University",
        }

    # ------------------------------------------------------------------
    # OpenFDA methods
    # ------------------------------------------------------------------

    def get_drug_info(self, drug_name: str) -> dict:
        """
        Fetch official drug label information from OpenFDA.

        Searches by brand name first, falls back to generic name.

        Parameters
        ----------
        drug_name : Brand or generic name. e.g. "Amoxicillin", "Ibuprofen"

        Returns
        -------
        dict with keys:
            drug_name, brand_name, generic_name, warnings,
            adverse_reactions, indications, dosage, manufacturer, source

        Raises
        ------
        APIError
            If no drug label is found or the request fails.
        """
        clean = drug_name.strip()
        url = f"{_OPENFDA_DRUG_BASE}/label.json"

        # Try brand name first
        params = {"search": f'openfda.brand_name:"{clean}"', "limit": 1}
        data = self._get(url, params=params)
        results = data.get("results")

        # Fall back to generic name
        if not results:
            params["search"] = f'openfda.generic_name:"{clean}"'
            data = self._get(url, params=params)
            results = data.get("results")

        if not results:
            raise APIError(
                f"No drug label found for '{drug_name}'. "
                "Check the spelling or try a generic name."
            )

        label = results[0]
        openfda = label.get("openfda", {})

        def first(field: str) -> str | None:
            value = label.get(field)
            if isinstance(value, list) and value:
                return value[0]
            return None

        def first_openfda(field: str) -> str | None:
            value = openfda.get(field)
            if isinstance(value, list) and value:
                return value[0]
            return None

        return {
            "drug_name": clean,
            "brand_name": first_openfda("brand_name"),
            "generic_name": first_openfda("generic_name"),
            "warnings": first("warnings"),
            "adverse_reactions": first("adverse_reactions"),
            "indications": first("indications_and_usage"),
            "dosage": first("dosage_and_administration"),
            "manufacturer": first_openfda("manufacturer_name"),
            "source": "OpenFDA — U.S. Food & Drug Administration",
        }

    def get_drug_recall(self, drug_name: str) -> list[dict]:
        """
        Check for active recalls on a drug via OpenFDA enforcement reports.

        Parameters
        ----------
        drug_name : Brand or generic name to check.

        Returns
        -------
        list[dict]
            Each dict has: recall_number, reason, status, date, product_description.
            Returns an empty list if no recalls are found — this is normal
            and expected for most drugs.

        Raises
        ------
        APIError
            Only if the network request itself fails.
        """
        url = f"{_OPENFDA_DRUG_BASE}/enforcement.json"
        params = {
            "search": f'product_description:"{drug_name.strip()}"',
            "limit": 5,
        }

        try:
            data = self._get(url, params=params)
        except APIError as e:
            # OpenFDA returns 404 when there are zero enforcement records —
            # this is expected and means "no recalls found", not a real error.
            if "HTTP 404" in str(e):
                return []
            raise

        recalls = []
        for item in data.get("results", []):
            recalls.append({
                "recall_number": item.get("recall_number"),
                "reason": item.get("reason_for_recall"),
                "status": item.get("status"),
                "date": item.get("report_date"),
                "product_description": item.get("product_description"),
            })

        return recalls