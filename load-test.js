import http from 'k6/http';
import { check, sleep } from 'k6';
import { randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// --- TÙY CHỈNH KỊCH BẢN TẢI ---
export const options = {
  stages: [
    // Giai đoạn 1: Tăng tải từ từ lên 100 người dùng ảo trong 30 giây
    { duration: '30s', target: 100 },
    // Giai đoạn 2: Giữ ổn định 100 người dùng ảo trong 1 phút để hệ thống bão hòa
    { duration: '1m', target: 100 },
    // Giai đoạn 3: Tạo một đợt tăng tải đột biến (spike) lên 500 người dùng ảo trong 30 giây
    { duration: '30s', target: 500 },
    // Giai đoạn 4: Giữ ổn định ở mức tải cao trong 1 phút
    { duration: '1m', target: 500 },
    // Giai đoạn 5: Giảm tải về 0 trong 30 giây để xem hệ thống hồi phục
    { duration: '30s', target: 0 },
  ],
  // Tùy chọn ngưỡng (thresholds) để k6 báo cáo pass/fail
  thresholds: {
    'http_req_failed': ['rate<0.01'], // Tỷ lệ lỗi phải dưới 1%
    'http_req_duration': ['p(95)<500'], // 95% yêu cầu phải hoàn thành dưới 500ms
  },
};

// --- HÀM CHÍNH THỰC THI BÀI TEST ---
export default function () {
  // Danh sách các endpoint để lựa chọn ngẫu nhiên
  const endpoints = [
    'kafka',
    'minio',
    'redis'
  ];
  
  // Chọn ngẫu nhiên một endpoint từ danh sách trên
  const randomEndpoint = endpoints[randomIntBetween(0, endpoints.length - 1)];
  const url = `http://localhost:8080/send-message/${randomEndpoint}/`;

  // Tạo một payload JSON để gửi đi
  // Dùng __VU và __ITER để đảm bảo mỗi message có id duy nhất
  const payload = JSON.stringify({
    id: __VU * 10000 + __ITER, // Virtual User ID và Iteration number
    content: `k6 load test message to ${randomEndpoint}`
  });

  // Thiết lập header cho yêu cầu POST
  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  // Gửi yêu cầu POST
  const res = http.post(url, payload, params);

  // Kiểm tra (check) xem yêu cầu có thành công không (status code là 200)
  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  // Đợi 1 giây giữa các lần lặp
  sleep(1);
}