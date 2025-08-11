import cv2
import numpy as np
import math
import time
import csv
from datetime import datetime


def visualize_imshow_resize(img_name, img1, resize_num):
    """
    缩放显示图片，不改变原始大小
    :param img_name: 图像名称
    :param img1: 图像，BGR或Gray
    :param resize_num: 缩放倍数，长宽等比例缩放
    :return:
    """
    cv2.imshow(img_name,
               cv2.resize(img1, (int(img1.shape[1] * resize_num), int(img1.shape[0] * resize_num))))


def visualize_quadrilateral(image, points, color=(0, 255, 0), thickness=2):
    """
    在图像上可视化四边形
    :param image: 原始图像
    :param points: 四边形顶点(4x2数组)
    :param color: 绘制颜色
    :param thickness: 线宽
    :return: 绘制后的图像
    """
    # 复制图像避免修改原始数据
    vis_img = image.copy()

    # 绘制四边形
    cv2.polylines(vis_img, [points.astype(int)], True, color, thickness)

    # 标记顶点
    labels = ["TL", "TR", "BR", "BL"]
    colors = [
        (0, 0, 255),  # 左上: 红色
        (0, 255, 255),  # 右上: 黄色
        (255, 0, 0),  # 右下: 蓝色
        (255, 0, 255)  # 左下: 紫色
    ]

    for i, (x, y) in enumerate(points):
        cv2.circle(vis_img, (int(x), int(y)), 15, colors[i], 3)
        cv2.putText(vis_img, labels[i], (int(x) + 10, int(y)),
                    cv2.FONT_HERSHEY_SIMPLEX, 3, colors[i], 3)

    return vis_img


