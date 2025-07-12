# FAQ Chatbot với Function Calling

## Tổng quan

Dự án này đã được nâng cấp để hỗ trợ **Function Calling** - một tính năng mạnh mẽ của OpenAI cho phép AI gọi các hàm cụ thể để thực hiện các tác vụ phức tạp.

## Cải tiến chính

### 1. Trước đây (Static FAQ)
- Bot chỉ có thể trả lời dựa trên dữ liệu FAQ tĩnh
- Không thể thực hiện các tác vụ động
- Giới hạn trong việc cung cấp thông tin chi tiết

### 2. Bây giờ (Function Calling)
- Bot có thể gọi các hàm để thực hiện tác vụ cụ thể
- Có thể tìm kiếm, lọc và xử lý dữ liệu động
- Cung cấp thông tin chi tiết và cá nhân hóa

## Các chức năng hiện có

### 1. `search_faq(query)`
- **Mô tả**: Tìm kiếm trong cơ sở dữ liệu FAQ
- **Tham số**: `query` (string) - từ khóa tìm kiếm
- **Ví dụ**: "Tìm thông tin về xe điện"

### 2. `get_car_recommendations(car_type)`
- **Mô tả**: Đưa ra gợi ý xe dựa trên loại xe
- **Tham số**: `car_type` (enum) - sedan, suv, hatchback, electric
- **Ví dụ**: "Gợi ý xe SUV cho tôi"

### 3. `get_maintenance_info(service_type)`
- **Mô tả**: Cung cấp thông tin bảo dưỡng
- **Tham số**: `service_type` (enum) - oil_change, tire_rotation, brake_inspection, transmission_service, all
- **Ví dụ**: "Khi nào tôi nên thay dầu?"

### 4. `get_fuel_efficiency_tips()`
- **Mô tả**: Đưa ra các mẹo tiết kiệm nhiên liệu
- **Tham số**: Không có
- **Ví dụ**: "Cho tôi mẹo tiết kiệm nhiên liệu"

## Cấu trúc code

### `faq_data.py`
- `FAQ_LIST`: Dữ liệu FAQ gốc
- `CAR_DATABASE`: Cơ sở dữ liệu xe hơi
- `MAINTENANCE_SCHEDULE`: Lịch bảo dưỡng
- `FUEL_EFFICIENCY_TIPS`: Mẹo tiết kiệm nhiên liệu
- `FUNCTION_DEFINITIONS`: Định nghĩa các function cho OpenAI
- `AVAILABLE_FUNCTIONS`: Mapping các function thực tế

### `faq_bot.py`
- `get_faq_answer_with_functions()`: Hàm chính với function calling
- `execute_function_call()`: Thực thi function call
- `get_faq_answer()`: Hàm gốc (để tương thích ngược)

### `app.py`
- Giao diện Gradio với 2 tab:
  - **Function Calling Bot**: Sử dụng function calling
  - **Simple Bot**: Sử dụng phương pháp truyền thống

## Cách sử dụng

### 1. Chạy ứng dụng
```bash
python app.py
```

### 2. Test function calling
```bash
python test_functions.py
```

### 3. Các câu hỏi mẫu
- "Gợi ý cho tôi xe SUV"
- "Khi nào tôi nên thay dầu?"
- "Cho tôi mẹo tiết kiệm nhiên liệu"
- "Tìm thông tin về xe điện"
- "Xe sedan nào tốt?"

## Lợi ích của Function Calling

1. **Linh hoạt**: Bot có thể thực hiện nhiều tác vụ khác nhau
2. **Chính xác**: Dữ liệu được lấy từ các function cụ thể
3. **Mở rộng**: Dễ dàng thêm function mới
4. **Cá nhân hóa**: Có thể lọc và tùy chỉnh thông tin
5. **Tích hợp**: Có thể kết nối với API bên ngoài

## Mở rộng tương lai

### Các function có thể thêm:
- `get_car_prices()`: Lấy giá xe từ API
- `calculate_loan()`: Tính toán khoản vay
- `find_dealers()`: Tìm đại lý gần nhất
- `check_recall()`: Kiểm tra thông báo thu hồi
- `get_reviews()`: Lấy đánh giá xe

### Tích hợp API bên ngoài:
- API giá xe thời gian thực
- API thông tin giao thông
- API dự báo thời tiết (cho lời khuyên lái xe)
- API bản đồ (tìm trạm xăng, garage)

## Cấu hình môi trường

Thêm vào `.env`:
```
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://
MODEL_NAME=GPT-4o-mini
MAX_TOKENS=200
TEMPERATURE=0.5

# Retry mechanism configuration
RETRY_ATTEMPTS=3
RETRY_WAIT_MIN=1
RETRY_WAIT_MAX=10
```

## Cơ chế Retry với Tenacity

### Tại sao cần Retry?
- **Mạng không ổn định**: Kết nối có thể bị gián đoạn
- **Rate limiting**: API có thể giới hạn số request
- **Server overload**: Server có thể quá tải tạm thời
- **Timeout**: Request có thể timeout do network latency

### Cấu hình Retry
```python
@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),  # Tối đa 3 lần thử
    wait=wait_exponential(multiplier=1, min=RETRY_WAIT_MIN, max=RETRY_WAIT_MAX),  # Exponential backoff
    retry=retry_if_exception_type((openai.APIError, openai.RateLimitError, openai.APITimeoutError, ConnectionError)),
    reraise=True
)
```

### Các loại lỗi được retry:
- `openai.APIError`: Lỗi API chung
- `openai.RateLimitError`: Vượt quá giới hạn request
- `openai.APITimeoutError`: Timeout
- `ConnectionError`: Lỗi kết nối mạng

### Exponential Backoff:
- Lần thử 1: Ngay lập tức
- Lần thử 2: Đợi 1-2 giây
- Lần thử 3: Đợi 2-4 giây
- Tối đa: 10 giây

### Test Retry:
```bash
python test_retry.py
```
