import json

# Sample FAQ data: Replace with your actual questions and answers
FAQ_LIST = [
    {"question": "Tôi nên cân nhắc những yếu tố nào khi mua một chiếc xe hơi mới?", "answer": "Khi mua xe mới, bạn nên xem xét ngân sách, mục đích sử dụng (gia đình, đi làm, off-road), loại xe (sedan, SUV, hatchback), mức tiêu thụ nhiên liệu, tính năng an toàn, công nghệ tích hợp, chi phí bảo dưỡng và giá trị bán lại."},
    {"question": "Xe điện (EV) có thực sự là tương lai của ngành ô tô không? Ưu và nhược điểm của chúng là gì?", "answer": "Xe điện được coi là một phần quan trọng của tương lai ngành ô tô do giảm phát thải và chi phí vận hành thấp hơn. Ưu điểm bao gồm thân thiện môi trường, chi phí nhiên liệu thấp, vận hành êm ái. Nhược điểm là phạm vi hoạt động giới hạn, thời gian sạc, cơ sở hạ tầng sạc chưa đồng bộ và giá mua ban đầu thường cao hơn."},
    {"question": "Làm thế nào để duy trì và kéo dài tuổi thọ cho chiếc xe của tôi?", "answer": "Để duy trì và kéo dài tuổi thọ xe, bạn cần tuân thủ lịch bảo dưỡng định kỳ của nhà sản xuất, thay dầu nhớt và bộ lọc đúng hạn, kiểm tra lốp xe thường xuyên, giữ vệ sinh xe sạch sẽ cả bên trong và bên ngoài, và lái xe cẩn thận."},
    {"question": "Sự khác biệt giữa xe số sàn và xe số tự động là gì? Tôi nên chọn loại nào?", "answer": "Xe số sàn yêu cầu người lái phải tự điều khiển côn và sang số, mang lại cảm giác lái thể thao và kiểm soát tốt hơn. Xe số tự động tự động thay đổi số, dễ lái hơn, đặc biệt trong giao thông đô thị. Lựa chọn phụ thuộc vào sở thích cá nhân, kỹ năng lái và điều kiện lái xe thường xuyên của bạn."},
    {"question": "Công nghệ xe tự lái hiện nay đang ở mức độ nào và khi nào chúng ta có thể thấy chúng phổ biến trên đường?", "answer": "Công nghệ xe tự lái đang ở các cấp độ khác nhau, từ hỗ trợ lái nâng cao (ADAS) đến xe hoàn toàn tự lái (cấp độ 5). Hiện tại, hầu hết các xe thương mại có tính năng tự lái cấp độ 2 hoặc 3 (ví dụ: giữ làn đường, kiểm soát hành trình thích ứng). Xe tự lái hoàn toàn phổ biến có thể mất thêm một thập kỷ hoặc hơn do các thách thức về pháp lý, đạo đức và công nghệ."},
    {"question": "Khi nào thì tôi nên đưa xe đi bảo dưỡng?", "answer": "Bạn nên đưa xe đi bảo dưỡng theo lịch trình khuyến nghị của nhà sản xuất, thường được ghi trong sách hướng dẫn sử dụng xe. Ngoài ra, bạn cũng nên đưa xe đi kiểm tra khi có các dấu hiệu bất thường như tiếng ồn lạ, đèn báo lỗi trên bảng điều khiển, hoặc xe vận hành không ổn định."},
    {"question": "Giá xe hơi có xu hướng tăng hay giảm trong tương lai gần và tại sao?", "answer": "Giá xe hơi có thể bị ảnh hưởng bởi nhiều yếu tố. Trong ngắn hạn, các vấn đề về chuỗi cung ứng, lạm phát và chi phí nguyên vật liệu có thể đẩy giá lên. Về dài hạn, sự cạnh tranh gia tăng, tiến bộ công nghệ và sản xuất quy mô lớn có thể giúp giảm giá thành một số phân khúc xe, đặc biệt là xe điện."},
    {"question": "Thị trường xe cũ ở Việt Nam có đáng tin cậy không? Những điều cần lưu ý khi mua xe cũ là gì?", "answer": "Thị trường xe cũ ở Việt Nam khá sôi động nhưng cần cẩn trọng. Khi mua xe cũ, bạn nên kiểm tra kỹ lịch sử bảo dưỡng, kilomet đã đi, tình trạng động cơ, hộp số, khung gầm và hệ thống điện. Tốt nhất là nên đưa xe đến garage uy tín để kiểm tra tổng thể hoặc nhờ người có kinh nghiệm đi cùng."},
    {"question": "Làm thế nào để chọn được loại bảo hiểm xe hơi phù hợp?", "answer": "Để chọn bảo hiểm phù hợp, bạn cần xác định nhu cầu bảo vệ (bảo hiểm vật chất, bảo hiểm trách nhiệm dân sự), so sánh các gói bảo hiểm từ nhiều công ty khác nhau, xem xét mức khấu trừ, giới hạn bồi thường và các điều khoản loại trừ."},
    {"question": "Tương lai của ngành sản xuất ô tô sẽ như thế nào trong bối cảnh công nghệ và môi trường thay đổi nhanh chóng?", "answer": "Tương lai ngành ô tô sẽ tập trung mạnh vào xe điện, xe tự lái, dịch vụ di chuyển (mobility-as-a-service), và các vật liệu bền vững. Các nhà sản xuất sẽ ưu tiên R&D vào pin, phần mềm, trí tuệ nhân tạo và kết nối. Mục tiêu là tạo ra các phương tiện không chỉ hiệu quả mà còn thân thiện với môi trường và an toàn hơn."}
]

