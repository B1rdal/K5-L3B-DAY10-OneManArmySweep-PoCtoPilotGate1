# Team

## Thông tin nhóm

- Tên nhóm: OneManArmySweep
- Lớp: L3B
- Repo: `K5-L3B-DAY10-OneManArmySweep-PoCtoPilotGate1`
- Thẻ sự cố: S5 (bốc ngẫu nhiên cho bài làm cá nhân).
- Số thành viên: 1.

## Thành viên

| STT | Họ và tên | MSSV | Vai | Trưởng nhóm |
|---:|---|---|---|:---:|
| 1 | Dao Duc Son | 2A202604105 | Kỹ sư cổng; Sản phẩm và kinh doanh; Vận hành và pháp lý | Có |

## DaoDucSon-2A202604105

### Phần việc phụ trách

Vòng 2: Phiếu C C0–C12, chỉ số theo dõi chi phí, phạm vi pilot theo kho, quyết định v2 và gói bài nộp.

Vòng 1: câu 1.1–1.6 (Phiếu A), câu 2.1–2.10 và quyết định v1 (Phiếu B), `lab10/guards.py`, `config/acceptance_criteria.json`, `config/operating_gates.json`.

### Đóng góp cụ thể

Hồ sơ vòng 1 gồm tiêu chí chấp nhận, phân tích rủi ro, ba cổng phòng ngừa, cấu hình kinh doanh/vận hành/pháp lý, kết quả kiểm thử, runbook và quyết định Gate 1 v1.

### Bằng chứng

Vòng 2: grade `R-S5-grade-20261119-181231-ed310d`; visible và regression đạt; quyết định v2 **Thu hẹp**. Xem `submission/round2/README.md` và Form C.

Xem Phiếu A mục A5 (commit tiêu chí), Phiếu B mục B0/B8 (run ID và checkpoint); bản tổng hợp là `submission/round1/README.md`. Commit ký `21cf02d`; checkpoint `244f5db1`; baseline `R-base-before-20261119-152719-bde05c`; prepared `R-base-prepared-20261119-153024-6ab0ad`. Kết quả:110/110,13public tests và9probes; report/trace/journal thực tế trong `submission/round1/runs/` và `checks/`.

### Exit ticket

- Điều học được: pass_rate cao chưa đủ để chọn pilot; phải đọc riêng chi phí từng kho, nguồn tiền đã trả và sức người nhận các ca chuyển tay. Scope phải phản ánh nơi tự động hóa tạo giá trị, đồng thời tính cả chi phí phần bị loại.
- Điều còn chưa chắc: giả định ledger nhất quán, giá công và năng lực duyệt trong mock có giữ được khi CSKH và assistant cùng ghi, khách nhắn lại và lưu lượng thật tăng đột biến hay không.
