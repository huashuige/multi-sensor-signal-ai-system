import cv2
import time


def process_frame(frame):
    """
    在此处添加你的图像识别/处理算法
    例如：目标检测、图像分割、特征提取等

    参数:
        frame: 输入图像帧 (numpy数组)

    返回:
        processed_frame: 处理后的图像帧
    """
    # 示例处理：转换为灰度图
    processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 在此处添加你的识别算法...
    # 例如:
    #   results = your_detection_model.detect(frame)
    #   processed_frame = draw_results(frame, results)

    return processed_frame


def main():
    # 初始化摄像头
    cap = cv2.VideoCapture(1,cv2.CAP_DSHOW)  # 0表示默认摄像头

    # 设置视频分辨率为 1280x720
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # 设置帧率为 30 FPS
    cap.set(cv2.CAP_PROP_FPS, 60)

    # 获取相机属性
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    time.sleep(1)
    print(f"Width: {width}, Height: {height}, FPS: {fps}")

    if not cap.isOpened():
        print("无法打开摄像头")
        return

    print("按 'q' 键退出程序...")
    # 添加这句是可以用鼠标拖动弹出的窗体
    cv2.namedWindow('real_img', cv2.WINDOW_NORMAL)

    while True:
        # 读取一帧
        ret, frame = cap.read()

        # 检查是否成功读取帧
        if not ret:
            print("无法获取帧，请检查摄像头连接")
            break

        # 调用处理函数
        processed_frame = process_frame(frame)

        # 显示原始帧和处理结果
        cv2.imshow('real_img', frame)
        cv2.imshow('processed_frame', processed_frame)

        # 退出条件：按q键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # ret, frame = cap.read()
    # cv2.imshow('real_img2', frame)
    # cv2.imwrite('real_img2.jpg', frame)
    # cv2.waitKey(0)

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()