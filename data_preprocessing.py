from datetime import datetime
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
START_DATE = pd.Timestamp("2024-01-01")
END_DATE = pd.Timestamp("2026-09-25")
ACCESS_DATE = "2026-09-30"

FILES = {
	"BSR": ("BSR Historical Data.csv", "%Y/%m/%d"),
	"VNINDEX": ("VN Index Historical Data.csv", "%m/%d/%Y"),
}

SOURCE_URLS = {
	"BSR": "https://www.investing.com/equities/binh-son-refining-and-petrochemical-historical-data",
	"VNINDEX": "https://www.investing.com/indices/vn",
}


def load_series(symbol):
	filename, date_format = FILES[symbol]
	raw = pd.read_csv(DATA_DIR / filename)
	required = {"Date", "Price"}
	missing = required - set(raw.columns)
	if missing:
		raise ValueError(f"{symbol}: missing columns {sorted(missing)}")

	frame = pd.DataFrame(
		{
			"date": pd.to_datetime(raw["Date"], format=date_format, errors="coerce"),
			symbol: pd.to_numeric(
				raw["Price"].astype(str).str.replace(",", "", regex=False),
				errors="coerce",
			),
		}
	)
	checks = {
		"raw_rows": len(raw),
		"invalid_dates": int(frame["date"].isna().sum()),
		"invalid_prices": int(frame[symbol].isna().sum()),
		"non_positive_prices": int((frame[symbol] <= 0).sum()),
		"duplicate_rows": int(frame["date"].duplicated(keep=False).sum()),
	}
	if any(checks[key] for key in ("invalid_dates", "invalid_prices", "non_positive_prices", "duplicate_rows")):
		raise ValueError(f"{symbol}: validation failed: {checks}")

	frame = frame.drop_duplicates("date").sort_values("date")
	frame = frame[frame["date"].between(START_DATE, END_DATE)].reset_index(drop=True)
	if frame.empty:
		raise ValueError(f"{symbol}: no rows in requested period")
	checks.update(
		{
			"rows_in_range": len(frame),
			"first_session": frame["date"].min().strftime("%Y-%m-%d"),
			"last_session": frame["date"].max().strftime("%Y-%m-%d"),
			"is_ascending": bool(frame["date"].is_monotonic_increasing),
		}
	)
	return frame, checks


def main():
	bsr, bsr_checks = load_series("BSR")
	vnindex, vnindex_checks = load_series("VNINDEX")
	merged = bsr.merge(vnindex, on="date", how="inner", validate="one_to_one")
	merged = merged.sort_values("date").reset_index(drop=True)

	merged[["date", "BSR", "VNINDEX"]].to_csv(
		DATA_DIR / "cleaned_aligned_prices.csv", index=False, date_format="%Y-%m-%d"
	)

	bsr_dates = set(bsr["date"])
	vnindex_dates = set(vnindex["date"])
	bsr_missing_on_index = sorted(vnindex_dates - bsr_dates)
	report = [
		"BÁO CÁO TIỀN XỬ LÝ BSR - VN-INDEX",
		f"Ngày chạy: {datetime.now():%Y-%m-%d %H:%M:%S}",
		f"Ngày truy cập nguồn: {ACCESS_DATE}",
		f"Khoảng yêu cầu: {START_DATE:%Y-%m-%d} đến {END_DATE:%Y-%m-%d}",
		"",
		"Đối tượng: Y = BSR, Công ty Cổ phần Lọc Hóa dầu Bình Sơn, Energy / Oil & Gas / Refining & Petrochemicals.",
		"BSR: giao dịch trên HOSE trong giai đoạn sau khi chuyển niêm yết từ UPCOM sang HOSE.",
		"Đối tượng: X = VN-Index, chỉ số giá thị trường cổ phiếu tại HOSE; VN-Index không phải một sàn giao dịch.",
		f"Nguồn BSR: Investing.com - {SOURCE_URLS['BSR']}",
		f"Nguồn VN-Index: Investing.com - {SOURCE_URLS['VNINDEX']}",
		"Loại giá: dùng cột Price của Investing.com cho cả hai chuỗi; đây là giá đóng cửa, không phải Adjusted Close.",
		"Đơn vị: BSR = VND/cổ phiếu; VN-Index = điểm chỉ số.",
		"",
		"Kiểm tra dữ liệu:",
		f"BSR: {bsr_checks}",
		f"VN-Index: {vnindex_checks}",
		f"01/01/2024 là ngày lễ; phiên đầu thực tế: BSR={bsr_checks['first_session']}, VN-Index={vnindex_checks['first_session']}.",
		f"25/09/2026: phiên cuối thực tế: BSR={bsr_checks['last_session']}, VN-Index={vnindex_checks['last_session']}.",
		f"Ngày VN-Index có nhưng BSR không có: {len(bsr_missing_on_index)} ngày.",
		"Các ngày thiếu không tự động được kết luận là BSR tạm ngừng giao dịch; có thể do lịch thị trường hoặc dữ liệu nguồn.",
		"Danh sách ngày VN-Index có nhưng BSR thiếu: " + ", ".join(d.strftime("%Y-%m-%d") for d in bsr_missing_on_index),
		"",
		f"Số phiên BSR sau lọc: {len(bsr)}",
		f"Số phiên VN-Index sau lọc: {len(vnindex)}",
		f"Số ngày bị loại khi đồng bộ: BSR-only={len(bsr_dates - vnindex_dates)}, VNINDEX-only={len(vnindex_dates - bsr_dates)}",
		f"N quan sát giá dùng chung: {len(merged)}.",
		"Không nội suy và không forward-fill ngày thiếu; log return sẽ được tính ở notebook.",
		"",
		"Đầu ra: cleaned_aligned_prices.csv, processing_log.txt",
	]
	(DATA_DIR / "processing_log.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
	print(f"N giá dùng chung: {len(merged)}")
	print(f"Ngày VN-Index có nhưng BSR thiếu: {len(bsr_missing_on_index)}")


if __name__ == "__main__":
	main()
