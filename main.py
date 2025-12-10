import os
import cv2
from datetime import datetime
import uuid
from flask import Flask, request, jsonify

from trans import remove_grid_lines_and_process
from ai_get import recognize_captcha_from_array
from connect import connect_nearby_elements


def create_app():
    app = Flask(__name__)

    # 添加一个 HEAD 方法专用的存活检测接口
    @app.route("/online", methods=["HEAD"])
    def online_head():
        return "", 200


    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    @app.route("/predict", methods=["POST"])
    def predict():
        if "file" not in request.files:
            return jsonify({"error": "missing file field"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "empty filename"}), 400

        # 为每次请求创建唯一的输出目录，保留原始、二值化和预处理后图像
        run_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
        run_dir = os.path.join("out", "http_runs", run_id)
        os.makedirs(run_dir, exist_ok=True)

        in_path = os.path.join(run_dir, "input.png")
        binary_path = os.path.join(run_dir, "binary.png")
        cleaned_path = os.path.join(run_dir, "cleaned.png")
        connected_path = os.path.join(run_dir, "connected.png")

        file.save(in_path)

        # 1. 预处理：二值化并去整行/整列线
        remove_grid_lines_and_process(in_path, cleaned_path, binary_output_path=binary_path)

        # 2. 连接相邻元素（距离 <= 3px）
        connected_img = connect_nearby_elements(cleaned_path, connected_path, max_distance=3)
        if connected_img is None:
            return jsonify({"error": "failed to connect nearby elements"}), 500

        # 3. AI识别连接后的图像
        result = recognize_captcha_from_array(connected_img)

        result_txt_path = os.path.join(run_dir, "result.txt")
        with open(result_txt_path, "w", encoding="utf-8") as f:
            f.write(result)
            
        return jsonify(
            {
                "result": result,
                "saved_paths": {
                    "original": in_path,
                    "binary": binary_path,
                    "cleaned": cleaned_path,
                    "connected": connected_path,
                },
            }
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8011, debug=False)
