# label-app

## Cách trích xuất data từ dataset lớn

- Điều chỉnh dataset nguồn và số lượng data muốn lấy trong file extract_data.js

- Terminal: node extract_data.js

- File data.json sẽ xuất hiện nếu chương trình chạy thành công

- Kéo file data.json vào cùng nơi với file App.jsx

- Note: dataset gốc phải cùng folder của file extract_data

- Note: Đã có sẵn file data.json không cần thực hiện bước này

## Run

- Terminal: npm run dev

- Lúc này hiện ra Local: http://localhost:xxxx/. Đây chỉ là demo chưa public chỉ phục vụ xem những thay đổi

- Muốn update lên web đã public thì Terminal: npx vercel --prod

- Lúc này hiện ra Aliased: https://my-label-app.vercel.app
