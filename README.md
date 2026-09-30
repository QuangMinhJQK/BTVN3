# BSR và VN-Index: tiền xử lý dữ liệu giá

## Đối tượng

- **Y:** BSR, Công ty Cổ phần Lọc Hóa dầu Bình Sơn, ngành Energy / Oil & Gas / Refining & Petrochemicals. BSR giao dịch trên HOSE trong giai đoạn sau khi chuyển niêm yết từ UPCOM sang HOSE.
- **X:** VN-Index, chỉ số giá thị trường cổ phiếu tại HOSE; đây là chỉ số, không phải một sàn giao dịch.

## Nguồn

Hai CSV đầu vào được tải thủ công từ cùng nguồn Investing.com:

- [BSR Historical Data](https://www.investing.com/equities/binh-son-refining-and-petrochemical-historical-data)
- [VN Index Historical Data](https://www.investing.com/indices/vn)

Ngày truy cập: **2026-09-30**.

Cột `Price` được dùng làm giá đóng cửa cho cả hai chuỗi. Dữ liệu không có `Adjusted Close`, nên dùng nhất quán giá đóng cửa do Investing.com cung cấp, không tự điều chỉnh riêng cho cổ tức. BSR tính bằng VND/cổ phiếu; VN-Index tính bằng điểm.

## Chạy

```powershell
D:/python/python.exe data_preprocessing.py
```

Script lọc khoảng 01/01/2024 đến 25/09/2026, chuẩn hóa định dạng ngày, kiểm tra giá không dương/ngày trùng/thứ tự thời gian, kiểm tra phiên đầu/cuối, ghép theo ngày chung và chốt số quan sát `N`. Script không tính log return; phần đó sẽ thực hiện ở notebook sau.

01/01/2024 là ngày lễ; phiên gần nhất thực tế của cả BSR và VN-Index là 02/01/2024. Ngày 25/09/2026 có dữ liệu ở cả hai chuỗi. Không nội suy hoặc forward-fill ngày thiếu.

## Kết quả kiểm tra

- BSR: 670 phiên, từ 02/01/2024 đến 25/09/2026.
- VN-Index: 678 phiên, từ 02/01/2024 đến 25/09/2026.
- Sau khi đồng bộ theo ngày: `N = 670` quan sát giá chung.
- Không có giá `<= 0`, ngày trùng hoặc lỗi thứ tự thời gian.
- VN-Index có dữ liệu nhưng BSR không có phiên vào 8 ngày: 07/01/2025, 08/01/2025, 09/01/2025, 10/01/2025, 13/01/2025, 14/01/2025, 15/01/2025 và 16/01/2025. Đây là các ngày cần ghi nhận để kiểm tra khả năng BSR tạm ngừng giao dịch; không tự động kết luận nguyên nhân chỉ từ dữ liệu giá.

## Đầu ra

- `data/cleaned_aligned_prices.csv`: giá BSR và VN-Index trên ngày chung.
- `data/processing_log.txt`: log nguồn, kiểm tra dữ liệu, tổng số phiên, ngày bị loại và N.

Ngày VN-Index có dữ liệu nhưng BSR không có được liệt kê trong log. Đây là ngày thiếu quan sát của BSR, không tự động chứng minh BSR bị đình chỉ giao dịch.
