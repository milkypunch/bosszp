import cv2
import numpy as np

# 读取截图
screenshot = cv2.imread('/Users/milkypunch/Desktop/screenshotx.png', 0)

# 模板路径列表
target_template_paths = [
    '/Users/milkypunch/Downloads/target_template1.png',
    '/Users/milkypunch/Downloads/target_template2.png',
    '/Users/milkypunch/Downloads/target_template3.png',
    '/Users/milkypunch/Downloads/target_template4.png',
    '/Users/milkypunch/Downloads/target_template5.png',
    '/Users/milkypunch/Downloads/target_template6.png',
    '/Users/milkypunch/Downloads/target_template7.png',
    '/Users/milkypunch/Downloads/target_template8.png',
    '/Users/milkypunch/Downloads/target_template9.png',
]

# 初始化变量
best_puzzle_match = None
best_gap_match = None
best_puzzle_center = None
best_gap_center = None
best_distance = float('inf')

# 遍历所有模板
for template_path in target_template_paths:
    # 读取模板
    template = cv2.imread(template_path, 0)
    
    # 边缘检测
    edges_screenshot = cv2.Canny(screenshot, 50, 150)
    edges_template = cv2.Canny(template, 50, 150)
    
    # 模板匹配
    result = cv2.matchTemplate(edges_screenshot, edges_template, cv2.TM_CCOEFF_NORMED)
    
    # 获取匹配结果
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # 确定模板的中心点
    template_center = (max_loc[0] + template.shape[1] // 2, max_loc[1] + template.shape[0] // 2)
    
    # 计算距离（假设拼图和缺口的模板是一样的）
    if best_puzzle_center is None:
        best_puzzle_center = template_center
        best_gap_center = template_center
    else:
        distance = np.sqrt((best_puzzle_center[0] - template_center[0])**2 + (best_puzzle_center[1] - template_center[1])**2)
        if distance < best_distance:
            best_distance = distance
            best_gap_center = template_center

# 输出结果
print(f"拼图位置: {best_puzzle_center}")
print(f"缺口位置: {best_gap_center}")
print(f"拼图和缺口之间的距离: {best_distance}")

# 显示结果
screenshot_color = cv2.cvtColor(screenshot, cv2.COLOR_GRAY2BGR)
cv2.circle(screenshot_color, best_puzzle_center, 5, (0, 255, 0), -1)
cv2.circle(screenshot_color, best_gap_center, 5, (0, 0, 255), -1)
cv2.line(screenshot_color, best_puzzle_center, best_gap_center, (255, 0, 0), 2)
cv2.imshow('Result', screenshot_color)
cv2.waitKey(0)
cv2.destroyAllWindows()

