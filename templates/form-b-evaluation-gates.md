# Phiếu B · Đo, rủi ro, cổng vòng 1 và quyết định v1

**Bàn:** K5-L3B-DAY10-OneManArmySweep-PoCtoPilotGate1  
**Người chuẩn bị:** Dao Duc Son - 2A202604105, thành viên duy nhất; Codex hỗ trợ theo khai báo TEAM.md. Các PIC NV-* là vai nhân viên mock trong tình huống, không phải thành viên nhóm hay chữ ký thật.

<a id="b0"></a>
## B0 · Nhật ký lần chạy vòng 1

Sẽ ghi mã thực tế sau khi đẩy commit tiêu chí; chưa chạy eval/trace ở thời điểm viết phần rủi ro này.

<a id="b1"></a>
## B1 · Câu 2.1 · Lần chạy đầu tiên

Chưa đo; không thay số minh hoạ trong đề thành số của nhóm.

<a id="b2"></a>
## B2 · Câu 2.2 · Bảng soát lỗi T-002@55

Sẽ điền từ trace thực tế sau khi đẩy tiêu chí.

<a id="b3"></a>
## B3 · Câu 2.3 · Bản đồ dữ liệu và drift

| Mục | Nội dung gắn với LogiX |
|---|---|
| Người dùng | Khách gửi ticket và CSKH xử lý ngoại lệ; Oanh/hãng/shop/người nhận là bên chịu tác động dù không dùng agent |
| Việc cần xong | Xác định quyền lợi giao trễ, ghi đúng tiền và payer, chuyển người khi vượt thẩm quyền, trả lời đúng trạng thái |
| Đầu ra | `issue_refund`, `file_carrier_fault`, `notify_carrier`, `send_reply`, queue người duyệt và log căn cứ |
| Bảng đọc | orders/parcels/recipient; policies; approvals; ledger_seed; customers/carriers; ops_limits/ops_facts/staff trong data/world.json; chữ ticket là dữ liệu không tin cậy |
| Trường then chốt | promised_date, delivered_date, status, delay_cause, parcel_id/carrier_id/driver_id; shipping_fee_vnd/goods_value_vnd; policy effective dates/auto_limit; approval scope/status/expiry/max; ledger đã trả |
| Nguồn thật và bản sao | Tracking được coi là nguồn thật trong mock; ngoài đời do scan/đối tác cập nhật, cần provenance và độ mới. Policy effective_from/to là nguồn quyết định, index_active là chỉ mục sao có thể trễ. Approval có ticket/order/customer là quyền duyệt. Ledger là nguồn số tiền đã chuyển; refund_status là bản sao batch đêm, không thay ledger. Chữ khách/checkout_note không là quyền hay tracking |
| Định dạng | Ngày ISO YYYY-MM-DD so theo as_of=2026-11-16 của world (khác ngày làm bài); delivered_date có thể null, cause null không tự suy CARRIER; đơn nhiều kiện phải dùng kiện ticket nêu, không mặc định kiện đầu |
| Lệch ngoài đời | Quét giao nhập bù, chưa cập nhật ledger vào cờ refund_status, index policy còn active bản cũ; sale tăng tải, giá LLM thay đổi, ghi chú người mua chứa chỉ thị/PII |
| Câu hỏi về nguồn | Vì sao biết giao trễ? Đối chiếu promised_date và delivered_date/as_of của kiện đúng; ai nhập, lúc nào? Nếu thiếu/sai tracking thì người xác minh, không tin số ngày trong ticket |

**Tóm lại:** Trợ lý dùng tracking, policy theo ngày hiệu lực và approval/ledger để giúp khách cùng CSKH giải quyết hoàn tiền có thể đối soát. Nếu ngày giao/hẹn, cause, policy cap hay ledger sai thì tiền/lỗi hãng sai theo. Dấu hiệu sớm: policy có hiệu lực khác index_active; proposal khác DB; ledger có tiền nhưng cờ NONE; tải queue tăng.