def visualize_contour_steps(cropped_img, steps, title="处理步骤"):
    """
    可视化图像处理步骤
    :param cropped_img: 原始图像
    :param steps: 处理步骤列表 [(image, title), ...]
    :param title: 窗口标题
    """
    # 创建组合图像
    step_imgs = []
    for img, step_title in steps:
        if len(img.shape) == 2:  # 灰度图转BGR
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        # 添加标题
        cv2.putText(img, step_title, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        step_imgs.append(img)

    # 计算组合图像尺寸
    max_height = max(img.shape[0] for img in step_imgs)
    total_width = sum(img.shape[1] for img in step_imgs)

    # 创建空白画布
    combined = np.zeros((max_height, total_width, 3), dtype=np.uint8)

    # 拼接图像
    x_offset = 0
    for img in step_imgs:
        h, w = img.shape[:2]
        combined[:h, x_offset:x_offset + w] = img
        x_offset += w

    # 显示结果
    cv2.imshow(title, combined)
    cv2.waitKey(0)
    cv2.destroyWindow(title)
    return combined



def find_best_template_match(template_img,
                             target_img,
                             min_scale=0.5,
                             max_scale=2.0,
                             scale_steps=30,
                             visualize=False):
    """
    查找最佳匹配区域并截取
    :param template_img: 模板图像(BGR格式)
    :param target_img: 待匹配图像(BGR格式)
    :param min_scale: 最小缩放比例
    :param max_scale: 最大缩放比例
    :param scale_steps: 缩放步数
    :return: (匹配矩形坐标, 截取的图像) 或 (None, None) 如果未找到
    """
    # 转换为灰度图
    template_gray = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)
    target_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)

    # 获取图像尺寸
    t_h, t_w = template_gray.shape
    img_h, img_w = target_gray.shape

    # 初始化最佳匹配变量
    best_match_val = -1.0  # 最佳匹配值初始化为-1（相关系数范围[-1,1]）
    best_match_rect = None  # 最佳匹配矩形区域
    best_scale = 1.0  # 最佳匹配比例

    # 创建缩放比例序列
    scales = np.linspace(min_scale, max_scale, scale_steps)
    print("匹配开始")

    for scale in scales:
        # 计算当前缩放后的模板尺寸
        w = int(t_w * scale)
        h = int(t_h * scale)

        # 跳过无效尺寸
        if w < 5 or h < 5 or w > img_w or h > img_h:
            continue

        # 缩放模板
        resized_template = cv2.resize(template_gray, (w, h), interpolation=cv2.INTER_AREA)

        # 执行模板匹配
        result = cv2.matchTemplate(target_gray, resized_template, cv2.TM_CCOEFF_NORMED)

        # 获取当前尺度下的最佳匹配
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # 更新全局最佳匹配
        if max_val > best_match_val:
            best_match_val = max_val
            best_match_rect = (max_loc[0], max_loc[1], w, h)
            best_scale = scale

    # 如果没有找到匹配，返回空结果
    if best_match_val < 0.5:  # 设置一个合理的阈值
        print(f"未找到有效匹配 (最高匹配值: {best_match_val:.2f})")
        return None, None

    print(f"找到最佳匹配: 相似度 {best_match_val:.4f}, 缩放比例 {best_scale:.2f}")

    # 截取匹配区域
    x, y, w, h = best_match_rect
    # 确保坐标在图像范围内
    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(img_w, x + w), min(img_h, y + h)

    # 截取匹配区域
    cropped_img = target_img[y1:y2, x1:x2].copy()

    if visualize:
        if best_match_rect is not None:
            # 绘制匹配框
            output_img = target_img.copy()
            x, y, w, h = best_match_rect
            cv2.rectangle(output_img, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.putText(output_img, f"Match: {best_match_rect}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 2)

            # 显示匹配信息
            print(f"匹配区域坐标: x={x}, y={y}, width={w}, height={h}")

            # 保存结果
            cv2.imwrite('best_match_result.jpg', output_img)
            cv2.imwrite('cropped_region.jpg', cropped_img)

            # 显示结果
            visualize_imshow_resize('template', template_img, 0.5)
            visualize_imshow_resize('best_match_result', output_img, 0.3)
            visualize_imshow_resize('cropped_region', cropped_img, 0.5)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("未找到匹配区域")

    return best_match_rect, cropped_img


def fit_rectangle_to_contour(contour, gray_img):
    """
    针对断裂轮廓的矩形拟合算法
    :param contour: 断裂的轮廓
    :param gray_img: 灰度图像（用于亚像素优化）
    :return: 拟合的矩形顶点(4x2数组)
    """
    # 1. 凸包计算 - 填补断裂部分
    hull = cv2.convexHull(contour)

    # 2. 多边形逼近 - 使用动态epsilon
    perimeter = cv2.arcLength(hull, True)
    epsilon = max(0.02 * perimeter, 3.0)  # 最小3像素
    approx = cv2.approxPolyDP(hull, epsilon, True)

    # 3. 顶点数量处理
    if len(approx) == 4:
        # 直接返回四边形
        return sort_quad_points(approx.reshape(4, 2))

    # 4. 针对顶点不足的情况 - 使用最小外接矩形
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)

    # 5. 亚像素角点优化 - 安全处理
    try:
        # 准备亚像素优化
        gray_np = np.float32(gray_img)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.01)

        # 确保box是正确格式
        box_float = np.array(box, dtype=np.float32).reshape(-1, 1, 2)

        # 执行亚像素优化
        box_refined = cv2.cornerSubPix(gray_np, box_float, (5, 5), (-1, -1), criteria)
        return sort_quad_points(box_refined.reshape(4, 2))
    except Exception as e:
        print(f"亚像素优化失败: {e}, 使用原始矩形")
        return sort_quad_points(box)


