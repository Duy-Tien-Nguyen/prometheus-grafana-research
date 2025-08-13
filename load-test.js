import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 500 }, // Tăng lên 50 người dùng ảo trong 30s
    { duration: '2m', target: 1000 },  // Giữ 50 người dùng ảo trong 1 phút
    { duration: '30s', target: 2000 },  // Giảm về 0 trong 30s
    { duration: '30s', target: 0 },  // Giảm về 0 trong 30s
  ],
};

export default function () {
  http.get('http://localhost:8080/api/v1/heavy'); 
  sleep(1);
}