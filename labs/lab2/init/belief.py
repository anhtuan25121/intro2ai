# belief.py - theo dõi / phỏng đoán vị trí đối phương khi mất dấu (enemy_position is None).
#
# ĐÂY LÀ BẢN TỐI GIẢN (placeholder): chỉ nhớ vị trí thấy lần cuối.
# Phần việc của 19127615 là nâng lên belief distribution 21x21 (predict + update 2 pha),
# GIỮ NGUYÊN 3 chữ ký dưới đây - agent.py gọi đúng theo interface này, không được đổi.
#   - EnemyTracker()
#   - update(self, map_state, my_pos, enemy_pos, step)  -> không trả về gì
#   - get_target(self, my_pos)                          -> (row, col) hoặc None
# Xem đặc tả đầy đủ ở labs/lab2/README.md §4 và các bản mẫu HideSeek/Blind/{B,C}/agent.py.


class EnemyTracker:
    def __init__(self):
        self.last_seen = None
        self.last_seen_step = -1

    def update(self, map_state, my_pos, enemy_pos, step):
        # thấy đối phương -> ghi lại; mất dấu -> giữ nguyên phỏng đoán cũ
        if enemy_pos is not None:
            self.last_seen = (int(enemy_pos[0]), int(enemy_pos[1]))
            self.last_seen_step = step

    def get_target(self, my_pos):
        # None nếu chưa từng thấy đối phương lần nào
        return self.last_seen
