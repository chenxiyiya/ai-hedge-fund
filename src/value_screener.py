import argparse
import math
from datetime import datetime

from src.tools.api import (
    get_financial_metrics,
    get_market_cap,
    search_line_items,
)

DEFAULT_LINE_ITEMS = [
    "earnings_per_share",
    "book_value_per_share",
    "outstanding_shares",
]


def compute_margin_of_safety(line_item, market_cap: float) -> float | None:
    eps = getattr(line_item, "earnings_per_share", None)
    bvps = getattr(line_item, "book_value_per_share", None)
    shares = getattr(line_item, "outstanding_shares", None)
    if eps and bvps and shares and market_cap and market_cap > 0:
        graham_number = math.sqrt(22.5 * eps * bvps)
        price = market_cap / shares
        if price > 0:
            return (graham_number - price) / price
    return None


def score_stock(ticker: str, end_date: str) -> dict | None:
    metrics = get_financial_metrics(
        ticker,
        end_date,
        period="annual",
        limit=1,
    )
    line_items = search_line_items(
        ticker,
        DEFAULT_LINE_ITEMS,
        end_date,
        period="annual",
        limit=1,
    )
    market_cap = get_market_cap(ticker, end_date)

    if not metrics or not line_items or market_cap is None:
        return None

    fm = metrics[0]
    li = line_items[0]

    score = 0
    reasons = []

    if fm.price_to_earnings_ratio and fm.price_to_earnings_ratio < 15:
        score += 1
        reasons.append(f"P/E {fm.price_to_earnings_ratio:.1f} < 15")
    if fm.price_to_book_ratio and fm.price_to_book_ratio < 1.5:
        score += 1
        reasons.append(f"P/B {fm.price_to_book_ratio:.1f} < 1.5")
    if fm.debt_to_assets and fm.debt_to_assets < 0.5:
        score += 1
        reasons.append(f"Debt/Assets {fm.debt_to_assets:.2f} < 0.5")
    if fm.current_ratio and fm.current_ratio > 1.5:
        score += 1
        reasons.append(f"Current ratio {fm.current_ratio:.2f} > 1.5")

    mos = compute_margin_of_safety(li, market_cap)
    if mos is not None and mos > 0.3:
        score += 2
        reasons.append(f"Margin of safety {mos:.0%}")

    if fm.revenue_growth and fm.revenue_growth > 0.05:
        score += 1
        reasons.append(f"Revenue growth {fm.revenue_growth:.0%}")
    if fm.earnings_growth and fm.earnings_growth > 0.05:
        score += 1
        reasons.append(f"Earnings growth {fm.earnings_growth:.0%}")

    return {
        "ticker": ticker,
        "score": score,
        "margin_of_safety": mos,
        "reasons": reasons,
    }


def screen_stocks(tickers: list[str], end_date: str) -> list[dict]:
    results: list[dict] = []
    for ticker in tickers:
        result = score_stock(ticker, end_date)
        if result:
            results.append(result)
    results.sort(key=lambda r: r["score"], reverse=True)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simple value investing stock screener",
    )
    parser.add_argument(
        "--tickers",
        required=True,
        help="Comma-separated tickers",
    )
    parser.add_argument(
        "--end-date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="End date for fundamental data (YYYY-MM-DD)",
    )
    args = parser.parse_args()
    tickers = [t.strip() for t in args.tickers.split(",") if t.strip()]

    results = screen_stocks(tickers, args.end_date)

    print(f"Value Screen Results as of {args.end_date}:")
    for r in results:
        mos = f"{r['margin_of_safety']:.0%}" if r["margin_of_safety"] is not None else "N/A"  # noqa: E501
        reason_str = "; ".join(r["reasons"])
        print(f"{r['ticker']:>6}: Score {r['score']}, MOS {mos} - {reason_str}")  # noqa: E501


if __name__ == "__main__":
    main()
