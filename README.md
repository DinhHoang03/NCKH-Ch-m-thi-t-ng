# 📄 Phần Mềm Chấm Thi Tự Động - HUMG

## Giới thiệu đề tài
Đề tài nghiên cứu khoa học: **"Xây dựng phần mềm chấm thi trắc nghiệm tự động bằng nhận diện ảnh"**.

Phần mềm giúp hỗ trợ giáo viên và nhà trường tự động hóa quá trình chấm thi trắc nghiệm, từ quét ảnh phiếu trả lời, nhận dạng đáp án đến tính điểm và lưu trữ kết quả. Giảm thiểu sai sót, tiết kiệm thời gian và nâng cao hiệu quả chấm thi.

---

## 👨‍🏫 Giảng viên hướng dẫn
**Cô Trần Mai Hương**

---

## 👥 Nhóm thực hiện
- **Team Leader:** Nguyễn Việt Đức
- **Các thành viên:**
  1. Hoàng Bình Định
  2. Nguyễn Việt Đức
  3. Nguyễn Trung Đức
  4. Lê Minh Tiến

---

## 🔥 Chức năng chính
- Quét ảnh **đáp án mẫu**.
- Quét ảnh **bài thi cần chấm**.
- Nhận diện số báo danh (SBD), mã đề thi (MDT), đáp án.
- Tự động so sánh, tính điểm.
- Hiển thị kết quả và lưu ảnh kết quả.
- Giao diện trực quan, dễ sử dụng.

---

## 🧩 Luồng hoạt động chính

1. **Khởi động ứng dụng**  
2. **Chọn ảnh đáp án mẫu**
3. **Xử lý và trích xuất đáp án mẫu**
4. **Chọn ảnh bài thi cần chấm**
5. **Trích xuất SBD, MDT, đáp án bài làm**
6. **So sánh với đáp án mẫu & tính điểm**
7. **Hiển thị kết quả lên giao diện**
8. **Lưu kết quả về máy**

---

## 🎯 Sơ đồ luồng hoạt động

![Sơ đồ luồng](A_flowchart_in_a_digital_image_illustrates_the_flo.png)

---

## 💻 Công nghệ sử dụng
- **Python 3**
- **OpenCV** (Xử lý ảnh)
- **Tkinter + ttkbootstrap** (Giao diện người dùng)
- **PIL (Pillow)** (Xử lý ảnh nâng cao)

---

## 📂 Hướng dẫn sử dụng

### Cách chạy phần mềm:
```bash
python cham_thi_tu_dong_beta_1.1.py
