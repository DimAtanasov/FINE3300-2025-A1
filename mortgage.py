"""
FINE 3300 – Assignment 1
Author: Dimitar Atanasov

File: mortgage.py

What I do with this file:
- I calculate mortgage payments for common Canadian schedules:
  Monthly, Semi-monthly, Bi-weekly, Weekly, plus Rapid Bi-weekly and Rapid Weekly.
- The rate is quoted with SEMI-ANNUAL compounding (Canadian rule),
  so I convert j (nominal semi-annual) → EAR → per-period rate r_m.
- The code returns all amounts rounded to cents.

Formulas I used:
  EAR = (1 + j/2)^2 - 1
  r_m = (1 + EAR)^(1/m) - 1
  PVA(r, n) = (1 - (1 + r)^(-n)) / r
  payment = principal / PVA(r, n)
"""

from typing import Tuple


class MortgagePayment:
    """
    Fixed-rate Canadian mortgage calculator.

    Encapsulation choice:
    - I store the APR (%) and amortization years as "private" members
      so nothing else can change them without validation.
    """

    # constructor
    def __init__(self, quoted_rate_percent: float, amort_years: int) -> None:
        """
        quoted_rate_percent: APR quoted with SEMI-ANNUAL compounding (e.g., 5.5 for 5.5%)
        amort_years: whole years (e.g., 25)
        """
        self.__quoted_rate_pct: float = 0.0
        self.__amort_years: int = 0
        self.set_rate_percent(quoted_rate_percent)
        self.set_amort_years(amort_years)

    # helper: present-value factor
    @staticmethod
    def _pva(r: float, n: int) -> float:
        """Present value of an annuity-immediate. Handles r = 0."""
        if r == 0:
            return float(n)
        return (1.0 - (1.0 + r) ** (-n)) / r

    # helper: nominal → effective annual
    @staticmethod
    def _semi_to_effective_annual(j: float) -> float:
        """Convert nominal j (semi-annual) to effective annual rate (EAR)."""
        return (1.0 + j / 2.0) ** 2 - 1.0

    # helper: effective annual → per-period rate
    @staticmethod
    def _effective_to_periodic(ear: float, m: int) -> float:
        """Convert EAR to a per-period rate for m payments per year."""
        return (1.0 + ear) ** (1.0 / m) - 1.0

    # calculate payment for one frequency
    def _payment_given_frequency(self, principal: float, m_per_year: int) -> float:
        """Compute the level payment for a given payment frequency."""
        j = self.__quoted_rate_pct / 100.0
        ear = self._semi_to_effective_annual(j)
        r = self._effective_to_periodic(ear, m_per_year)
        n = m_per_year * self.__amort_years
        return principal / self._pva(r, n)

    # public method: return all six payments
    def payments(self, principal: float) -> Tuple[float, float, float, float, float, float]:
        """
        Returns (monthly, semi_monthly, bi_weekly, weekly, rapid_bi_weekly, rapid_weekly)
        after rounding to two decimals.
        """
        if not isinstance(principal, (int, float)):
            raise TypeError("principal must be an int or float")
        if principal < 0:
            raise ValueError("principal must be non-negative")

        monthly = self._payment_given_frequency(principal, 12)
        semi_monthly = self._payment_given_frequency(principal, 24)
        bi_weekly = self._payment_given_frequency(principal, 26)
        weekly = self._payment_given_frequency(principal, 52)

        rapid_bi_weekly = monthly / 2.0
        rapid_weekly = monthly / 4.0

        r2 = lambda x: round(x + 1e-9, 2)
        return (
            r2(monthly),
            r2(semi_monthly),
            r2(bi_weekly),
            r2(weekly),
            r2(rapid_bi_weekly),
            r2(rapid_weekly),
        )

    # setter methods
    def set_rate_percent(self, quoted_rate_percent: float) -> None:
        if not isinstance(quoted_rate_percent, (int, float)):
            raise TypeError("quoted_rate_percent must be an int or float")
        if quoted_rate_percent < 0 or quoted_rate_percent > 100:
            raise ValueError("quoted_rate_percent must be between 0 and 100")
        self.__quoted_rate_pct = float(quoted_rate_percent)

    def set_amort_years(self, amort_years: int) -> None:
        if not isinstance(amort_years, int):
            raise TypeError("amort_years must be an int")
        if amort_years <= 0 or amort_years > 100:
            raise ValueError("amort_years must be between 1 and 100")
        self.__amort_years = amort_years

    # getter methods
    def get_rate_percent(self) -> float:
        """Return the stored annual interest rate."""
        return self.__quoted_rate_pct

    def get_amort_years(self) -> int:
        """Return the stored amortization period in years."""
        return self.__amort_years


# quick self-test so I can verify it runs by itself
if __name__ == "__main__":
    mp = MortgagePayment(quoted_rate_percent=5.5, amort_years=25)
    result = mp.payments(100_000.0)
    print(result)  # Expected: (610.39, 304.85, 281.38, 140.61, 305.20, 152.60)

