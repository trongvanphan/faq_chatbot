# 🚗 Câu Hỏi Demo Chatbot Ô Tô - Tiếng Việt (Có Guardrail)

**🆕 Phiên bản mới với Guardrail và trả lời hoàn toàn bằng tiếng Việt**

---

## 🔍 1. TƯ VẤN MUA XE (Car Recommendations)

### Theo Ngân Sách
```
"Tôi muốn mua xe với ngân sách 800 triệu, xe nào phù hợp?"
```

```
"Xe nào tốt nhất dưới 1 tỷ đồng cho gia đình 4 người?"
```

```
"Gợi ý xe luxury trong tầm 2 tỷ cho doanh nhân"
```

### Theo Mục Đích Sử Dụng
```
"Xe nào tiết kiệm nhiên liệu cho việc đi làm hàng ngày?"
```

```
"Tôi cần xe để đi du lịch gia đình cuối tuần, xe nào phù hợp?"
```

```
"Xe nào tốt cho việc kinh doanh và gặp khách hàng?"
```

```
"Gợi ý xe phù hợp cho người mới lái"
```

### Theo Đặc Tính Cụ Thể
```
"Xe nào có công nghệ an toàn cao nhất hiện tại?"
```

```
"Tôi muốn xe có tính năng thông minh và kết nối hiện đại"
```

```
"Xe hybrid nào đáng mua nhất ở Việt Nam?"
```

```
"Xe 7 chỗ nào bán chạy nhất và đáng tin cậy?"
```

---

## 📚 2. TÌM KIẾM THÔNG TIN (Document Search)

### Thông Tin Chung
```
"Cho tôi biết về lịch bảo dưỡng xe định kỳ"
```

```
"Thông tin về bảo hành xe ô tô như thế nào?"
```

```
"Các tính năng an toàn cần có trên xe hiện đại"
```

```
"Cách tiết kiệm nhiên liệu khi lái xe"
```

### Thông Tin Xe Cụ Thể
```
"Thông số kỹ thuật của Honda Civic"
```

```
"Tính năng nổi bật của Toyota Camry"
```

```
"So sánh Mazda CX-5 và Honda CR-V"
```

```
"Đánh giá xe Vinfast Lux A2.0"
```

### Kiến Thức Kỹ Thuật
```
"Phân biệt động cơ xăng và diesel"
```

```
"Hệ thống phanh ABS hoạt động như thế nào?"
```

```
"Tìm hiểu về hệ thống treo độc lập"
```

```
"Công nghệ hybrid và electric khác nhau thế nào?"
```

---

## 📰 3. TIN TỨC Ô TÔ (News Search)

### Tin Tức Chung
```
"Tin tức mới nhất về ngành ô tô Việt Nam"
```

```
"Xu hướng xe điện tại Việt Nam hiện nay"
```

```
"Chính sách thuế xe ô tô mới nhất"
```

### Công Nghệ & Xu Hướng
```
"Cập nhật mới nhất về xe tự lái"
```

```
"Công nghệ an toàn mới trên ô tô năm 2025"
```

```
"Phát triển pin xe điện mới nhất"
```

### Thị Trường
```
"Giá xe ô tô có xu hướng thay đổi như thế nào?"
```

```
"Xe nào đang hot nhất trên thị trường Việt Nam?"
```

```
"Dự báo thị trường ô tô Việt Nam 2025"
```

---

## 🎯 4. CÂU HỎI SO SÁNH & PHỨC TạP

### So Sánh Trực Tiếp
```
"So sánh Honda City và Toyota Vios về tổng thể"
```

```
"Nên chọn Mazda 3 hay Honda Civic cho người trẻ?"
```

```
"Hyundai Tucson vs Mazda CX-5: xe nào đáng mua hơn?"
```

### Tư Vấn Phức Tạp
```
"Gia đình tôi có 2 con nhỏ, thường xuyên đi xa, ngân sách 1.2 tỷ, xe nào phù hợp?"
```

```
"Tôi làm kinh doanh, cần xe sang trọng nhưng tiết kiệm nhiên liệu, tầm 1.5 tỷ"
```

