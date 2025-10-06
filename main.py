"""
FINE 3300 – Assignment 1
Author: Dimitar Atanasov

File: main.py

What I do with this file:
- This is the main runner that ties my two classes together.
- First, it asks the user for mortgage details and prints all six payment types.
- Then, it asks for a currency conversion (CAD ↔ USD) and shows the result.
- It handles bad inputs by asking again instead of crashing.

Concepts from class I used here:
- input() and print() for user interaction
- loops and try/except for validation
- importing and using my own modules
"""

from mortgage import MortgagePayment
from exchange_rates import ExchangeRates
import glob


# getting numeric inputs safely
def _get_float(prompt: str, positive_only: bool = True) -> float:
    """Keep asking until the user gives a valid float (and positive if required)."""
    while True:
        try:
            value = float(input(prompt).strip())
            if positive_only and value <= 0:
                print("Invalid input. Please enter a positive number.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a numeric value.")


def _get_int(prompt: str, positive_only: bool = True) -> int:
    """Keep asking until the user gives a valid integer (and positive if required)."""
    while True:
        try:
            value = int(input(prompt).strip())
            if positive_only and value <= 0:
                print("Invalid input. Please enter a positive whole number.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a whole number.")


# running the mortgage part
def run_mortgage_flow() -> None:
    """Ask the user for mortgage info and display all six payment amounts."""
    print("\n=== Mortgage Payments ===")

    principal = _get_float("Enter principal amount (e.g., 500000): ")
    quoted_rate = _get_float("Enter quoted annual rate % (semi-annual compounding, e.g., 5.5): ")
    amort_years = _get_int("Enter amortization in years (e.g., 25): ")

    mp = MortgagePayment(quoted_rate_percent=quoted_rate, amort_years=amort_years)
    monthly, semi_monthly, bi_weekly, weekly, rapid_biweekly, rapid_weekly = mp.payments(principal)

    print("\n--- Results ---")
    print(f"Monthly Payment: ${monthly:,.2f}")
    print(f"Semi-monthly Payment: ${semi_monthly:,.2f}")
    print(f"Bi-weekly Payment: ${bi_weekly:,.2f}")
    print(f"Weekly Payment: ${weekly:,.2f}")
    print(f"Rapid Bi-weekly Payment: ${rapid_biweekly:,.2f}")
    print(f"Rapid Weekly Payment: ${rapid_weekly:,.2f}")


# running the exchange rate part
def _autodetect_csv() -> str | None:
    """Check if a Bank of Canada CSV file is already in this folder."""
    matches = sorted(glob.glob("BankOfCanadaExchangeRates*.csv"))
    return matches[-1] if matches else None


def run_fx_flow() -> None:
    """Ask for a conversion amount and currency pair, then show the result."""
    print("\n=== Exchange Rate Conversion (CAD ↔ USD) ===")

    csv_path = _autodetect_csv()
    if csv_path is None:
        csv_path = input("Enter path to BankOfCanadaExchangeRates.csv: ").strip()
    else:
        print(f"Using data file: {csv_path}")

    xr = ExchangeRates(csv_path)

    amount = _get_float("Enter amount (e.g., 100000): ")

    # make sure currencies are valid
    while True:
        from_ccy = input("From currency (CAD or USD): ").strip().upper()
        if from_ccy not in ("CAD", "USD"):
            print("Invalid currency. Please enter either 'CAD' or 'USD'.")
            continue
        break

    while True:
        to_ccy = input("To currency (CAD or USD): ").strip().upper()
        if to_ccy not in ("CAD", "USD"):
            print("Invalid currency. Please enter either 'CAD' or 'USD'.")
            continue
        if to_ccy == from_ccy:
            print("Cannot convert to the same currency. Try again.")
            continue
        break

    converted = xr.convert(amount, from_ccy, to_ccy)
    print("\n--- Results ---")
    print(f"{amount:,.2f} {from_ccy} = {converted:,.2f} {to_ccy}")


# main program
if __name__ == "__main__":
    # run both parts one after the other
    run_mortgage_flow()
    run_fx_flow()
