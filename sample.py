import pandas as pd
import random

# Danh sách sản phẩm công nghệ và linh kiện tương ứng
products = [
    ("Smartphone", ["Screen", "Battery", "Camera", "Processor", "Speaker"]),
    ("Laptop", ["Screen", "Keyboard", "Battery", "RAM", "SSD", "Processor"]),
    ("Smartwatch", ["Screen", "Battery", "Heart Rate Sensor", "Strap"]),
    ("Tablet", ["Screen", "Battery", "Speaker", "Processor", "Stylus"]),
    ("Gaming Console", ["Controller", "Processor", "RAM", "GPU", "SSD"]),
]

# Tạo danh sách dữ liệu
data = []
for i in range(1, 6):  # Chỉ tạo 5 mẫu dữ liệu
    product_name, components = random.choice(products)
    component_list = ", ".join(components)  # Chọn ngẫu nhiên vài linh kiện
    data.append([i, product_name, component_list])

# Chuyển dữ liệu thành DataFrame
df = pd.DataFrame(data, columns=["ID", "Product Name", "Components"])

# Lưu vào file Excel
df.to_excel("sample.xlsx", index=False)

print("File Excel đã được tạo thành công với 5 mẫu dữ liệu!")