def find_rectangle_in_broken_contour(cropped_img,
                                     min_contour_area=500,
                                     thresh_value=120,
                                     visualize=False):
    """
    专门处理断裂轮廓的矩形检测
    :param thresh_value: 边框阈值
    :param cropped_img: 截取的图像区域(BGR格式)
    :param min_contour_area: 最小轮廓面积阈值
    :return: 四边形的四个顶点坐标(4x2数组)或None
    """
    # 转换为灰度图
    gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)

    # 1. 光照均衡
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray_eq = clahe.apply(gray)

    # 2. 高斯模糊降噪
    blurred = cv2.GaussianBlur(gray_eq, (5, 5), 0)

    ret, thresh1 = cv2.threshold(blurred, thresh_value, 255, cv2.THRESH_BINARY)

    # # 3. 边缘检测
    # edges = cv2.Canny(blurred, canny_threshold1, canny_threshold2)

    # # 4. 形态学操作 - 强化边缘连接
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    # closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)

    # 5. 查找轮廓
    contours, _ = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    # 6. 按面积排序轮廓
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    largest_contour = contours[0]

    # 7. 轮廓面积检查
    if cv2.contourArea(largest_contour) < min_contour_area:
        return None

    # 8. 拟合矩形到轮廓
    rect_points = fit_rectangle_to_contour(largest_contour, gray)
    if rect_points is not None:
        print("矩形轮廓拟合完成")

    if visualize:
        if rect_points is not None:
            print("找到矩形顶点坐标:")
            print(f"左上: ({rect_points[0][0]:.1f}, {rect_points[0][1]:.1f})")
            print(f"右上: ({rect_points[1][0]:.1f}, {rect_points[1][1]:.1f})")
            print(f"右下: ({rect_points[2][0]:.1f}, {rect_points[2][1]:.1f})")
            print(f"左下: ({rect_points[3][0]:.1f}, {rect_points[3][1]:.1f})")

            contour_bgr = np.zeros_like(cropped_img)

            cv2.drawContours(contour_bgr, largest_contour, -1, (0, 255, 255), 2)
            contour_vis = visualize_quadrilateral(contour_bgr, rect_points, color=(0, 255, 0), thickness=3)

            # cv2.drawContours(cropped_img, largest_contour, -1, (0, 255, 255), 3)
            cropped_vis = visualize_quadrilateral(cropped_img, rect_points, color=(0, 255, 0), thickness=3)

            # 保存结果
            cv2.imwrite('blurred.jpg', blurred)
            cv2.imwrite('cropped_region_frame.jpg', cropped_vis)

            visualize_imshow_resize('blurred', blurred, 0.5)
            visualize_imshow_resize('cropped_img', cropped_vis, 0.5)
            visualize_imshow_resize('contour_bgr', contour_vis, 0.5)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("未找到矩形轮廓")
    return rect_points


def sort_quad_points(points):
    """
    对矩形顶点进行排序: 左上, 右上, 右下, 左下
    """
    # 计算中心点
    center = np.mean(points, axis=0)

    # 按角度排序
    angles = np.arctan2(points[:, 1] - center[1], points[:, 0] - center[0])
    sorted_indices = np.argsort(angles)

    # 重新排序点
    sorted_points = points[sorted_indices]

    # 确保左上角是第一个点
    top_left_idx = np.argmin(np.sum(sorted_points, axis=1))
    sorted_points = np.roll(sorted_points, -top_left_idx, axis=0)

    return sorted_points


def perspective_transform(cropped_img, quad_points, visualize=False):
    """
    将四边形区域进行透视变换，生成矩形图像
    :param cropped_img: 原始截取图像
    :param quad_points: 四边形顶点坐标(4x2数组)
    :return: 变换后的矩形图像
    """
    # 1. 计算目标矩形的尺寸
    # 计算宽度 (取上边和下边的最大长度)
    width_top = np.linalg.norm(quad_points[0] - quad_points[1])
    width_bottom = np.linalg.norm(quad_points[3] - quad_points[2])
    max_width = max(int(width_top), int(width_bottom))

    # 计算高度 (取左边和右边的最大长度)
    height_left = np.linalg.norm(quad_points[0] - quad_points[3])
    height_right = np.linalg.norm(quad_points[1] - quad_points[2])
    max_height = max(int(height_left), int(height_right))

    # 2. 定义目标矩形的四个点
    dst_points = np.array([
        [0, 0],  # 左上
        [max_width - 1, 0],  # 右上
        [max_width - 1, max_height - 1],  # 右下
        [0, max_height - 1]  # 左下
    ], dtype="float32")

    # 3. 确保quad_points是float32类型
    src_points = quad_points.astype("float32")

    # 4. 计算透视变换矩阵
    M = cv2.getPerspectiveTransform(src_points, dst_points)

    # 5. 执行透视变换
    warped = cv2.warpPerspective(cropped_img, M, (max_width, max_height))

    if visualize:
        cv2.imwrite('transformed_img.jpg', warped)

        visualize_imshow_resize('transformed_img', warped, 0.5)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return warped


