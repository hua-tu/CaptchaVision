# trans.py

import cv2
import numpy as np
import os

# --- 1. 配置路径 ---
INPUT_PATH = "img/img_1.png"
OUTPUT_PATH = "out/temp_1.png"
# 二值化中间结果输出路径
BINARY_OUTPUT_PATH = "out/binary_1.png"


# --- 2. 辅助方法 ---


def remove_full_length_stripes(img: np.ndarray, black_thresh: int = 128) -> np.ndarray:
    """
    去除从边界延伸到底/到右的整条黑线：
    - 若某列自顶到底全为黑，则整列置白
    - 若某行自左到右全为黑，则整行置白
    """
    black = img < black_thresh
    full_black_cols = np.all(black, axis=0)
    full_black_rows = np.all(black, axis=1)

    cleaned = img.copy()
    cleaned[:, full_black_cols] = 255
    cleaned[full_black_rows, :] = 255
    return cleaned


# --- 3. 核心图像处理函数 ---

def remove_grid_lines_and_process(input_path, output_path, binary_output_path=BINARY_OUTPUT_PATH, 
                                   adaptive_c=10, white_threshold=255):
    """
    对图像进行二值化，并使用整行/整列全黑去除背景线条。
    
    参数:
        input_path: 输入图片路径
        output_path: 输出图片路径
        binary_output_path: 二值化中间结果输出路径
        adaptive_c: 自适应阈值参数C，值越大阈值越严格（默认10，可尝试15-20让更多像素变黑）
        white_threshold: 白色阈值，大于等于此值的像素保持白色，其他都变成黑色（默认255，即只有纯白色是白色）
    """

    # 检查输入文件是否存在
    if not os.path.exists(input_path):
        print(f"❌ 错误：输入文件未找到！请检查路径：{input_path}")
        return

    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✅ 创建输出目录：{output_dir}")

    # 1. 读取图像
    img = cv2.imread(input_path)

    # 检查图片是否成功读取
    if img is None:
        print(f"❌ 错误：无法读取图像，请检查文件格式或损坏：{input_path}")
        return

    print("--- 图像处理开始 ---")

    # 2. 灰度化
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. 自适应二值化 (去除背景的第一步)
    # 使用 Gaussian C 自适应阈值，适用于背景亮度不均匀的情况
    # 参数说明：
    # - blockSize=101: 局部邻域大小，越大越平滑，但可能丢失细节
    # - C=adaptive_c: 从平均值中减去的常数，值越大阈值越严格（更倾向于黑色）
    #   可以调整：增大 C 值（如15-20）会让更多像素变成黑色（更严格）
    binary_img = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 101, adaptive_c
    )
    print(f"✅ 完成：自适应二值化（C={adaptive_c}）")
    
    # 3.5. 后处理：把所有不是纯白色的像素都变成黑色
    # 这样确保只有纯白色（255）是白色，其他所有浅色、灰色都变成黑色（0）
    # white_threshold 参数可以调整：降低此值（如250）会让更多浅灰色也保持白色
    binary_img = np.where(binary_img >= white_threshold, 255, 0).astype(np.uint8)
    print(f"✅ 完成：非纯白色统一变成黑色（白色阈值={white_threshold}）")

    # 将二值化结果单独输出，便于调试与查看
    if binary_output_path:
        binary_dir = os.path.dirname(binary_output_path)
        if binary_dir and not os.path.exists(binary_dir):
            os.makedirs(binary_dir)
        cv2.imwrite(binary_output_path, binary_img)
        print(f"✅ 已保存二值化结果：{binary_output_path}")

    # 4. 使用整行/整列全黑策略去除背景线条
    cleaned = remove_full_length_stripes(binary_img, black_thresh=128)
    print("✅ 完成：整行/整列全黑线条去除")

    # 5. 保存最终结果
    cv2.imwrite(output_path, cleaned)

    print(f"--- 处理完成！结果已保存到：{output_path} ---")


# --- 3. 脚本执行 ---

if __name__ == "__main__":
    remove_grid_lines_and_process(INPUT_PATH, OUTPUT_PATH)