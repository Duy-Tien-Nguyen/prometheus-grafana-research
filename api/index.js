const express = require('express');
const app = express();
const port = 5000; // Cổng nội bộ của API

// Endpoint chính để bắn tải
app.get('/api/v1/ping', (req, res) => {
  res.status(200).send('Pong!');
});

// Endpoint giả lập một tác vụ nặng
app.get('/api/v1/heavy', (req, res) => {
  // Giả lập CPU load bằng một vòng lặp
  let result = 0;
  for (let i = 0; i < 50000; i++) {
    result += Math.sqrt(i);
  }
  res.status(200).send(`Heavy task done! Result: ${result}`);
});

app.listen(port, () => {
  console.log(`Simple API listening on port ${port}`);
});