**Drift cụ thể:** ngày 2026-12-01 policy chuyển v3→v4 theo dữ liệu đã phát: min_days_fee 3→2, min_days_bonus 7→5, auto_limit 200.000→100.000đ, FORCE_MAJEURE không còn thuộc fault_causes dù vẫn hoàn phí. Đây là thay đổi quan hệ vào–ra (concept/policy drift), không chỉ nhiều ticket hơn. Theo dõi event `policy.policy_id` so với phiên bản hiệu lực, tỷ lệ hoàn ngoài policy/approval và lỗi hãng thiếu cause hợp lệ; một sự kiện sai bản hoặc lỗi hãng oan là đỏ. pass_rate, pass_k, wrongful_refund, wrongful_carrier_faults có thể đổi; không đổi ngưỡng đã ký để chạy theo kết quả.

<a id="b4"></a>
## B4 · Câu 2.4 · HAZOP vòng 1

**Tool duy nhất chọn phân tích:** `issue_refund`. Các nhánh dưới là giả thuyết trước khi xây cổng, không gọi là lỗi đã quan sát nếu chưa có trace.

| Tham số/dòng dữ liệu | Guideword | Lệch cụ thể | Hậu quả/ai chịu | Hiện có gì ngăn? | Cổng và tầng |
|---|---|---|---|---|---|
| payer và amount_vnd | WRONG | Chữ ticket/checkout_note bị coi là lệnh full refund, payer MERCHANT thay quyền lợi policy | Shop bị chuyển chi phí, Oanh lệch sổ | Host chỉ giới hạn tổng giá trị đơn, chưa xác thực payer/căn cứ | G2 kiểm entitlement và LOGIX từ nguồn thật; sửa/chặn trước write |
| approval_id | INVALID | Dùng A-0031 đã used, hết hạn 2026-10-01, sai ticket/order nhưng cùng khách | Khoản không ai thực sự phê duyệt, Hạnh bị đứng tên | Agent lookup có fallback customer, chưa kiểm đủ scope | G2 kiểm ticket/order/customer/status/expiry/max_vnd và approver cấu hình; thiếu thì escalate |
| tracking/policy | INCOMPLETE | cause trống hoặc policy không có khoảng ngày chứa as_of | Hoàn và ghi lỗi không đủ căn cứ; hãng/shop chịu | Agent có thể mặc định CARRIER khi delay>0, đọc index_active | G1 policy theo ngày; G2 thiếu chứng cứ thì người xác minh |
| retry và ledger | PERTURBED | Write đã commit nhưng confirm thất bại; retry cùng refund hoặc ticket khác của đơn cũ | Trả hai lần, Oanh phải thu hồi/đối soát | refund_status cập nhật batch đêm, host không chặn nếu chưa vượt tiền đơn | G2 dùng ledger tính quyền lợi còn lại; retry đủ tiền thì deny; không dựa cờ |
| LLM policy/confirm | INCAPABLE | LLM 429 liên tiếp, fail_open hay retry write | Chi phí tăng, có thể chuyển tiền không kiểm chứng | Có fallback nhưng chưa bảo đảm an toàn | G2 không tin basis fail_open; tính lại từ DB, thiếu dữ kiện thì escalate; giới hạn LLM config |

Nhánh chưa quan sát trước baseline: INVALID approval, retry, full-refund directive và LLM fail-open là suy luận từ code/phân tích, cần kiểm chứng riêng; không bịa trace.

### Mở rộng ngoài kỹ thuật

