import cv2
import numpy as np
import os
import sys


def connect_nearby_elements(input_path: str, output_path: str = None, max_distance: int = 2):
    """
    连接相邻的元素：如果距离 <= max_distance px，就连接起来
    
    直接遍历所有黑色像素，对于每个像素，检查周围max_distance范围内的其他黑色像素并连接
    不使用膨胀，不考虑性能，只确保能连接
    
    参数:
        input_path: 输入图片路径
        output_path: 输出图片路径，如果为None则自动生成
        max_distance: 最大连接距离（像素），默认2px
    """
    if not os.path.exists(input_path):
        print(f"❌ 错误：输入文件未找到：{input_path}")
        return None
    
    # 读取图像
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"❌ 错误：无法读取图像：{input_path}")
        return None
    
    # 统一处理：让前景（要连接的像素）变成255，背景变成0
    # cleaned.png通常是黑色前景、白色背景，所以需要反转
    # 检查图像中黑色像素（<128）和白色像素（>=128）的数量
    black_pixels = np.sum(img < 128)
    white_pixels = np.sum(img >= 128)
    
    print(f"📊 图像统计：黑色像素={black_pixels}, 白色像素={white_pixels}")
    
    # 记录是否需要反转（用于最后恢复原始格式）
    need_reverse = False
    
    # 如果黑色像素少，说明黑色是前景，需要反转让前景变成255
    if black_pixels < white_pixels:
        binary = 255 - img
        need_reverse = True
        print("✅ 已反转图像：黑色前景 -> 白色前景")
    else:
        binary = img.copy()
        print("✅ 保持原图：白色是前景")
    
    # 创建输出图像
    connected = binary.copy()
    
    # 找到所有前景像素（值为255）
    foreground_pixels = np.column_stack(np.where(binary == 255))
    
    print(f"✅ 找到 {len(foreground_pixels)} 个前景像素")
    
    # 对于每个前景像素，检查周围max_distance范围内的其他前景像素
    connection_count = 0
    processed_pairs = set()  # 避免重复连接
    height, width = binary.shape
    
    for y1, x1 in foreground_pixels:
        # 只检查周围 max_distance 范围内的区域
        y_min = max(0, y1 - max_distance)
        y_max = min(height, y1 + max_distance + 1)
        x_min = max(0, x1 - max_distance)
        x_max = min(width, x1 + max_distance + 1)
        
        # 在这个区域内查找其他前景像素
        region = binary[y_min:y_max, x_min:x_max]
        region_foreground = np.column_stack(np.where(region == 255))
        
        for ry, rx in region_foreground:
            y2 = y_min + ry
            x2 = x_min + rx
            
            # 跳过自己
            if x1 == x2 and y1 == y2:
                continue
            
            # 计算欧氏距离
            distance = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
            
            if distance <= max_distance:
                # 避免重复连接（使用排序后的坐标对）
                pair = tuple(sorted([(x1, y1), (x2, y2)]))
                if pair not in processed_pairs:
                    # 在两个点之间画线连接
                    cv2.line(connected, (x1, y1), (x2, y2), 255, thickness=1)
                    processed_pairs.add(pair)
                    connection_count += 1
    
    print(f"✅ 已连接 {connection_count} 对距离 <= {max_distance}px 的元素")
    
    # 如果之前反转了图像，现在反转回来，保持与输入图像格式一致
    if need_reverse:
        connected = 255 - connected
    
    # 保存结果
    if output_path is None:
        output_path = input_path.replace('.png', '_connected.png')
    
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    cv2.imwrite(output_path, connected)
    print(f"✅ 连接完成，结果已保存到：{output_path}")
    
    return connected


if __name__ == "__main__":
    # 默认处理指定路径
    default_path = "img/cleaned.png"
    
    # 如果命令行有参数，使用命令行参数
    input_path = sys.argv[1] if len(sys.argv) > 1 else default_path
    
    # 生成输出路径（在原文件名后加 _connected）
    output_path = input_path.replace('.png', '_connected.png')
    
    # 连接距离 <= 2px 的元素
    connect_nearby_elements(input_path, output_path, max_distance=3)

