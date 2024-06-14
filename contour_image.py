import cv2
import numpy as np

def handle_img2(path):
 # 读取图像
    img = cv2.imread(path)
    
    # 转换为灰度图像
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 自适应阈值处理
    imgAdaptiveThresh = cv2.adaptiveThreshold(imgGray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # 形态学操作（开运算和闭运算）
    kernel = np.ones((5, 5), np.uint8)
    imgMorph = cv2.morphologyEx(imgAdaptiveThresh, cv2.MORPH_CLOSE, kernel)
    imgMorph = cv2.morphologyEx(imgMorph, cv2.MORPH_OPEN, kernel)
    
    # Canny边缘检测
    imgCanny = cv2.Canny(imgMorph, 50, 150)
    
    # 轮廓检测
    contours, _ = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 绘制轮廓
    imgContours = cv2.drawContours(img.copy(), contours, -1, (0, 255, 0), 2)
    
    # 轮廓近似和形状描述符
    for contour in contours:
        epsilon = 0.01 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        huMoments = cv2.HuMoments(cv2.moments(approx)).flatten()
        print("Hu Moments:", huMoments)
    
    return imgContours

def handle_img(path):
    img = cv2.imread(path)
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 0)
    # imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 0)
    imgCanny = cv2.Canny(imgBlur, 50, 150)
    # imgCanny = cv2.Canny(imgBlur, 50, 150)

    imgEqualized = cv2.equalizeHist(imgCanny)

    return imgEqualized

_path = '/Users/milkypunch/Desktop/1.jpeg'
path = '/Users/milkypunch/Downloads/target_template11.png'
bkg_image = handle_img(_path)
target_template = handle_img(path)

res_target = cv2.matchTemplate(bkg_image, target_template, cv2.TM_CCOEFF_NORMED)
_, max_val, _, max_loc_target = cv2.minMaxLoc(res_target)
print(_, max_val, _, max_loc_target)

w, h = 82, 84
top_left = max_loc_target
bottom_right = (top_left[0] + w, top_left[1] + h)

img = cv2.imread(_path, 0)
cv2.rectangle(img, top_left, bottom_right, 255, 2)
cv2.imshow('Matched Image', img)
cv2.waitKey(0)
cv2.destroyAllWindows()




# # 480 × 240像素
# edge_image = cv2.Canny(cv2.imread(_path, 0), 50, 150)
# cv2.imwrite('edge.png', edge_image)
# w, h = 84, 84
# path = '/Users/milkypunch/Downloads/target_template11.png'
# target_template = cv2.Canny(cv2.imread(path, 0), 50, 150)
# cv2.imwrite('targetEdge.png', target_template)
# res_target = cv2.matchTemplate(edge_image, target_template, cv2.TM_CCOEFF_NORMED)
# _, max_val, _, max_loc_target = cv2.minMaxLoc(res_target)
# top_left = max_loc_target
# bottom_right = (top_left[0] + w, top_left[1] + h)

# image = cv2.imread(_path, 0)
# cv2.rectangle(image, top_left, bottom_right, 255, 2)
# cv2.imshow('Matched Image', image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# print(_, max_val, _, max_loc_target)
# # 在使用 cv2.matchTemplate 进行模板匹配时，返回的最大值位置（max_loc）实际上是模板的左上角在目标图像中的位置，而不是模板的中心点。
