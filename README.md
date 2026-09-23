# VNPL Partner Onboarding (Interim)

**[English](#english)** · **[Tiếng Việt](#tiếng-việt)**

---

## English

### 1. What this tool is

A small, temporary web app where new **clients** and **vendors** get a recorded **Finance + Legal decision** before Ops sets them up in **Sota** (our FMS).

It does three things:

1. **Standard intake.** Sales submits new clients; Procurement/Ops submits new vendors.
2. **Parallel review.** Finance and Legal review at the same time. Large or unusual cases go to an Approver.
3. **Sota export.** Approved partners are exported as CSV files (with the correct salesperson and Sota sales code), ready to import into Sota.

It is **not** a CRM. It will be retired when **Polaris CRM** goes live (about 8–11 weeks). Documents stay in **SharePoint**; this tool stores links only. Do **not** enter bank account numbers or ID/passport numbers.

The interface is in Vietnamese. Menu and button names below are quoted exactly as they appear on screen.

### 2. Roles

| Role (group) | Who | Can do |
|---|---|---|
| **Sales** | Forwarding sales | Create and submit **client** requests. Sees only their own requests. |
| **Procurement** | Ops / procurement | Create and submit **vendor** requests. Sees only their own requests. |
| **Finance** | Finance (TCKH) | Finance review. Sees all requests. Can change the salesperson and client code after approval. |
| **Legal** | Legal / admin-legal | Legal review. Sees all requests. |
| **Approver** | Board member / delegated manager | Decides escalated requests. |
| **Exporter** | Ops coordinator | Exports approved partners to Sota CSV. |
| **Admin** | IT/Digital | Users, roles, salesperson list, everything else. |

One person can hold several roles. **Nobody can review or approve their own request**; the system blocks it.

### 3. The workflow

```
Draft ──submit──► In review ──┬─ any reviewer requests changes ─► Changes requested ──resubmit──► In review
                              ├─ any reviewer rejects ──────────► Rejected (final)
                              ├─ both approve, no trigger ──────► Approved ──export──► Exported to Sota
                              └─ both approve + trigger ────────► Escalated ──► Approved / Rejected
```

| Status on screen | Meaning |
|---|---|
| Nháp | Draft, only the creator sees and edits it |
| Đang duyệt | Waiting for Finance and Legal |
| Yêu cầu chỉnh sửa | A reviewer asked for changes; the creator edits and resubmits |
| Chờ cấp trên duyệt | Escalated, waiting for the Approver |
| Đã duyệt | Approved, ready for Sota export |
| Từ chối | Rejected, read-only, final |
| Đã xuất Sota | Included in a Sota export file |

**Escalation triggers** (current test values; Finance will confirm the real ones):
- Requested credit limit **above 500,000,000 VND**, or
- Payment terms **longer than 45 days**, or
- Legal answers **"No"** to "Dùng hợp đồng mẫu" (standard contract used).

**Resubmission** starts a new review round: Finance and Legal must both review again. Earlier decisions and comments stay visible in the history.

### 4. How to use it, by role

Log in at the tool's address with the username and temporary password IT gives you. On first login you must set a new password.

#### 4.1 Sales: new client
1. Menu **"Khách hàng"** → **"Thêm vào"** (Add).
2. Fill in the form. You can save as a draft at any time.
   Required before submitting: MST, registered address, **salesperson** ("Nhân viên kinh doanh"), invoice name, e-invoice email, payment terms.
   - **Salesperson** is the person who owns the client in Sota, not necessarily you. Pick from the list.
   - **MST** must be 10 digits, or 10 digits + "-" + 3 digits for a branch (e.g. `0101234567-001`).
   - Tick **"Có thu hộ / chi hộ"** if the client will have pass-through payments, and describe them.
   - Paste SharePoint links for the business registration and contract/quotation.
   - Add at least one business contact at the bottom ("Người liên hệ").
3. Save.
4. To submit: in the **"Khách hàng"** list, tick your request → action dropdown **"Gửi duyệt"** → **"Đi đến" (Go)**.
5. If the system says the **MST or company name already exists**, check the listed request numbers. If it really is a new client, open your request, fill **"Lý do tạo dù trùng"** (reason), save, and submit again.
6. If a reviewer requests changes, the status becomes **"Yêu cầu chỉnh sửa"**. Read their comment at the bottom of the request, edit, save, and submit again.

#### 4.2 Procurement / Ops: new vendor
Same steps under menu **"Nhà cung cấp"**.
Required: vendor type, country, payment terms, and **either** MST **or** a foreign registration number (for overseas vendors). Salesperson is optional for vendors for now.

#### 4.3 Finance reviewer
1. Find work: **"Khách hàng"** or **"Nhà cung cấp"** → filter **"Hàng đợi" → "Chờ tôi duyệt"** (waiting for my review). Open a request to read it.
2. To decide: menu **"Duyệt Tài chính"** → **"Thêm vào"** → choose the request under "Đối tác" (only requests waiting for review are listed).
3. Fill the checklist (Có / Không / N/A), an evidence link if you have one, and a decision:
   - **Duyệt**: approve.
   - **Duyệt có điều kiện**: approve with conditions. The conditions text is **required** and is included in the Sota export.
   - **Yêu cầu chỉnh sửa**: send it back to the creator. A comment is **required**.
   - **Từ chối**: reject (final). A comment is **required**.
4. Save. Decisions cannot be edited afterwards.

Finance can also enter the **client code** ("Mã khách hàng") and change the **salesperson** at any time after submission. If the partner was already exported, it is flagged **"Thay đổi sau khi xuất"** so Ops re-exports it.

#### 4.4 Legal reviewer
Same as Finance, using menu **"Duyệt Pháp chế"** and the legal checklist.
If the standard contract was **not** used, answer "Không" and write the deviation summary; this escalates the request to the Approver once both reviews are positive.

#### 4.5 Approver
Filter **"Chờ tôi duyệt"** shows escalated requests. Decide via menu **"Duyệt cấp trên"** → **"Thêm vào"**: **Duyệt** or **Từ chối** (a comment is required to reject).

#### 4.6 Ops exporter: export to Sota
1. **"Khách hàng"** (or **"Nhà cung cấp"**) → filter **"Hàng đợi" → "Sẵn sàng xuất Sota"**. This lists new approvals and exported partners changed since their last export.
2. Tick the rows → action **"Xuất CSV cho Sota"** → **"Đi đến" (Go)**. A CSV file downloads (UTF-8, opens correctly in Excel with Vietnamese characters).
3. Rows missing a required Sota field (e.g. **the salesperson has no Sota code**) are **left out, never half-filled**. The reason appears as a warning the next time the page loads. Fix the data (IT adds the Sota code in "Nhân viên kinh doanh") and export again.
4. Clients and vendors are exported separately, one file per type.
5. Every export is logged under menu **"Lô xuất Sota"** (who, when, which records, what was left out, file content).

#### 4.7 Everyone
- **Comments**: at the bottom of each request ("Bình luận"). Comments cannot be edited or deleted.
- **History**: each request shows its review history ("Lịch sử duyệt") and a full audit log ("Nhật ký") of who changed what and when, with before/after values. The global log is under menu **"Nhật ký"**.
- **Search**: by request number (REQ-2026-xxxx), company name, or MST.
- Nothing can be deleted.

### 5. Login and security
- IT creates your account with a **temporary password**; you must change it at first login.
- **5 wrong passwords lock the account for 15 minutes.**
- You are logged out after **60 minutes** without activity.
- Forgot your password? Ask IT; there is no self-service reset.

### 6. For IT / Admin
- **Add a user:** menu "Người dùng" (Users) → Add → username + temporary password → then assign a **group** (Sales, Procurement, Finance, Legal, Approver, Exporter). "Bắt đổi mật khẩu khi đăng nhập" is ticked by default.
- **Reset a password:** set a new password on the user page, then tick "Bắt đổi mật khẩu khi đăng nhập" again.
- **Unlock an account:** on the user page, clear "Khoá đến" (locked until).
- **Salesperson list:** menu "Nhân viên kinh doanh". Every client salesperson needs a **Sota sales code**, or their clients will not export.
- **Escalation thresholds:** environment variables `ESCALATION_CREDIT_LIMIT_VND` and `ESCALATION_PAYMENT_DAYS`.

### 7. Testing guide

**Demo accounts** (test environment only), password `Vnpl@2026demo`:

| Username | Role |
|---|---|
| `sales1` | Sales |
| `proc1` | Procurement |
| `fin1` | Finance |
| `legal1` | Legal |
| `boss1` | Approver |
| `ops1` | Exporter |
| `admin` | IT admin |

Demo salespeople: **Nguyễn Văn An** (Sota code S001) and **Trần Thị Bình** (no Sota code, used to test export exceptions).

**Test scenarios.** Please run these and note anything unexpected:

| # | Steps | Expected result |
|---|---|---|
| 1 | As any user, enter a wrong password 5 times | Account locked for 15 minutes |
| 2 | As `sales1`, create a client with MST `12345` and save | Blocked with a Vietnamese error message |
| 3 | As `sales1`, create and submit a client with MST `0101234567`, salesperson Nguyễn Văn An, credit limit 100,000,000, terms 30 days | Status "Đang duyệt" |
| 4 | As `fin1` approve it; as `legal1` choose "Yêu cầu chỉnh sửa" with a comment | Status "Yêu cầu chỉnh sửa" |
| 5 | As `sales1`, edit and resubmit; `fin1` and `legal1` both approve | Both had to review again; status "Đã duyệt" |
| 6 | As `sales1`, create another client with the same MST and submit | Duplicate warning; submits only after filling the reason |
| 7 | Submit a client with credit limit 1,000,000,000; both reviewers approve | Status "Chờ cấp trên duyệt"; `boss1` approves → "Đã duyệt" |
| 8 | Log in as `sales1` and try to review your own request (give `sales1` the Finance group to test) | Your request is not in the list; the system refuses |
| 9 | As `ops1`, export the approved clients | CSV downloads, opens in Excel with correct Vietnamese; status "Đã xuất Sota"; batch appears in "Lô xuất Sota" |
| 10 | Approve a client whose salesperson is Trần Thị Bình, then export | Client left out, with the reason "Thiếu: sales_rep_fms_code" |
| 11 | As `fin1`, change the salesperson of an exported client | Flag "Thay đổi sau khi xuất"; appears again in "Sẵn sàng xuất Sota"; change recorded in "Nhật ký" |
| 12 | Create and submit a vendor as `proc1` (foreign vendor: MST empty, foreign registration number filled) | Accepted |

**Reporting issues:** send the request number (REQ-…), your username, what you did, what you expected, and a screenshot.

### 8. Known limitations (dev version)
- Submit and export are **list actions** (tick → choose action → "Đi đến"); there are no buttons on the request page yet.
- Reviewers start from the review menus, not from a button on the request.
- Export warnings show on the next page load, because the browser is downloading the file.
- One evidence link per review, not one per checklist item.
- **Sota columns are placeholders** until we receive Sota's actual import fields.
- No email notifications; check your "Chờ tôi duyệt" queue.

---

## Tiếng Việt

### 1. Công cụ này là gì

Một ứng dụng web nhỏ, dùng tạm thời, để mọi **khách hàng** và **nhà cung cấp** mới đều có **quyết định duyệt của Tài chính + Pháp chế** được ghi nhận trước khi Ops tạo trên **Sota** (hệ thống FMS).

Công cụ làm ba việc:

1. **Chuẩn hoá đầu vào.** Sales tạo yêu cầu khách hàng mới; Mua hàng/Ops tạo yêu cầu nhà cung cấp mới.
2. **Duyệt song song.** Tài chính và Pháp chế duyệt cùng lúc. Trường hợp lớn hoặc bất thường chuyển lên cấp trên.
3. **Xuất file Sota.** Đối tác đã duyệt được xuất ra file CSV (kèm đúng nhân viên kinh doanh và mã sales Sota) để import vào Sota.

Đây **không phải** CRM. Công cụ sẽ ngừng khi **Polaris CRM** go-live (khoảng 8–11 tuần). Tài liệu vẫn lưu trên **SharePoint**; công cụ chỉ lưu đường link. **Không** nhập số tài khoản ngân hàng hay số CCCD/hộ chiếu.

### 2. Vai trò

| Vai trò (nhóm) | Ai | Được làm |
|---|---|---|
| **Sales** | Sales forwarding | Tạo và gửi duyệt yêu cầu **khách hàng**. Chỉ thấy yêu cầu của mình. |
| **Procurement** | Ops / mua hàng | Tạo và gửi duyệt yêu cầu **nhà cung cấp**. Chỉ thấy yêu cầu của mình. |
| **Finance** | Tài chính (TCKH) | Duyệt Tài chính. Thấy tất cả. Được đổi nhân viên kinh doanh và mã khách hàng sau khi duyệt. |
| **Legal** | Pháp chế / hành chính-pháp chế | Duyệt Pháp chế. Thấy tất cả. |
| **Approver** | BGĐ / người được uỷ quyền | Quyết định các yêu cầu được chuyển lên cấp trên. |
| **Exporter** | Điều phối Ops | Xuất file CSV cho Sota. |
| **Admin** | IT/Digital | Người dùng, phân quyền, danh sách sales, mọi thứ khác. |

Một người có thể giữ nhiều vai trò. **Không ai được duyệt yêu cầu do chính mình tạo**; hệ thống sẽ chặn.

### 3. Quy trình

```
Nháp ──gửi duyệt──► Đang duyệt ──┬─ một bên yêu cầu chỉnh sửa ─► Yêu cầu chỉnh sửa ──gửi lại──► Đang duyệt
                                 ├─ một bên từ chối ───────────► Từ chối (kết thúc)
                                 ├─ cả hai duyệt, không vượt ngưỡng ─► Đã duyệt ──xuất──► Đã xuất Sota
                                 └─ cả hai duyệt + vượt ngưỡng ──────► Chờ cấp trên duyệt ──► Đã duyệt / Từ chối
```

| Trạng thái | Ý nghĩa |
|---|---|
| Nháp | Chỉ người tạo thấy và sửa |
| Đang duyệt | Chờ Tài chính và Pháp chế |
| Yêu cầu chỉnh sửa | Người duyệt yêu cầu sửa; người tạo sửa rồi gửi lại |
| Chờ cấp trên duyệt | Vượt ngưỡng, chờ cấp trên |
| Đã duyệt | Sẵn sàng xuất Sota |
| Từ chối | Chỉ xem, kết thúc |
| Đã xuất Sota | Đã nằm trong một file xuất Sota |

**Điều kiện chuyển cấp trên** (giá trị đang dùng để thử nghiệm; Tài chính sẽ xác nhận giá trị thật):
- Hạn mức công nợ đề xuất **trên 500.000.000 VND**, hoặc
- Thời hạn thanh toán **trên 45 ngày**, hoặc
- Pháp chế chọn **"Không"** ở mục "Dùng hợp đồng mẫu".

**Gửi lại** sẽ mở vòng duyệt mới: Tài chính và Pháp chế phải duyệt lại từ đầu. Các quyết định và bình luận cũ vẫn hiển thị trong lịch sử.

### 4. Hướng dẫn theo vai trò

Đăng nhập bằng tên đăng nhập và mật khẩu tạm do IT cấp. Lần đầu đăng nhập bắt buộc đổi mật khẩu.

#### 4.1 Sales: khách hàng mới
1. Menu **"Khách hàng"** → **"Thêm vào"**.
2. Điền form. Có thể lưu nháp bất cứ lúc nào.
   Bắt buộc trước khi gửi duyệt: MST, địa chỉ đăng ký, **nhân viên kinh doanh**, tên xuất hoá đơn, email nhận HĐĐT, thời hạn thanh toán.
   - **Nhân viên kinh doanh** là người phụ trách khách hàng trên Sota, không nhất thiết là bạn. Chọn từ danh sách.
   - **MST** gồm 10 chữ số, hoặc 10 chữ số + "-" + 3 chữ số với chi nhánh (VD: `0101234567-001`).
   - Tick **"Có thu hộ / chi hộ"** nếu khách có thu hộ/chi hộ, và mô tả.
   - Dán link SharePoint của ĐKKD và hợp đồng/báo giá.
   - Thêm ít nhất một người liên hệ ở cuối trang ("Người liên hệ").
3. Lưu.
4. Gửi duyệt: trong danh sách **"Khách hàng"**, tick yêu cầu → chọn hành động **"Gửi duyệt"** → **"Đi đến"**.
5. Nếu hệ thống báo **trùng MST hoặc tên công ty**, kiểm tra các số yêu cầu được liệt kê. Nếu đúng là khách mới, mở yêu cầu, điền **"Lý do tạo dù trùng"**, lưu và gửi lại.
6. Nếu người duyệt yêu cầu chỉnh sửa, trạng thái thành **"Yêu cầu chỉnh sửa"**. Đọc bình luận ở cuối yêu cầu, sửa, lưu và gửi duyệt lại.

#### 4.2 Mua hàng / Ops: nhà cung cấp mới
Các bước tương tự ở menu **"Nhà cung cấp"**.
Bắt buộc: loại NCC, quốc gia, thời hạn thanh toán, và **MST hoặc số đăng ký nước ngoài** (với NCC nước ngoài). Nhân viên kinh doanh hiện không bắt buộc với NCC.

#### 4.3 Người duyệt Tài chính
1. Tìm việc: **"Khách hàng"** hoặc **"Nhà cung cấp"** → lọc **"Hàng đợi" → "Chờ tôi duyệt"**. Mở yêu cầu để xem.
2. Ra quyết định: menu **"Duyệt Tài chính"** → **"Thêm vào"** → chọn yêu cầu ở ô "Đối tác" (chỉ hiện các yêu cầu đang chờ duyệt).
3. Điền checklist (Có / Không / N/A), link bằng chứng nếu có, và chọn quyết định:
   - **Duyệt**.
   - **Duyệt có điều kiện**: **bắt buộc** nhập điều kiện; điều kiện sẽ nằm trong file xuất Sota.
   - **Yêu cầu chỉnh sửa**: trả về người tạo. **Bắt buộc** nhận xét.
   - **Từ chối**: kết thúc. **Bắt buộc** nhận xét.
4. Lưu. Quyết định không sửa được sau khi lưu.

Tài chính cũng nhập được **mã khách hàng** và đổi **nhân viên kinh doanh** sau khi yêu cầu đã gửi. Nếu đối tác đã xuất Sota, hệ thống đánh dấu **"Thay đổi sau khi xuất"** để Ops xuất lại.

#### 4.4 Người duyệt Pháp chế
Như Tài chính, dùng menu **"Duyệt Pháp chế"** và checklist pháp chế.
Nếu **không** dùng hợp đồng mẫu, chọn "Không" và ghi tóm tắt sai khác; yêu cầu sẽ chuyển cấp trên khi cả hai bên đều duyệt.

#### 4.5 Cấp trên (Approver)
Bộ lọc **"Chờ tôi duyệt"** hiện các yêu cầu được chuyển lên. Quyết định ở menu **"Duyệt cấp trên"** → **"Thêm vào"**: **Duyệt** hoặc **Từ chối** (từ chối bắt buộc nhận xét).

#### 4.6 Ops: xuất file Sota
1. **"Khách hàng"** (hoặc **"Nhà cung cấp"**) → lọc **"Hàng đợi" → "Sẵn sàng xuất Sota"**. Danh sách gồm các đối tác mới duyệt và đối tác đã xuất nhưng có thay đổi sau đó.
2. Tick các dòng → hành động **"Xuất CSV cho Sota"** → **"Đi đến"**. File CSV được tải về (UTF-8, mở bằng Excel hiển thị đúng tiếng Việt).
3. Dòng nào thiếu trường bắt buộc của Sota (VD: **nhân viên kinh doanh chưa có mã Sota**) sẽ **bị loại, không bao giờ xuất thiếu**. Lý do hiện thành cảnh báo ở lần tải trang kế tiếp. Sửa dữ liệu (IT bổ sung mã Sota trong "Nhân viên kinh doanh") rồi xuất lại.
4. Khách hàng và nhà cung cấp xuất riêng, mỗi loại một file.
5. Mọi lần xuất được ghi ở menu **"Lô xuất Sota"** (ai, khi nào, bản ghi nào, bản ghi nào bị loại, nội dung file).

#### 4.7 Mọi người
- **Bình luận**: ở cuối mỗi yêu cầu ("Bình luận"). Không sửa, không xoá được.
- **Lịch sử**: mỗi yêu cầu có "Lịch sử duyệt" và "Nhật ký" ghi lại ai đổi gì, lúc nào, giá trị trước/sau. Nhật ký chung ở menu **"Nhật ký"**.
- **Tìm kiếm**: theo số yêu cầu (REQ-2026-xxxx), tên công ty hoặc MST.
- Không thể xoá bất cứ dữ liệu nào.

### 5. Đăng nhập và bảo mật
- IT tạo tài khoản với **mật khẩu tạm**; bắt buộc đổi ở lần đăng nhập đầu.
- **Sai mật khẩu 5 lần sẽ khoá tài khoản 15 phút.**
- Tự đăng xuất sau **60 phút** không thao tác.
- Quên mật khẩu? Liên hệ IT; không có chức năng tự đặt lại.

### 6. Dành cho IT / Admin
- **Thêm người dùng:** menu "Người dùng" → "Thêm vào" → tên đăng nhập + mật khẩu tạm → gán **nhóm** (Sales, Procurement, Finance, Legal, Approver, Exporter). Mục "Bắt đổi mật khẩu khi đăng nhập" được tick sẵn.
- **Đặt lại mật khẩu:** đặt mật khẩu mới ở trang người dùng, rồi tick lại "Bắt đổi mật khẩu khi đăng nhập".
- **Mở khoá tài khoản:** xoá giá trị "Khoá đến" ở trang người dùng.
- **Danh sách sales:** menu "Nhân viên kinh doanh". Mỗi sales phụ trách khách hàng cần có **mã sales Sota**, nếu không khách hàng của họ sẽ không xuất được.
- **Ngưỡng chuyển cấp trên:** biến môi trường `ESCALATION_CREDIT_LIMIT_VND` và `ESCALATION_PAYMENT_DAYS`.

### 7. Hướng dẫn kiểm thử

**Tài khoản demo** (chỉ trên môi trường test), mật khẩu `Vnpl@2026demo`:

| Tên đăng nhập | Vai trò |
|---|---|
| `sales1` | Sales |
| `proc1` | Procurement |
| `fin1` | Finance |
| `legal1` | Legal |
| `boss1` | Approver |
| `ops1` | Exporter |
| `admin` | IT admin |

Sales demo: **Nguyễn Văn An** (mã Sota S001) và **Trần Thị Bình** (chưa có mã Sota, dùng để thử trường hợp bị loại khi xuất).

**Kịch bản kiểm thử.** Vui lòng chạy và ghi lại mọi điểm bất thường:

| # | Thao tác | Kết quả mong đợi |
|---|---|---|
| 1 | Nhập sai mật khẩu 5 lần | Tài khoản bị khoá 15 phút |
| 2 | `sales1` tạo khách hàng với MST `12345` và lưu | Bị chặn, báo lỗi tiếng Việt |
| 3 | `sales1` tạo và gửi duyệt khách hàng MST `0101234567`, sales Nguyễn Văn An, hạn mức 100.000.000, thanh toán 30 ngày | Trạng thái "Đang duyệt" |
| 4 | `fin1` duyệt; `legal1` chọn "Yêu cầu chỉnh sửa" kèm nhận xét | Trạng thái "Yêu cầu chỉnh sửa" |
| 5 | `sales1` sửa và gửi lại; `fin1` và `legal1` cùng duyệt | Cả hai phải duyệt lại; trạng thái "Đã duyệt" |
| 6 | `sales1` tạo khách hàng khác trùng MST và gửi duyệt | Cảnh báo trùng; chỉ gửi được khi điền lý do |
| 7 | Gửi duyệt khách hàng hạn mức 1.000.000.000; hai bên duyệt | "Chờ cấp trên duyệt"; `boss1` duyệt → "Đã duyệt" |
| 8 | Cho `sales1` thêm nhóm Finance, rồi thử tự duyệt yêu cầu của mình | Yêu cầu không có trong danh sách; hệ thống từ chối |
| 9 | `ops1` xuất các khách hàng đã duyệt | Tải CSV, mở Excel đúng tiếng Việt; trạng thái "Đã xuất Sota"; có lô trong "Lô xuất Sota" |
| 10 | Duyệt một khách hàng có sales là Trần Thị Bình rồi xuất | Bị loại, lý do "Thiếu: sales_rep_fms_code" |
| 11 | `fin1` đổi sales của một khách hàng đã xuất | Có dấu "Thay đổi sau khi xuất"; hiện lại trong "Sẵn sàng xuất Sota"; ghi trong "Nhật ký" |
| 12 | `proc1` tạo và gửi duyệt NCC nước ngoài (bỏ trống MST, điền số đăng ký nước ngoài) | Được chấp nhận |

**Báo lỗi:** gửi số yêu cầu (REQ-…), tên đăng nhập, thao tác đã làm, kết quả mong đợi và ảnh chụp màn hình.

### 8. Hạn chế đã biết (bản dev)
- Gửi duyệt và xuất file là **hành động trên danh sách** (tick → chọn hành động → "Đi đến"); chưa có nút trên trang yêu cầu.
- Người duyệt bắt đầu từ menu duyệt, chưa có nút "Duyệt" trên trang yêu cầu.
- Cảnh báo khi xuất hiện ở lần tải trang kế tiếp vì trình duyệt đang tải file.
- Mỗi lần duyệt chỉ có một link bằng chứng, chưa tách theo từng mục checklist.
- **Các cột Sota đang là tạm thời** cho đến khi có danh sách trường import thực tế của Sota.
- Chưa có email thông báo; hãy kiểm tra bộ lọc "Chờ tôi duyệt".

---

## Developer notes

### Run locally
```
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed --demo        # roles + demo users (password Vnpl@2026demo)
python manage.py runserver          # http://127.0.0.1:8000
python manage.py test onboarding
```

### Deploy (Render + Neon)
- Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py seed`
- Start: `gunicorn config.wsgi`
- Env: `DATABASE_URL` (Neon), `SECRET_KEY`, `DEBUG=0`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS=https://<host>`,
  optional `ESCALATION_CREDIT_LIMIT_VND`, `ESCALATION_PAYMENT_DAYS`.
- First admin: `python manage.py createsuperuser` in the Render shell. Do **not** run `seed --demo` in production.

### Where things live
- State machine, review rules, export: `onboarding/services.py`
- Sota CSV columns: `onboarding/sota_mapping.py` (placeholder until Sota fields are confirmed)
- Roles/permissions: `onboarding/management/commands/seed.py`
- Login lockout / forced password change: `onboarding/auth.py`
- Requirements: `BRDv3.md`