```
"Xe nào vừa phù hợp đi phố vừa có thể off-road nhẹ, giá dưới 900 triệu?"
```

### Tình Huống Cụ Thể
```
"Xe cũ hay xe mới tốt hơn với ngân sách 600 triệu?"
```

```
"Mua xe trả góp hay trả thẳng có lợi hơn?"
```

```
"Xe Nhật hay xe Hàn phù hợp với khí hậu Việt Nam hơn?"
```

---

## ❌ 5. CÂU HỎI NGOÀI CHUYÊN MÔN (Test Guardrail) 🛡️

**🆕 Đặc biệt quan trọng:** Chatbot bây giờ sẽ **TỪ CHỐI** trả lời các câu hỏi không liên quan đến ô tô!

### Để Test Khả Năng Guardrail (Sẽ bị từ chối)
```
"Hướng dẫn nấu phở bò ngon"
```

```
"Dự báo thời tiết ngày mai ở Hà Nội"
```

```
"Cách học tiếng Anh hiệu quả"
```

```
"Giá vàng hôm nay thế nào?"
```

```
"Recipe for chocolate cake"
```

**🎯 Kết quả mong đợi:** 
Chatbot sẽ trả lời: *"🚫 Xin lỗi, tôi chỉ có thể trả lời các câu hỏi liên quan đến ô tô, xe hơi và giao thông..."*

### Test Câu Hỏi Biên Giới
```
"Giá xăng hôm nay" (Nên được trả lời - liên quan đến ô tô)
```

```
"Luật giao thông mới nhất" (Nên được trả lời - liên quan đến xe)
```

```
"Xe máy nào tốt?" (Có thể bị từ chối - không phải ô tô)
```

---

## 💡 6. GỢI Ý SỬ DỤNG TRONG DEMO

### **Thứ Tự Câu Hỏi Đề Xuất:**

1. **Khởi động** (Knowledge Base):
   - "Cho tôi biết về lịch bảo dưỡng xe định kỳ"

2. **Tư vấn cơ bản** (Car Recommendations):
   - "Xe nào tốt nhất dưới 1 tỷ đồng cho gia đình 4 người?"

3. **Tư vấn nâng cao** (Car Recommendations):
   - "Gia đình tôi có 2 con nhỏ, thường xuyên đi xa, ngân sách 1.2 tỷ, xe nào phù hợp?"

4. **Tìm kiếm cụ thể** (Document Search):
   - "So sánh Mazda CX-5 và Honda CR-V"

5. **Tin tức** (News Search):
   - "Xu hướng xe điện tại Việt Nam hiện nay"

6. **Test Guardrail** 🛡️ (Error Handling):
   - "Hướng dẫn nấu phở bò ngon" (phải bị từ chối)
   - "Giá vàng hôm nay?" (phải bị từ chối)

### **Mẹo Demo:**
- Bắt đầu với câu hỏi đơn giản để làm nóng hệ thống
- Dần dần tăng độ phức tạp để show khả năng của AI
- **🆕 Test guardrail** để show chatbot từ chối câu hỏi không liên quan
- Giải thích cho khán giả biết hệ thống đang route đến agent nào
- **🇻🇳 Nhấn mạnh** tất cả câu trả lời đều bằng tiếng Việt

---

## 🆕 6. TÍNH NĂNG MỚI

### **🛡️ Guardrail Protection**
- Từ chối trả lời câu hỏi không liên quan đến ô tô
- Hướng dẫn người dùng đặt câu hỏi phù hợp
- Bảo vệ chatbot khỏi bị lạm dụng

### **🇻🇳 Full Vietnamese Support** 
- Tất cả câu trả lời bằng tiếng Việt
- Hỗ trợ từ ngữ và ngữ cảnh Việt Nam
- Đơn vị tiền tệ VNĐ (triệu, tỷ)

---

*Các câu hỏi này được thiết kế để demo đầy đủ các tính năng của chatbot ô tô, từ cơ bản đến nâng cao, bằng tiếng Việt tự nhiên.*
