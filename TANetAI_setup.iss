; Script tạo bộ cài đặt TANetAI - Gateway Monitor
; Phiên bản: 16.2
; Tác giả: Tấn Lai Hoàng

[Setup]
; --- THÔNG TIN ỨNG DỤNG ---
AppName=TANetAI
AppVersion=16.2
AppPublisher=Tấn Lai Hoàng
AppContact=tanlaihoang.work@gmail.com
AppPublisherURL=https://github.com/TanyanArchitect
AppSupportURL=https://github.com/TanyanArchitect

; --- CẤU HÌNH ĐẦU RA ---
; Tên file Setup sẽ được tạo ra (Ví dụ: TANetAI-v16.2-Setup.exe)
OutputBaseFilename=TANetAI-v16.2-Setup
; Thư mục chứa file setup (sẽ tự tạo nếu chưa có)
OutputDir=.\InstallerOutput

; --- CẤU HÌNH CÀI ĐẶT ---
; Thư mục cài đặt mặc định trên máy người dùng (C:\Program Files (x86)\TANetAI)
DefaultDirName={autopf}\TANetAI
; Nhóm trong Start Menu
DefaultGroupName=TANetAI
; Yêu cầu quyền Admin để cài đặt (Bắt buộc để cài Npcap và chạy Scapy)
PrivilegesRequired=admin

; --- TÙY CHỌN NÉN ---
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
; Sử dụng tiếng Anh chuẩn để tránh lỗi font trên các máy không có locale Việt Nam
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; 1. File chương trình chính (Lấy từ thư mục dist sau khi build PyInstaller)
Source: "dist\TANetAI.exe"; DestDir: "{app}"; Flags: ignoreversion

; 2. File cấu hình (Để người dùng có thể Reset hoặc chỉnh tay nếu muốn)
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion

; 3. Trình cài đặt Npcap (File tạm để chạy khi cài đặt, sẽ xóa sau khi xong)
; LƯU Ý: Bạn phải tải file npcap-1.84.exe và để cùng thư mục với file .iss này
Source: "npcap-1.84.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
; Tạo shortcut trong Start Menu
Name: "{group}\TANetAI"; Filename: "{app}\TANetAI.exe"
Name: "{group}\Gỡ cài đặt TANetAI"; Filename: "{uninstallexe}"

; Tạo shortcut ngoài Desktop
Name: "{autodesktop}\TANetAI"; Filename: "{app}\TANetAI.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Tạo biểu tượng ngoài màn hình (Desktop)"; GroupDescription: "Tùy chọn:";

[Run]
; 1. Chạy cài đặt Npcap
; Lưu ý: Bản Npcap miễn phí không hỗ trợ cờ /S (Silent), nên cửa sổ cài đặt sẽ hiện lên.
; /winpcap_mode=yes: Bắt buộc để Scapy hoạt động tốt trên Windows.
Filename: "{tmp}\npcap-1.84.exe"; Parameters: "/winpcap_mode=yes"; StatusMsg: "Đang khởi chạy trình cài đặt Npcap (Vui lòng nhấn Install để tiếp tục)..."; Flags: waituntilterminated

; 2. Chạy chương trình sau khi cài đặt xong (Tùy chọn cho người dùng)
Filename: "{app}\TANetAI.exe"; Description: "Khởi chạy TANetAI ngay bây giờ"; Flags: nowait postinstall shellexec