# Car database for more detailed information
CAR_DATABASE = {
    "sedan": ["Honda Civic", "Toyota Camry", "Hyundai Elantra", "Mazda3", "BMW 3 Series"],
    "suv": ["Honda CR-V", "Toyota RAV4", "Mazda CX-5", "Ford EcoSport", "Hyundai Tucson"],
    "hatchback": ["Honda Jazz", "Toyota Yaris", "Mazda2", "Kia Morning", "Hyundai i10"],
    "electric": ["VinFast VF8", "Tesla Model 3", "BMW iX3", "Hyundai Kona Electric"]
}

MAINTENANCE_SCHEDULE = {
    "oil_change": {"interval": "5000-10000 km", "description": "Thay dầu động cơ và lọc dầu"},
    "tire_rotation": {"interval": "10000-15000 km", "description": "Xoay vị trí lốp xe"},
    "brake_inspection": {"interval": "20000-30000 km", "description": "Kiểm tra phanh"},
    "transmission_service": {"interval": "40000-60000 km", "description": "Bảo dưỡng hộp số"}
}

FUEL_EFFICIENCY_TIPS = [
    "Duy trì tốc độ ổn định, tránh tăng tốc đột ngột",
    "Kiểm tra áp suất lốp định kỳ",
    "Loại bỏ trọng lượng không cần thiết trong xe",
    "Sử dụng điều hòa một cách hợp lý",
    "Bảo dưỡng động cơ định kỳ"
]

# Function definitions for OpenAI function calling
FUNCTION_DEFINITIONS = [
    {
        "name": "search_faq",
        "description": "Tìm kiếm câu hỏi thường gặp về ô tô",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Từ khóa hoặc chủ đề cần tìm kiếm trong FAQ"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_car_recommendations",
        "description": "Đưa ra gợi ý xe hơi dựa trên loại xe",
        "parameters": {
            "type": "object",
            "properties": {
                "car_type": {
                    "type": "string",
                    "enum": ["sedan", "suv", "hatchback", "electric"],
                    "description": "Loại xe cần tìm: sedan, suv, hatchback, hoặc electric"
                }
            },
            "required": ["car_type"]
        }
    },
    {
        "name": "get_maintenance_info",
        "description": "Lấy thông tin về lịch bảo dưỡng xe",
        "parameters": {
            "type": "object",
            "properties": {
                "service_type": {
                    "type": "string",
                    "enum": ["oil_change", "tire_rotation", "brake_inspection", "transmission_service", "all"],
                    "description": "Loại dịch vụ bảo dưỡng cần thông tin"
                }
            },
            "required": ["service_type"]
        }
    },
    {
        "name": "get_fuel_efficiency_tips",
        "description": "Lấy các mẹo tiết kiệm nhiên liệu",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

# Function implementations
def search_faq(query):
    """Tìm kiếm trong FAQ dựa trên từ khóa"""
    query_lower = query.lower()
    results = []
    
    for faq in FAQ_LIST:
        if query_lower in faq['question'].lower() or query_lower in faq['answer'].lower():
            results.append(faq)
    
    if not results:
        return {"message": "Không tìm thấy câu hỏi nào phù hợp với từ khóa."}
    
    return {"results": results}

def get_car_recommendations(car_type):
    """Đưa ra gợi ý xe dựa trên loại xe"""
    if car_type not in CAR_DATABASE:
        return {"error": "Loại xe không hợp lệ"}
    
    return {
        "car_type": car_type,
        "recommendations": CAR_DATABASE[car_type],
        "message": f"Đây là một số gợi ý xe {car_type} phổ biến tại Việt Nam"
    }

def get_maintenance_info(service_type):
    """Lấy thông tin bảo dưỡng"""
    if service_type == "all":
        return {"maintenance_schedule": MAINTENANCE_SCHEDULE}
    
    if service_type not in MAINTENANCE_SCHEDULE:
        return {"error": "Loại dịch vụ không hợp lệ"}
    
    return {
        "service": service_type,
        "info": MAINTENANCE_SCHEDULE[service_type]
    }

def get_fuel_efficiency_tips():
    """Lấy các mẹo tiết kiệm nhiên liệu"""
    return {"tips": FUEL_EFFICIENCY_TIPS}

# Function dispatcher
AVAILABLE_FUNCTIONS = {
    "search_faq": search_faq,
    "get_car_recommendations": get_car_recommendations,
    "get_maintenance_info": get_maintenance_info,
    "get_fuel_efficiency_tips": get_fuel_efficiency_tips
}
