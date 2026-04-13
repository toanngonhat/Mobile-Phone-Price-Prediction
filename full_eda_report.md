# Báo cáo Phân tích Khám phá Dữ liệu (EDA) và Đề xuất Feature Engineering

Báo cáo giải trình quá trình Data Scientist phân tích bộ dữ liệu `sample_phone_data.csv` (Blank Slate). Mục tiêu là dựa hoàn toàn vào các bằng chứng toán học/thống kê để định hướng cấu trúc dữ liệu, và đưa ra quyết định loại bỏ (Drop) hay giữ lại (Keep) từng đặc trưng cho mô hình dự đoán AI.

## 1. Missing Values Heatmap

![Missing Values](file:///D:/HCMUT/HK252/IS/Assignment/phone-price-predict/Mobile-Phone-Price-Prediction/reports/01_missing_values.png)

- **Ý nghĩa & Phân tích:** Tập dữ liệu gốc tồn tại nhiều khoảng trắng rỗng (Dải màu vàng) nằm rải rác trên các cột. Việc đưa dữ liệu khuyết thiếu vào các mô hình hồi quy sẽ gây lỗi.
- **Kết luận Data Engineering:** Thiết lập Pipeline áp dụng `SimpleImputer`, lấp Median cho các Biến Số và Mode cho Biến Phân loại.

## 2. Normalized Used Price Distribution

![Distribution](file:///D:/HCMUT/HK252/IS/Assignment/phone-price-predict/Mobile-Phone-Price-Prediction/reports/02_price_distribution.png)

- **Ý nghĩa & Phân tích:** Phân phối của biến cần dự đoán đang mang hình hài quả chuông (Gaussian Distribution).
- **Kết luận Data Engineering:** Thuật toán tự học AI ưa chuộng phân phối chuẩn vì nó hạn chế Overfitting. Biến đích đã xử lý Logarit đạt chuẩn.

## 3. Brand vs Used Price Boxplot

![Boxplot](file:///D:/HCMUT/HK252/IS/Assignment/phone-price-predict/Mobile-Phone-Price-Prediction/reports/03_brand_boxplot.png)

- **Ý nghĩa & Phân tích:** Boxplot rất so le nhau (Apple và Samsung ở mốc giá trị cao hơn hẳn so với Xiaomi/Oppo).
- **Kết luận Feature Selection:** Thương hiệu đóng vai trò phân tầng cốt lõi. **Giữ lại cột `device_brand`**.

## 4. Hardware vs Price Scatterplots

![Scatter Plots](file:///D:/HCMUT/HK252/IS/Assignment/phone-price-predict/Mobile-Phone-Price-Prediction/reports/04_hardware_scatter.png)

- **Ý nghĩa & Phân tích:** Scatterplot tìm Tương quan Tuyến tính (Linear Correlation). Điểm ảnh phân bố dốc lên báo hiệu Tín hiệu (Signal).
- **Kết luận Feature Selection:** Cả RAM và Bộ nhớ (Storage) đều tạo thành mây nghiêng lên. **Chắc chắn giữ lại `ram` và `internal_memory`**.

## 5. Pearson Correlation Target Variables

![Correlation Plot](file:///D:/HCMUT/HK252/IS/Assignment/phone-price-predict/Mobile-Phone-Price-Prediction/reports/05_correlation_plot.png)

- **Ý nghĩa & Phân tích:** Chấm điểm Pearson của các ứng viên đối với Giá Mục tiêu. Biểu đồ chỉ ra `normalized_new_price` (Giá định mức gốc) có hệ số quá cao (>0.85).
- **Kết luận Feature Selection:** Cột Giá mới làm ô nhiễm dự báo bằng Rò Rỉ Dữ liệu (Data Leakage Trap). **Bắt buộc Xoá bỏ cột `normalized_new_price`**.

## 6. Random Forest Feature Importance

![Feature Importance Plot](file:///D:/HCMUT/HK252/IS/Assignment/phone-price-predict/Mobile-Phone-Price-Prediction/reports/06_feature_importance.png)

- **Ý nghĩa & Phân tích:** Cây phân cấp Random Forest mổ xẻ phần trăm đóng góp làm chìa khoá cắt rẽ nhánh dự đoán (Information Gain).
- **Kết luận Feature Selection:** Nổi bật ở ngưỡng đáy biểu đồ: Tính năng `front_camera_mp` (Camera Cảm biến Phía trước) và `weight` (Trọng Lượng) chiếm <3%. Cần thiết **Loại bỏ `front_camera_mp`, `weight`** hòng tối giản nhiễu hạt.

## 7. Correlation Heatmap Matrix

![Correlation Matrix](file:///D:/HCMUT/HK252/IS/Assignment/phone-price-predict/Mobile-Phone-Price-Prediction/reports/07_correlation_matrix.png)

- **Ý nghĩa & Phân tích:** Ma trận bao trùm Đo lường Chéo (Cross-feature multicollinearity). Cột có độ nóng cao sẽ làm lặp kiến thức của nhau.
- **Kết luận Feature Selection:** Thấy cực kỳ rõ `os` là bản sao trực tiếp phụ thuộc Hãng `device_brand` (Multicollinearity). Hệ quả: **Vứt bỏ cột `os`**.

## 8. Brand Market Share Countplot

![Brand Market Share](file:///D:/HCMUT/HK252/IS/Assignment/phone-price-predict/Mobile-Phone-Price-Prediction/reports/08_brand_market_share.png)

- **Ý nghĩa & Phân tích:** Countplot bóc phốt tình trạng Mất Cân Bằng Dữ Liệu Thiểu Số (Data Imbalance). Rất nhiều Brand lớn vắng bóng hoàn toàn ở đỉnh giá và đỉnh số lượng.
- **Kết luận Data Engineering:** Nảy sinh yêu cầu dùng Sinh Dữ Kiện Nhân Tạo (Synthetic Generation) nhằm vá lỗi cho các Feature của iPhone để hệ thống đào tạo trung lập.

## 9. Price vs Release Year Trend Lineplot

![Release Year Trend](file:///D:/HCMUT/HK252/IS/Assignment/phone-price-predict/Mobile-Phone-Price-Prediction/reports/09_price_vs_year_trend.png)

- **Ý nghĩa & Phân tích:** Đồ thị Lineplot nối tuyến trục thời gian làm thấu hiểu xu thế Khấu Hao (Time-series Depreciation). Có nếp gập (vực thẳm) từ trước năm 2017 chứng tỏ niên đại tỷ lệ nghịch với tầm giá hiện hành.
- **Kết luận Feature Selection:** Thông số Khấu Hao vạch rõ năng xuất định hình biểu giá. **Luận chứng Giữ Lại Dứt Khoát Cột `release_year` và `days_used`**.

## 10. Hardware Distribution Histograms

![Hardware Distribution](file:///D:/HCMUT/HK252/IS/Assignment/phone-price-predict/Mobile-Phone-Price-Prediction/reports/10_hardware_distribution.png)

- **Ý nghĩa & Phân tích:** Histogram phân loại dung lượng. Sóng dữ liệu tụ hội mạnh ở biên mốc RAM 4GB cũng như biên độ mốc PIN 3000 mAh.
- **Kết luận Data Engineering:** Tính chất co cụm (Long tail distribution) phản ứng cần cẩn trọng nếu phải Inference một con điện thoại siêu cứng RAM trên 12GB do thiếu hụt điểm tựa (Outliers).

---

# TỔNG KẾT: ĐỀ XUẤT FEATURE ENGINEERING CUỐI CÙNG

Tổng hợp toàn bộ phán quyết phân tích khách quan (Blank Slate EDA), mô hình được cấu trúc thành:

### ❌ Đặc trưng Bắt Buộc Loại Bỏ (Noise / Leakage Multicollinearity)

1. **`normalized_new_price`**: Xóa (Tránh bãi mìn Rò rỉ Dữ liệu Target Leakage).
2. **`os`**: Xóa (Trùng lặp Multicollinearity sinh ra cản trở).
3. **`weight`** và **`front_camera_mp`**: Xóa (Feature Importance quá thấp, giữ lại nhiễu đường truyền phân tích).

### 💎 Đặc trưng Cốt Lõi Dự Đoán Giá (Core Features - Đề Xuất Giữ Lại 8 Thông Số)
>
> **`device_brand`** (Nhận diện Thương Hiệu định hướng qua Boxplot)
> **`ram`**, **`internal_memory`** (Vũ khí cấu trúc lực tuyến tính qua Scatterplot)
> **`battery`**, **`screen_size`**, **`rear_camera_mp`** (Khung phần cứng cơ sở thiết yếu trên Ranking Cây Quyết Định)
> **`release_year`**, **`days_used`** (Nòng cốt Khấu hao vòng đời công nghệ qua Lineplot).
