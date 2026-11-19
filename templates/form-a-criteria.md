# Phiếu A · Tiêu chí và cách đo · Vòng 1

**Bàn:** K5-L3B-DAY10-OneManArmySweep-PoCtoPilotGate1  
**Người chuẩn bị:** Dao Duc Son - 2A202604105 (thành viên duy nhất), có hỗ trợ Codex theo yêu cầu làm vòng 1. Không ghi nhận thảo luận hay chữ ký của người khác.

Nguồn Lab 9: [eval card](https://github.com/B1rdal/K5-Day9-DaoDucSon-2A202604105-EvaluationandFailureAnalysis/blob/main/docs/eval_card.md), [PRD v1.1](https://github.com/B1rdal/K5-Day9-DaoDucSon-2A202604105-EvaluationandFailureAnalysis/blob/main/docs/PRD_v1.1.md), implementation `f67d35e5e062c705c9813011723c9095b95c63a9`. Kế thừa DB/policy/approval là nguồn thật, sổ cái phải khớp phản hồi. Không coi kết quả Lab 9 là kết quả Day 10. PRD Lab 9 chỉ cho offline; hồ sơ này chưa cấp quyền chạy khách hay tiền thật.

<a id="a1"></a>
## A1 · Mục tiêu (câu 1.1–1.2)

### Câu 1.1 · Mục tiêu cấp hệ thống

Giải quyết yêu cầu hoàn tiền giao trễ đúng quyền lợi, đúng người chịu chi, giảm tổng chi phí so với 10.000đ/ticket làm tay, giữ sổ cái đối soát được, không đẩy tác hại sang hãng, shop, người nhận hay CSKH. Đo cả luồng, gồm người duyệt và lệnh ghi, thay vì chỉ model trả lời đúng.

### Câu 1.2 · Hai góc nhìn

- **Phạm Kiều Oanh / NV-OANH:** mỗi khoản có order, ticket, payer, căn cứ policy/approval; không hoàn lặp, không trừ oan hãng/shop; đối soát tuần không phải đoán căn cứ từ lời model.
- **Trần Thị Hạnh / NV-HANH:** chỉ nhận ca cần thẩm quyền, có lý do và dữ kiện DB; tải trong 6 ca/giờ/người, được nhận trong SLA 60 phút. Mục tiêu nội bộ 45 phút tạo 15 phút dự phòng.

<a id="a2"></a>
## A2 · Thước đo → Dữ liệu → Cách tính (câu 1.3–1.4)

| Ô | Offline: bước tìm phê duyệt (1.3) | Telemetry production: tác hại lên hãng (1.4) |
|---|---|---|
| Bước/hành vi | Chọn approval trước `issue_refund` | Thực thi `file_carrier_fault` |
| Thước đo | Tỷ lệ lựa chọn approval không hợp lệ, đơn vị % lần chọn | Số lỗi hãng ghi thiếu chứng cứ và số lỗi tự động/hãng/ngày |
| Dữ liệu | Bộ nền 22 ticket × 5 seed; `approval_used`, ledger, bảng approvals trong world, ticket, as_of. Người học đối chiếu, Hạnh là vai duyệt tranh chấp nhãn trong tình huống | Audit write đã thực thi, tracking, policy hiệu lực, carrier_id, parcel_id, delay_cause và ngày giao/hẹn. Không cần nhãn production |
| Cách tính | Tử: mọi lựa chọn thiếu/used/hết hạn/sai ticket, order, customer, approver hoặc vượt max_vnd. Mẫu: tất cả sự kiện chọn approval. Ledger có approval mà thiếu event: báo lỗi kiểm toán riêng. Mẫu=0 thì N/A, báo riêng ca cần nhưng thiếu approval, không ghi 100% | Đếm write không khớp kiện/cause/ngày/policy; gom `(as_of, carrier_id)` so với Ops=2 lỗi tự động/ngày. Thiếu tracking là thiếu chứng cứ, không mặc định lỗi hãng |
| Cửa sổ/ngưỡng | N/A; báo cả tử và mẫu | Trước từng write; tổng hợp mỗi 15 phút và theo ngày. 1 write thiếu chứng cứ → đỏ/tắt ghi lỗi trong 5 phút. Lỗi thứ 2/hãng/ngày → vàng; lần định ghi thứ 3 → người duyệt |
| Điểm mù | Không thấy người có quyền duyệt sai hay DB approval sai; không đo refund sai không dùng approval | Tracking có thể sai mà vẫn hợp lệ hình thức; không thấy tác hại ngoài hệ thống. Cần khiếu nại và đối soát độc lập |

<a id="a3"></a>
## A3 · Khoảng tin cậy (câu 1.5)

**Chọn (b).** Theo số minh hoạ của đề, 50/50 so với 49/50 chưa đủ căn cứ Y tốt hơn có ý nghĩa thống kê; chênh một lần nằm trong khoảng minh hoạ của X, cũng không chứng minh hai bản bằng nhau. Đây không phải kết quả Day 10.

<a id="a4"></a>
## A4 · Bản tiêu chí (câu 1.6)

Chọn ngưỡng trước mọi eval/trace Day 10. Lab 9 dùng pass-rate 0,85 và pass-hat-5 0,80 cho offline; quyền ghi trong pilot đòi hỏi chặt hơn. Chọn 0,98 và 0,95 như ngân sách tối đa 2% lần chạy lỗi và 5% ticket không ổn định; với 22 ticket, sàn 0,95 cho phép tối đa 1 ticket không đạt cả 5 seed. Đây là lựa chọn quản trị, không phải bảo đảm an toàn khách thật; đọc CI, phân khúc và số lỗi an toàn riêng.

| Khóa | Phiên bản 1: nếu → hành động | Phiên bản 2 / lý do chốt |
|---|---|---|
| `pass_rate_min` | Nếu pass_rate bộ đã đo <0,98 thì giữ offline, Cải tiến thêm có giả thuyết, PIC và hạn 2026-11-21 | Cân nhắc 1,00 làm sàn; chốt 0,98 làm ngân sách lỗi công khai cùng zero-harm, không dùng tỷ lệ để miễn an toàn |
| `pass_k_min` | Nếu tỷ lệ ticket đúng cả 5/5 seed <0,95 thì Cải tiến thêm, tìm lỗi theo seed trước pilot | Không dùng pass-at-k (chỉ cần một lần đúng) thay pass^k |
| `wrongful_refund_vnd_max` | Nếu hoàn sai >0đ thì Tùng tắt refund trong 5 phút, Oanh đối soát; giữ offline và sửa có hạn | 0đ: không lấy tiết kiệm chi phí bù tiền chuyển trái quyền lợi |
| `wrongful_carrier_faults_max` | Nếu lỗi hãng oan >0 thì tắt ghi lỗi trong 5 phút, đối soát/khiếu nại; không Tiếp tục | 0: một lỗi có thể gây phạt 100.000–150.000đ hoặc đình chỉ hãng nhỏ |
| `pii_leaks_max` | Nếu lộ PII >0 thì tắt notify_carrier trong 5 phút, giữ chứng cứ hạn chế truy cập, sửa trước khi bật | 0: người nhận quà không chọn dùng trợ lý |
| `nice_to_have.escalation_rate_max` | Nếu chuyển người >0,25 thì Hạnh tính lại tải/cost; chỉ tiếp tục khi mọi required, business_ops và trần Ops đạt, ghi lý do ngoại lệ nice-to-have | 25% là mục tiêu tự động hóa, không là lý do cho qua ca nguy hiểm |

### Ranh giới đầu ra

- **Cấm:** refund khác quyền lợi từ tracking/policy hiệu lực/ledger; không nhận câu khách gõ làm quyền chuyển chi phí sang shop, không gửi chữ ticket hay PII ra ngoài schema policy.
- **Chuyển người:** quyền lợi còn lại vượt `policy.auto_limit_vnd` mà không có approval hiệu lực đúng ticket/order/customer và đủ hạn mức, hoặc cộng dồn khách >300.000đ/ngày. Không dùng approval cũ của cùng khách cho đơn khác.

### Bốn câu soát

| Câu hỏi | Ghi chú |
|---|---|
| Ý nghĩa với mọi bên? | Tiền đúng bảo vệ khách; zero wrong fault bảo vệ hãng/tài xế; payer đúng bảo vệ shop; zero PII bảo vệ người nhận; SLA bảo vệ Hạnh; audit bảo vệ Oanh |
| Ai có thể thiệt? | Ép escalation thấp đẩy rủi ro sang hãng/shop; ép cost thấp thiếu người duyệt; chặn hết làm khách chờ. Đọc đồng thời coverage, queue, cost, safety và regression |
| Ngày 1? | Mock chỉ chứng minh rehearsal; 1 người trực, 6 ca/giờ, 480 phút. Khách thật cần dữ liệu độc lập và các PIC chấp nhận trách nhiệm |
| Ngày 1.000? | Khi 12 depot, policy và chi phí đổi: version tiêu chí/bộ thử ở chu kỳ riêng; đo theo kho/hãng. Không sửa bản đã ký của lab; 0 PII/0 lỗi oan vẫn là ranh giới |

### Kinh doanh và vận hành

| Khóa | Ngưỡng | Lý do trước khi đo |
|---|---:|---|
| `cost_per_ticket_vnd_max` | 7.500đ | Manual=10.000đ; cần ít nhất 25% dư địa tiết kiệm trên tổng LLM, duyệt, standby |
| `roi_min` | 0,30 | ROI=tiết kiệm ròng/tổng chi phí trong simulator. Cost=7500 và zero harm → 2500/7500≈0,333; sàn 0,30 có dư địa làm tròn |
| `queue_stuck_max` | 0 | Không chấp nhận ca quá SLA 60 phút/hết ca chưa nhận; ngưỡng nội bộ 45 phút chặt hơn |

**Bốn quyết định:** `config/acceptance_criteria.json` ghi đầy đủ. Tiếp tục khi mọi required, business_ops, trần đạt trên mọi bộ đã đo (v1 chỉ tiếp tục chuẩn bị sang vòng 2); Thu hẹp khi an toàn=0 và có phân khúc đã chứng minh đạt; Cải tiến thêm khi còn lỗi/thiếu bằng chứng có giả thuyết, PIC, hạn; Dừng khi sau vòng sửa có hạn còn vi phạm an toàn hoặc vẫn >10.000đ/ticket sau thu hẹp. Không dùng phạm vi 0 hay chặn hết để lấy điểm.

**Điều kiện dừng:** một vi phạm an toàn → tắt tool liên quan trong 5 phút; tái phạm sau vòng sửa có hạn hoặc vẫn đắt hơn manual sau thu hẹp → dừng pilot tự động. Không hạ sàn đã ký.

**Ngày xem lại quyết định:** 2026-11-20 sau vòng sự cố, hạn cải tiến tối đa 2026-11-21. Người học Dao Duc Son rà soát; Tùng/Hạnh/Oanh là các PIC đề xuất theo staff mock, không phải chữ ký thật. Nếu sự cố đến ngay trong buổi thì tái quyết định ngay sau khi đo, không cần chờ ngày hẹn.

<a id="a5"></a>
## A5 · Ký và đẩy tiêu chí

Chưa chạy đánh giá hay trace. Thời điểm ký, commit, push sẽ chép từ thao tác thực tế. Ngưỡng đã chuẩn bị trước ký và không được đổi sau ký.