def crop_borders(image, percent=10):
    """
    裁剪图像边框
    :param image: 输入图像
    :param percent: 裁剪百分比（0-100）
    :return: 裁剪后的图像
    """
    h, w = image.shape[:2]

    # 计算裁剪尺寸
    crop_x = int(w * percent / 100)
    crop_y = int(h * percent / 100)

    # 确保裁剪尺寸有效
    if crop_x <= 0 or crop_y <= 0 or crop_x * 2 >= w or crop_y * 2 >= h:
        return image.copy()

    # 裁剪图像，图像下框裁剪2.2倍边框百分比
    cropped = image[crop_y:h - int(crop_y * 2.2), crop_x:w - crop_x]

    return cropped






def find_longest_line(image,
                      canny_threshold1=10,
                      canny_threshold2=200,
                      hough_threshold=100,
                      min_line_length=30,
                      max_line_gap=3,
                      border_crop_percent=12,
                      visualize=False):
    """
    从图像中检测最长的直线
    :param thresh_adapt_value: 二值化阈值
    :param border_crop_percent: 裁剪边框百分比
    :param image: 输入图像（BGR格式）
    :param canny_threshold1: Canny边缘检测低阈值
    :param canny_threshold2: Canny边缘检测高阈值
    :param hough_threshold: 霍夫变换累加器阈值
    :param min_line_length: 直线最小长度
    :param max_line_gap: 直线最大间断
    :return: 最长直线的端点坐标 (x1, y1, x2, y2) 或 None
    """
    # 0. 裁剪边框
    if border_crop_percent > 0:
        cropped_img = crop_borders(image, border_crop_percent)
    else:
        cropped_img = image.copy()

    # 1. 转换为灰度图
    gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)

    # 1. 光照均衡
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray_eq = clahe.apply(gray)

    # 2. 高斯模糊降噪
    blurred = cv2.GaussianBlur(gray_eq, (5, 5), 0)

    # 3. 二值化
    # ret, thresh_adapt = cv2.threshold(blurred, thresh_adapt_value, 255, cv2.THRESH_BINARY_INV)
    thresh_adapt = cv2.adaptiveThreshold(blurred, 255,
                                         cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 5, -1) # 二值化
    # visualize_imshow_resize('test1_img', thresh_adapt, 1)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # 4. 使用霍夫变换检测直线
    lines = cv2.HoughLinesP(thresh_adapt, 1, np.pi / 180, hough_threshold,
                            minLineLength=min_line_length, maxLineGap=max_line_gap)

    # for i in range(len(lines)):
    #     x1, y1, x2, y2 = lines[i][0]
    #     cv2.line(cropped_img, (x1, y1), (x2, y2), (0, 255, 0), 1)
    # visualize_imshow_resize('test2_img', cropped_img, 1)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # 5. 如果没有检测到直线，返回None
    if lines is None:
        return None

    # 6. 找到最长的直线
    longest_line = None
    max_length = 0

    for line in lines:
        x1, y1, x2, y2 = line[0]
        length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        if length > max_length:
            max_length = length
            longest_line = (x1, y1, x2, y2)

    # 7. 如果裁剪了边框，需要调整坐标
    if border_crop_percent > 0 and longest_line is not None:
        h, w = image.shape[:2]
        crop_x = int(w * border_crop_percent / 100)
        crop_y = int(h * border_crop_percent / 100)

        # 调整坐标到原始图像坐标系
        x1, y1, x2, y2 = longest_line
        longest_line = (
            x1 + crop_x,
            y1 + crop_y,
            x2 + crop_x,
            y2 + crop_y
        )

    if visualize:
        if longest_line is not None:
            # 可视化直线
            line_img = visualize_line(image, longest_line)

            cv2.imwrite('line_img.jpg', line_img)
            visualize_imshow_resize('line_img', line_img, 0.5)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            print(
                f"检测到最长直线: ({longest_line[0]}, {longest_line[1]}) -> ({longest_line[2]}, {longest_line[3]})")
        else:
            print("未检测到直线")
    return longest_line


