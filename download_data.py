"""Download historical daily OHLCV for a ticker using yfinance.

Defaults are set to MSFT from 2021-01-01 through 2026-08-01 (inclusive).
The script is configurable via CLI arguments and writes a CSV to the data/ folder by default.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import argparse
import sys

import yfinance as yf


DEFAULT_TICKER = "MSFT"
DEFAULT_START = "2021-01-01"
DEFAULT_END = "2026-08-01"  # inclusive by default


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
	p = argparse.ArgumentParser(description="Download daily historical data with yfinance")
	p.add_argument("--ticker", default=DEFAULT_TICKER, help="Ticker symbol (default: MSFT)")
	p.add_argument("--start", default=DEFAULT_START, help="Start date (YYYY-MM-DD)")
	p.add_argument("--end", default=DEFAULT_END, help="End date (YYYY-MM-DD). Treated as inclusive by default.")
	p.add_argument("--inclusive", action="store_true", default=True, help="Treat end date as inclusive (default: True)")
	p.add_argument("--output", help="Output CSV path (defaults to data/<TICKER>_daily_<start>_<end>.csv)")
	p.add_argument("--auto-adjust", action="store_true", default=False, help="Let yfinance auto-adjust prices (split/dividend adjusted)")
	return p.parse_args(argv)


def make_output_path(base_dir: Path, ticker: str, start: str, end: str) -> Path:
	fn = f"{ticker}_daily_{start}_{end}.csv"
	return base_dir / "data" / fn


def inclusive_end_for_yfinance(end_date: str, inclusive: bool) -> str:
	"""yfinance treats the end date as exclusive. If inclusive is requested, add one day to end_date."""
	if not inclusive:
		return end_date
	try:
		end_dt = datetime.strptime(end_date, "%Y-%m-%d")
		exclusive_dt = end_dt + timedelta(days=1)
		return exclusive_dt.strftime("%Y-%m-%d")
	except ValueError:
		raise ValueError("End date must be in YYYY-MM-DD format")


def main(argv: list[str] | None = None) -> int:
	args = parse_args(argv)

	# validate dates
	try:
		datetime.strptime(args.start, "%Y-%m-%d")
	except ValueError:
		print("Start date must be in YYYY-MM-DD format", file=sys.stderr)
		return 2

	try:
		# convert to exclusive end for yfinance if inclusive requested
		yf_end = inclusive_end_for_yfinance(args.end, args.inclusive)
	except ValueError as e:
		print(str(e), file=sys.stderr)
		return 2

	out_path = Path(args.output) if args.output else make_output_path(Path(__file__).parent, args.ticker, args.start, args.end)
	out_path.parent.mkdir(parents=True, exist_ok=True)

	print(f"Downloading {args.ticker} from {args.start} to {args.end} (inclusive={args.inclusive}) -> {out_path}")

	data = yf.download(
		args.ticker,
		start=args.start,
		end=yf_end,
		interval="1d",
		auto_adjust=args.auto_adjust,
		progress=False,
	)

	if data.empty:
		print(f"No data was downloaded for {args.ticker}.", file=sys.stderr)
		return 1

	data.to_csv(out_path)
	print(f"Downloaded {len(data)} daily rows for {args.ticker} to {out_path}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
