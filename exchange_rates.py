"""
FINE 3300 – Assignment 1
Author: Dimitar Atanasov

File: exchange_rates.py

What I do with this file:
- I read the Bank of Canada CSV and grab the latest USD/CAD rate.
- I only need CAD <-> USD for this assignment.
- I return converted amounts rounded to cents.

Notes to grader:
- I use the standard csv module (no extra packages).
- I cache the last USD/CAD so repeated calls don’t keep re-reading the file.
- I validate the inputs so strange values don’t silently pass through.
"""

import csv
from typing import Optional


class ExchangeRates:
    """
    Simple CAD <-> USD converter using the latest USD/CAD from a CSV.

    Encapsulation choice:
    - I store the CSV path and the cached rate in "private" members so nothing else
      can overwrite them by accident. (Yes, I know Python's "private" is by name-mangling.)
    """

    def __init__(self, csv_path: str) -> None:
        """
        csv_path: path to the BankOfCanadaExchangeRates.csv file.
        I do a basic check to make sure it's a non-empty string.
        """
        if not isinstance(csv_path, str) or not csv_path.strip():
            raise ValueError("csv_path must be a non-empty string")
        self.__csv_path: str = csv_path
        self.__cached_usd_cad: Optional[float] = None  # I fill this on first use

    def __latest_usd_cad(self) -> float:
        """
        Returns the most recent USD/CAD (CAD per 1 USD) from the CSV.
        How I do it:
        - csv.DictReader to read rows by header name.
        - Keep the last numeric value in the 'USD/CAD' column.
        - If the file has a BOM, utf-8-sig handles it cleanly.
        - I cache it so later conversions are fast.
        """
        # If I already looked it up, just reuse it.
        if self.__cached_usd_cad is not None:
            return self.__cached_usd_cad

        last_rate: Optional[float] = None
        with open(self.__csv_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            # I expect a "USD/CAD" column in this file (as per assignment).
            if "USD/CAD" not in (reader.fieldnames or []):
                raise ValueError('CSV must contain a "USD/CAD" column.')

            for row in reader:
                cell = (row.get("USD/CAD") or "").strip()
                if not cell:
                    continue
                try:
                    last_rate = float(cell)
                except ValueError:
                    # If a row has text/empty junk here, I just skip it.
                    continue

        if last_rate is None:
            # If I made it through the file and never found a number, that’s a problem.
            raise ValueError("No numeric USD/CAD values found in the CSV.")

        self.__cached_usd_cad = last_rate
        return last_rate

    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """
        Convert amount between CAD and USD using the latest USD/CAD.
        Rules I’m following (assignment):
        - Only CAD and USD are supported.
        - If someone asks for CAD->CAD (or USD->USD), I just return the amount.
        - USD/CAD is "CAD per 1 USD", so:
            USD->CAD: amount * rate
            CAD->USD: amount / rate
        """
        # Basic checks so the function can't be called with anything too weird.
        if not isinstance(amount, (int, float)):
            raise TypeError("amount must be a number")
        if amount < 0:
            raise ValueError("amount must be non-negative")

        f = (from_currency or "").upper().strip()
        t = (to_currency or "").upper().strip()
        if f not in ("CAD", "USD") or t not in ("CAD", "USD"):
            raise ValueError("from_currency/to_currency must be 'CAD' or 'USD'")

        # Same currency? Nothing to do (still round to cents).
        if f == t:
            return round(float(amount), 2)

        rate = self.__latest_usd_cad()  # CAD per 1 USD

        if f == "USD" and t == "CAD":
            out = float(amount) * rate
        elif f == "CAD" and t == "USD":
            out = float(amount) / rate
        else:
            # Should not happen after validation, but I like being explicit.
            raise ValueError("Unsupported currency pair")

        # I add a tiny epsilon to avoid rare 0.005 rounding issues.
        return round(out + 1e-9, 2)

    # Read-only accessors (I don’t expose setters on purpose).
    def get_csv_path(self) -> str:
        return self.__csv_path

    def get_cached_usd_cad(self) -> Optional[float]:
        return self.__cached_usd_cad


# Quick local test (so I can run this file by itself).
if __name__ == "__main__":
    # If your CSV filename has (1) or (6) etc., update this string accordingly.
    csv_file = "BankOfCanadaExchangeRates.csv"
    xr = ExchangeRates(csv_file)

    print("100,000 USD -> CAD:", xr.convert(100_000, "USD", "CAD"))
    print("100,000 CAD -> USD:", xr.convert(100_000, "CAD", "USD"))