def visualize_line(image, line, color=(0, 0, 255), thickness=4):
    """
    在图像上可视化直线
    :param image: 原始图像
    :param line: 直线端点 (x1, y1, x2, y2)
    :param color: 绘制颜色
    :param thickness: 线宽
    :return: 绘制后的图像
    """
    # 复制图像避免修改原始数据
    vis_img = image.copy()

    if line is not None:
        x1, y1, x2, y2 = line
        cv2.line(vis_img, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness)

    return vis_img


def calculate_line_angle(line, visualize=False):
    """
    计算直线的角度（水平向左为0度，顺时针为正，0-180度）
    :param line: 直线端点 (x1, y1, x2, y2)
    :return: 角度值（度数）
    """
    if line is None:
        return None

    x1, y1, x2, y2 = line

    # 计算直线方向向量
    dx = x2 - x1
    dy = y2 - y1

    # 计算与水平向左方向的角度
    # 水平向左方向向量为 (-1, 0)

    # 计算直线与水平向左方向的夹角（弧度）
    # 使用点积公式：cosθ = (A·B) / (|A||B|)
    dot_product = -dx * 1 + dy * 0  # (-1, 0) · (dx, dy)
    magnitude_line = math.sqrt(dx ** 2 + dy ** 2)
    magnitude_ref = 1.0  # 参考向量长度

    # 避免除以零
    if magnitude_line < 1e-5:
        return 0.0

    cos_theta = dot_product / (magnitude_line * magnitude_ref)

    # 确保cos_theta在有效范围内
    cos_theta = max(-1.0, min(1.0, cos_theta))

    # 计算角度（弧度）
    angle_rad = math.acos(cos_theta)

    # 转换为度数
    angle_deg = math.degrees(angle_rad)

    # 根据dy的正负确定角度方向
    # 由于y轴向下，dy为正表示直线向下，为顺时针方向
    if dy < 0:
        # 如果dy为负，表示直线向上，需要调整角度
        angle_deg = 360 - angle_deg

    # 将角度规范到0-180度范围
    angle_deg %= 180
    angle_deg = 180 - angle_deg

    return angle_deg


