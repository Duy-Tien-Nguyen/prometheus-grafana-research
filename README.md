Chắc chắn rồi! Đây là toàn bộ nội dung README đã được định dạng lại hoàn chỉnh bằng Markdown. Bạn có thể sao chép và dán trực tiếp vào file `README.md` trên GitHub.

---
```markdown
# Blueprint Giám sát Hệ thống với Prometheus & Grafana

Đây là kho lưu trữ mã nguồn thực nghiệm cho đề tài nghiên cứu khoa học: **"Ứng dụng Prometheus, Grafana trong Giám sát, Đánh giá Hiệu năng và Trạng thái của Hệ thống theo Thời gian thực"**.

## 📖 Tổng quan

Dự án này cung cấp một **blueprint "chìa khóa trao tay"** để nhanh chóng triển khai một hệ thống giám sát toàn diện cho một stack ứng dụng backend điển hình. Giải pháp sử dụng các công nghệ mã nguồn mở tiêu chuẩn ngành:
- **Prometheus:** Thu thập và lưu trữ dữ liệu metrics.
- **Grafana:** Trực quan hóa dữ liệu thông qua các dashboard chuyên biệt.
- **Alertmanager:** Xử lý và gửi các cảnh báo chủ động.
- **Docker & Docker Compose:** Đóng gói và triển khai toàn bộ hệ thống.

Mục tiêu của blueprint này là cung cấp một môi trường tham chiếu, có khả năng tái lập cao, phục vụ cho việc học tập, nghiên cứu và có thể làm nền tảng để phát triển cho các hệ thống trong thực tế.

## 🏛️ Kiến trúc Hệ thống

Hệ thống được thiết kế theo kiến trúc kéo (*pull-based*) với các thành phần được module hóa:

*(Ghi chú: Hãy chèn hình ảnh sơ đồ kiến trúc của bạn vào đây.)*
![Sơ đồ Kiến trúc](link_den_hinh_anh_kien_truc.png)

1.  **Exporters:** Thu thập metrics từ các dịch vụ.
2.  **Prometheus Server:** Chủ động "kéo" (scrape) metrics từ các Exporter.
3.  **Grafana:** Truy vấn (query) dữ liệu từ Prometheus và hiển thị trên các dashboard.
4.  **Alertmanager:** Nhận cảnh báo từ Prometheus và gửi thông báo qua các kênh đã cấu hình.

## 🚀 Hướng dẫn Khởi chạy

Để tái tạo lại toàn bộ môi trường thực nghiệm, vui lòng làm theo các bước sau.

### 1. Yêu cầu Hệ thống
- [Docker](https://docs.docker.com/get-docker/) (phiên bản 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (phiên bản V2+)
- Git

### 2. Cấu hình Email cho Alertmanager (Bước Bắt buộc)

Để tính năng cảnh báo qua email hoạt động, bạn cần chỉnh sửa trực tiếp file cấu hình của Alertmanager.

**a. Mở file:**
`alertmanager/alertmanager.yml`

**b. Tìm và thay thế các giá trị:**
Tìm đến khối `global` và điền vào thông tin máy chủ SMTP của bạn. Dưới đây là ví dụ sử dụng Gmail với Mật khẩu Ứng dụng:

```yaml
global:
  # THAY THẾ CÁC GIÁ TRỊ DƯỚI ĐÂY
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'your-email@gmail.com'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-16-char-app-password' # <-- Dùng Mật khẩu Ứng dụng của Google
  smtp_require_tls: true

# ...
receivers:
  - name: 'email-alert'
    email_configs:
      - to: 'recipient-email@example.com' # <-- THAY THẾ EMAIL SẼ NHẬN CẢNH BÁO
        send_resolved: true
        # ...
```

> ⚠️ **CẢNH BÁO BẢO MẬT QUAN TRỌNG:**
> File `alertmanager.yml` hiện đang chứa thông tin nhạy cảm của bạn. **TUYỆT ĐỐI KHÔNG COMMIT** file này lên kho lưu trữ Git công khai.

### 3. Cấp quyền cho Thư mục Dữ liệu (Bước Bắt buộc cho Linux/macOS)

Alertmanager container chạy với một user không phải `root` và cần quyền ghi vào thư mục dữ liệu của nó. Vì chúng ta sử dụng bind mount, bạn cần phải cấp quyền ghi cho thư mục `alertmanager_data` trên máy host của mình.

**a. Tạo thư mục (nếu chưa có):**
```bash
mkdir -p alertmanager_data
```

**b. Cấp quyền ghi:**
Chạy lệnh sau trong terminal tại thư mục gốc của dự án:
```bash
chmod -R 777 alertmanager_data
```
Lệnh này sẽ cấp toàn quyền ghi cho thư mục, đảm bảo Alertmanager có thể lưu trữ trạng thái hoạt động của nó.

### 4. Khởi chạy Hệ thống

Sau khi đã hoàn tất các bước cấu hình, hãy khởi chạy toàn bộ stack bằng lệnh sau:
```bash
docker-compose up -d --build
```
Hệ thống sẽ mất vài phút để khởi động. Bạn có thể kiểm tra trạng thái bằng lệnh `docker-compose ps`.

### 5. Truy cập các Dịch vụ

Khi hệ thống đã khởi động thành công, bạn có thể truy cập các giao diện qua trình duyệt:

- **Grafana:** `http://localhost:3010` (đăng nhập: `admin`/`admin`)
- **Prometheus:** `http://localhost:9090`
- **Alertmanager:** `http://localhost:9093`

Grafana đã được cấu hình để tự động nạp (provisioning) nguồn dữ liệu Prometheus và toàn bộ bộ sưu tập dashboard mẫu.

## 🔬 Thực hiện các Kịch bản Đánh giá

Repo này bao gồm các kịch bản được sử dụng trong Chương 4 của báo cáo.

### Kịch bản 1: Tăng tải Đột biến
Sử dụng công cụ **k6**.
```bash
# Cài đặt k6 nếu chưa có
# Chạy bài kiểm thử tải
k6 run load-test.js
```
Quan sát các dashboard Tổng quan và Nginx để thấy sự thay đổi.

### Kịch bản 2: Sự cố Cạn kiệt Tài nguyên
Sử dụng công cụ **stress-ng**.
```bash
# Cài đặt stress-ng nếu chưa có (ví dụ: sudo apt-get install stress-ng)
# Tạo tải 100% trên 4 cores trong 140 giây
stress-ng --cpu 4 --timeout 140s
```
Quan sát dashboard Tổng quan và kiểm tra email để xem chu trình cảnh báo.

## 📁 Cấu trúc Thư mục

- **`docker-compose.yml`**: File "nhạc trưởng" định nghĩa và kết nối toàn bộ các dịch vụ.
- **`alertmanager/`**: Chứa cấu hình (`alertmanager.yml`) và template email tùy chỉnh (`templates/`).
- **`api/`**: Mã nguồn của ứng dụng API giả lập được sử dụng để kiểm thử tải.
- **`grafana/provisioning/`**: Chứa các file cấu hình để Grafana tự động nạp datasources và dashboards.
- **`load-test.js`**: Kịch bản kiểm thử tải bằng k6.
- **`prometheus/`**: Chứa file cấu hình chính (`prometheus.yml`) và các quy tắc cảnh báo (`rules/`).

## 📄 Giấy phép (License)
Dự án này được cấp phép dưới Giấy phép MIT. Xem file `LICENSE` để biết thêm chi tiết.