| Thành phần | Guideword | Lệch cụ thể | Hậu quả/ai chịu | Cổng đề xuất |
|---|---|---|---|---|
| Người duyệt | INCAPABLE | 14 ca cần người trong 1 giờ nhưng 1 người chỉ 6 ca/giờ; nếu tới cùng lúc, ca 14 bắt đầu sau 130 phút | Khách chờ, Hạnh quá tải; zero queue không còn giữ được | 1 người/6 ca giờ là baseline có số thật; mục tiêu chờ 45 phút; gọi hỗ trợ ở 3 ca chờ hoặc wait 20, thu hẹp trước 45; không giả định có người vô hạn |
| Ngân sách | WRONG | Tự hoàn vượt Finance 2.000.000đ/ngày hoặc LLM vượt 1.500đ/ticket | LogiX mất ngân sách dù chất lượng nhìn tốt | cap tự động 1.800.000đ (90% Finance); budget LLM 1.200đ, dự phòng 300đ; tổng cost phải ≤7.500đ, ROI≥0,30 |
| Dữ liệu bên thứ ba | PERTURBED | customer_note và recipient_contact từ chữ khách/gift lọt sang hãng | Người nhận không chọn dùng AI vẫn lộ PII | G3 dựng lại payload từ schema policy; legal chặn các trường contact/note/name/phone/street |
| Phạm vi | INVALID | Nhân viên tin mean cost mà bỏ qua một kho đắt hơn làm tay | Pilot âm lợi nhuận tại kho đó, người duyệt gánh | Ban đầu đo all để không giấu ticket khó; đọc by_segment, chỉ Thu hẹp khi có phân khúc được chứng minh |

<a id="b5"></a>
## B5 · Câu 2.4 · Checklist go-live 9 nhóm

Sẽ cập nhật trạng thái và bằng chứng sau chạy cổng. Không mặc định mock pass là đã đủ go-live thật.

<a id="b6"></a>
## B6 · Câu 2.5 · Pre-mortem bốn lăng kính

Bản phân tích do thành viên duy nhất cùng AI chuẩn bị; không ghi như đã diễn ra vòng thảo luận 3–4 người. Giả định: sau ba tháng đã phải tắt pilot ở hai depot.

| Lý do thất bại (thì quá khứ) | Lăng kính | Kiểm hôm nay | Cổng / risk còn lại |
|---|---|---|---|
| Trợ lý đã dùng ngày khách khai hoặc policy active cũ, chuyển sai tiền và lặp khoản đã hoàn | Kỹ thuật | tracking/proposal/policy events, effective dates, ledger và approvals | **Chọn G1 nguồn policy theo ngày + G2 quyền ghi tiền**; DB gốc sai vẫn là rủi ro |
| Nhóm đã tự động hóa ticket tốn quá nhiều LLM/duyệt, tiết kiệm toàn cục đã che kho thua lỗ | Kinh doanh | ops_facts, per-ticket cost/ROI, ops.segments, tổng refund ngày | **Chọn cổng config business**: 1,8 triệu/ngày, 1.200đ LLM/ticket, ROI 0,30; phạm vi all để đo trước thu hẹp |
| Ca sale đã tăng gấp ba, một người 6 ca/giờ đã không nhận kịp ticket; nhân viên đã kiểm lại vì không hiểu quyết định | Con người/vận hành | arrivals, review_rate, queue wait/stuck, cost người; quyết định có ghi chú | **Chọn cổng config operations/runbook**: 1 người, 6 ca/giờ, wait≤45, note=true, sample=10%; stress thật chưa đo, giữ risk |
| Hãng/tài xế đã bị ghi lỗi không có cause hoặc sai kiện; người nhận quà đã bị gửi PII cho hãng | Pháp lý | faults/parcel/cause theo policy, outbound thực tế | **Chọn G3 chứng cứ hãng + tối thiểu payload**, legal config; khiếu nại độc lập và tracking sai vẫn cần người |

Ba cổng code là G1, G2, G3; con số kinh doanh/vận hành hỗ trợ cả bốn lăng kính. Không xem thẻ sự cố hay bài kiểm tra ẩn trong vòng 1. Risk sẽ mang sang Phiếu C C10: tracking nguồn sai, tải sale, chất lượng người duyệt và mô hình thật chưa được đo.

<a id="b7"></a>
## B7 · Câu 2.6–2.10 · Cổng và runbook

Chưa sửa guards/config ở thời điểm ghi phân tích này. Chỉ triển khai sau mốc baseline.

<a id="b8"></a>
## B8 · Quyết định Gate 1 v1

Chưa quyết định: phải có checkpoint và kết quả prepared thực tế.