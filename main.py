from ursina import *
import cv2
import mediapipe as mp

# アプリの初期化
app = Ursina(
    title='Desktop Parallax Box (Final Version)',
    borderless=False,
    vsync=True
)

# ウィンドウ設定
window.color = color.black
window.fps_counter.enabled = True
Text(text='[Left Click] to Reset', origin=(0, -18), color=color.gray)

# --- 顔認識の準備 ---
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

# ★カメラ番号
camera_id = 2
cap = cv2.VideoCapture(camera_id) 

# --- 状態管理 ---
current_face_x = 0.5
current_face_y = 0.5
center_ref_x = 0.5
center_ref_y = 0.5

# --- 3Dシーンの作成 ---

# 箱のサイズ
wall_scale = 6
wall_distance = 3

# ★壁の色分け（ハッキリした色に変更）★
# unlit=True で影をなくし、色を鮮やかに見せます

# 奥（赤）
back_wall = Entity(model='quad', scale=(wall_scale, wall_scale), z=wall_distance, color=color.red, double_sided=True, unlit=True)
# 左（緑）
left_wall = Entity(model='quad', scale=(wall_scale, wall_scale), x=-wall_distance, rotation_y=90, color=color.green, double_sided=True, unlit=True)
# 右（青）
right_wall = Entity(model='quad', scale=(wall_scale, wall_scale), x=wall_distance, rotation_y=-90, color=color.blue, double_sided=True, unlit=True)
# 天井（黄色）
ceiling = Entity(model='quad', scale=(wall_scale, wall_scale), y=wall_distance, rotation_x=90, color=color.yellow, double_sided=True, unlit=True)
# 床（グレー）
floor = Entity(model='quad', scale=(wall_scale, wall_scale), y=-wall_distance, rotation_x=-90, color=color.gray, double_sided=True, unlit=True)


# ★キャラクター（頭・体・手・足付きロボット）★

# 足元の基準点を作成し、床の高さに配置（これで接地します）
player_group = Entity(y=floor.y) 

# ロボットの色
c_body = color.azure
c_limb = color.dark_gray

# 1. 胴体 (中心位置を調整)
body = Entity(parent=player_group, model='cube', scale=(0.5, 0.8, 0.3), y=0.8, color=c_body, unlit=True)
# 2. 頭 (胴体の上)
head = Entity(parent=player_group, model='cube', scale=(0.35, 0.35, 0.35), y=1.5, color=color.white, unlit=True)
# 3. 足（左・右）(胴体の下)
leg_l = Entity(parent=player_group, model='cube', scale=(0.15, 0.8, 0.2), x=-0.15, y=0.4, color=c_limb, unlit=True)
leg_r = Entity(parent=player_group, model='cube', scale=(0.15, 0.8, 0.2), x=0.15, y=0.4, color=c_limb, unlit=True)
# 4. 腕（左・右）(胴体の横、今回追加！)
arm_l = Entity(parent=player_group, model='cube', scale=(0.15, 0.7, 0.2), x=-0.35, y=1.0, color=c_body, unlit=True)
arm_r = Entity(parent=player_group, model='cube', scale=(0.15, 0.7, 0.2), x=0.35, y=1.0, color=c_body, unlit=True)


# カメラ位置
camera.z = -8

# --- 入力検知（リセット） ---
def input(key):
    global center_ref_x, center_ref_y
    if key == 'left mouse down':
        center_ref_x = current_face_x
        center_ref_y = current_face_y
        # ジャンプ演出
        player_group.animate_y(floor.y + 0.5, duration=0.1)
        player_group.animate_y(floor.y, duration=0.1, delay=0.1)

# --- メインループ ---
def update():
    global current_face_x, current_face_y

    success, image = cap.read()
    if not success:
        return

    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_detection.process(image)

    if results.detections:
        for detection in results.detections:
            bbox = detection.location_data.relative_bounding_box
            
            current_face_x = bbox.xmin + bbox.width / 2
            current_face_y = bbox.ymin + bbox.height / 2
            
            target_x = (current_face_x - center_ref_x) * -15
            target_y = (current_face_y - center_ref_y) * -10
            
            camera.x = lerp(camera.x, target_x, 0.1)
            camera.y = lerp(camera.y, target_y, 0.1)
            
            # ロボットの胴体中心を見つめる
            camera.look_at(body)

app.run()
cap.release()