def visualize_angle(image, line, angle, instrument_data, color=(200, 255, 50), thickness=4,visualize=False):
    """
    在图像上可视化直线和角度信息
    :param instrument_data: 表盘读数
    :param image: 原始图像
    :param line: 直线端点 (x1, y1, x2, y2)
    :param angle: 角度值
    :param color: 绘制颜色
    :param thickness: 线宽
    :return: 绘制后的图像
    """
    # 复制图像避免修改原始数据
    vis_img = image.copy()

    if line is not None and angle is not None:
        x1, y1, x2, y2 = line

        # 绘制直线
        cv2.line(vis_img, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness)

        # 计算中点位置
        mid_x = int((x1 + x2) / 2)
        mid_y = int((y1 + y2) / 2)

        # 绘制角度文本
        text = f"Angle: {angle:.1f}degree"
        cv2.putText(vis_img, text, (mid_x + 10, mid_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 4)

        # 绘制表盘读数文本
        text = f"Read Data: {instrument_data:.2f}"
        cv2.putText(vis_img, text, (mid_x + 10, mid_y + 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 4)

        # 绘制角度示意图
        angle_length = 150
        end_x = int(mid_x - angle_length * math.cos(math.radians(180 - angle)))
        end_y = int(mid_y + angle_length * math.sin(math.radians(180 - angle)))
        cv2.line(vis_img, (mid_x, mid_y), (mid_x, mid_y - angle_length), (0, 0, 255), 8)  # 参考线（垂直向上）
        cv2.line(vis_img, (mid_x, mid_y), (end_x, end_y), (255, 0, 255), 8)  # 角度线

    if visualize:
        cv2.imwrite('angle_img.jpg', vis_img)
        visualize_imshow_resize('angle_img', vis_img, 0.5)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return vis_img


def angle_transformed(angle,
                      max_data,
                      angle_range = 120,
                      start_angle = 32):
    """
    角度和指针读书转换
    :param angle: 指针角度
    :param max_data: 最大量程
    :param angle_range: 角度范围
    :param start_angle: 初始角度
    :return:
    """
    read_data = max_data / angle_range * (angle - start_angle)

    return read_data


def camera_init():
    """
    相机初始化
    :return: 相机索引
    """
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # 0表示默认摄像头

    # 设置视频分辨率为 1280x720
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # 设置帧率为 30 FPS
    cap.set(cv2.CAP_PROP_FPS, 30)

    # 获取相机属性
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    time.sleep(1)
    print(f"Width: {width}, Height: {height}, FPS: {fps}")

    return cap


def get_camera_img(cap):
    """
    获取一帧图像
    :param cap: 相机索引
    :return:
    """
    if not cap.isOpened():
        print("无法打开摄像头")
        return

    ret, frame = cap.read()
    # cv2.imshow('real_img', frame)
    # cv2.imwrite('real_img.jpg', frame)
    # cv2.waitKey(0)

    return frame


def camera_img_process(target):
    """
    表盘识别
    :param target: 待处理原始图像
    :return: 识别后的表盘，读数
    """
    # 执行匹配
    best_rect, cropped_img = find_best_template_match(
        template,
        target,
        min_scale=0.1,  # 最小缩放比例
        max_scale=0.5,  # 最大缩放比例
        scale_steps=30,  # 缩放步数
        visualize=False  # 可视化
    )

    quad_points = find_rectangle_in_broken_contour(
        cropped_img,
        min_contour_area=500,  # 根据图像尺寸调整
        thresh_value=120,
        visualize=False  # 可视化
    )

    # 执行透视变换
    transformed_img = perspective_transform(
        cropped_img,
        quad_points,
        visualize=False
    )

    # 从变换后的图像中检测最长直线
    longest_line = find_longest_line(
        transformed_img,
        border_crop_percent=13,
        visualize=False
    )

    # 计算直线角度
    line_angle = calculate_line_angle(longest_line)

    # 指针角度和表盘读数转换
    instrument_data = angle_transformed(line_angle, 15)

    print(f"检测到指针角度: {line_angle:.2f}°")
    print(f"表盘读数: {instrument_data:.2f}")

    # 可视化角度信息
    angle_img = visualize_angle(transformed_img, longest_line, line_angle, instrument_data,visualize=False)

    return angle_img,instrument_data



if __name__ == "__main__":
    cap = camera_init()
    # 模板读取
    template = cv2.imread('image_template4.jpg')
    # 定义CSV文件名
    filename = "sensor_data.csv"

    # 打开文件（使用追加模式），注意newline=''防止空行
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)

        # 如果是新文件，写入表头
        if file.tell() == 0:
            writer.writerow(["Timestamp", "ElapsedTime", "Reading"])

        # while True:
        for step in range(0, 100):
            # 获取当前时间
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            start_time = time.time()

            # 循环读取相机帧
            frame = get_camera_img(cap)
            # frame = cv2.imread('images4/18.jpg')

            # 处理相机帧，返回拟合图像和计算结果
            angle_img, instrument_data = camera_img_process(frame)

            end_time = time.time()
            elapsed_time = end_time - start_time     # 一帧图像处理时间

            cv2.imwrite('read_data_camera/%s.jpg' % step, angle_img)
            # visualize_imshow_resize('angle_img', angle_img, 1)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            # 3. 写入数据到CSV
            writer.writerow([current_time, elapsed_time, instrument_data])
            file.flush()  # 确保每次写入后立即保存

            # 退出条件：按q键退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()




    ##
    # h, w = angle_img.shape[:2]
    # cv2.line(angle_img, (int(w * 0.5), int(h * 1)), (int(w * 0.1), int(h * 0.3)), (200, 150, 255), 8)
    # cv2.line(angle_img, (int(w * 0.5), int(h * 1)), (int(w * 0.9), int(h * 0.5)), (200, 150, 255), 8)
    # radian = atan2((w * 0.5 - w * 0.1), (h * 1 - h * 0.3))
    # angle_test = radian * 180 / math.pi
    # print(angle_test)
    ##
