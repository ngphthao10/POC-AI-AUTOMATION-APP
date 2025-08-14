#!/usr/bin/env python3
"""
Ứng dụng Tự động hóa AI
Ứng dụng tự động hóa dựa trên console với nhiều tiện ích khác nhau
"""

import sys
import os
import json
from pathlib import Path

def get_application_path():
    """Lấy thư mục nơi ứng dụng đang chạy"""
    if getattr(sys, 'frozen', False):
        # Chạy như PyInstaller bundle
        application_path = os.path.dirname(sys.executable)
    else:
        # Chạy như script
        application_path = os.path.dirname(os.path.abspath(__file__))
    return application_path

def get_input_file_path():
    """Lấy đường dẫn đến file input.json"""
    app_path = get_application_path()
    return os.path.join(app_path, "input.json")

def clear_screen():
    """Xóa màn hình console"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """In header của ứng dụng"""
    print("=" * 60)
    print("    🐍 ỨNG DỤNG TỰ ĐỘNG HÓA AI 🐍")
    print("    Tiện ích dựa trên Console")
    print("=" * 60)
    print()

def print_menu():
    """In menu chính"""
    print("📋 MENU CHÍNH:")
    print("1. CSP Admin - Thay đổi vai trò và chi nhánh")
    print("6. Thoát")
    print("-" * 40)

def csp_admin_change_role_and_branch():
    """Chức năng CSP Admin - Thay đổi vai trò và chi nhánh"""
    print("\n🏢 CSP ADMIN - THAY ĐỔI VAI TRÒ VÀ CHI NHÁNH")
    print("=" * 45)
    print("Tự động hóa thay đổi vai trò và chi nhánh người dùng CSP")
    
    input_file_path = get_input_file_path()
    print(f"📂 File đầu vào: {input_file_path}")
    
    while True:
        print("\n📋 Menu CSP Admin:")
        print("1. 🚀 Chạy tự động hóa CSP")
        print("2. 📄 Xem file đầu vào")
        print("3. 📝 Xem định dạng mẫu")
        print("4. ← Quay lại menu chính")
        
        choice = input("\nChọn tùy chọn (1-4): ").strip()
        
        if choice == '1':
            demo_automation_run()
        elif choice == '2':
            show_current_input_file()
        elif choice == '3':
            show_sample_input_format()
        elif choice == '4':
            break
        else:
            print("❌ Lựa chọn không hợp lệ! Vui lòng thử lại.")
            input("Nhấn Enter để tiếp tục...")

def show_sample_input_format():
    """Hiển thị định dạng đầu vào mẫu cho tự động hóa CSP"""
    print("\n📄 ĐỊNH DẠNG ĐẦU VÀO MẪU")
    print("-" * 30)
    sample = '''{
  "admin_credentials": {
    "username": "admin_username",
    "password": "admin_password",
    "csp_admin_url": "https://csp-portal.com/portal/users/list"
  },
  "users": [
    {
      "target_user": "user1@example.com",
      "new_role": "CSP-RB-TELLER",
      "branch_hierarchy": ["VIB Bank", "North", "002"]
    },
    {
      "target_user": "user2@example.com", 
      "new_role": "CSP_Inquiry",
      "branch_hierarchy": ["VIB Bank", "North", "003"]
    }
  ]
}'''
    print(sample)
    input("\nNhấn Enter để tiếp tục...")

def show_current_input_file():
    """Hiển thị nội dung file đầu vào hiện tại"""
    try:
        input_path = get_input_file_path()
        if os.path.exists(input_path):
            print(f"\n📄 FILE ĐẦU VÀO: {input_path}")
            print("-" * 40)
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content)
        else:
            print(f"\n❌ Không tìm thấy file: {input_path}")
            print("💡 Đặt input.json cùng thư mục với file thực thi")
    except Exception as e:
        print(f"\n❌ Lỗi đọc file: {e}")
    input("\nNhấn Enter để tiếp tục...")

def demo_automation_run():
    """Chạy tự động hóa CSP thực tế"""
    print("\n🚀 TỰ ĐỘNG HÓA CSP ADMIN")
    print("-" * 35)
    
    # Kiểm tra file đầu vào
    input_path = get_input_file_path()
    if not os.path.exists(input_path):
        print(f"❌ Không tìm thấy file: {input_path}")
        print("� Đặt input.json cùng thư mục với file thực thi")
        input("\nNhấn Enter để tiếp tục...")
        return
    
    try:
        # Tải và xác thực file đầu vào
        with open(input_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        users = config_data.get('users', [])
        admin_user = config_data.get('admin_credentials', {}).get('username', 'Không xác định')
        
        print(f"✅ Tải thành công: {len(users)} người dùng")
        print(f"👤 Admin: {admin_user}")
        
        # Hiển thị danh sách người dùng ngắn gọn
        if users:
            print(f"\n👥 Danh sách xử lý:")
            for i, user in enumerate(users, 1):
                target_user = user.get('target_user', 'Không rõ')
                new_role = user.get('new_role') or 'Không đổi'
                
                # Lấy thông tin chi nhánh (chỉ lấy mã chi nhánh cuối cùng)
                branch_hierarchy = user.get('branch_hierarchy', [])
                branch_code = branch_hierarchy[-1] if branch_hierarchy else 'Không rõ'
                
                print(f"   {i}. {target_user} | Chi nhánh: {branch_code} | Vai trò: {new_role}")
        
        # Xác nhận
        print(f"\n⚠️  Sẽ thực hiện tự động hóa trình duyệt thực tế")
        confirm = input("Tiếp tục? (y/N): ").strip().lower()
        
        if confirm in ['y', 'yes', 'c', 'có']:
            print("\n🔄 Bắt đầu tự động hóa...")
            run_actual_csp_automation(input_path)
        else:
            print("❌ Đã hủy tự động hóa")
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON không hợp lệ: {e}")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    
    input("\nNhấn Enter để tiếp tục...")

def run_actual_csp_automation(input_file: str):
    """Chạy tự động hóa CSP thực tế"""
    try:
        try:
            from src.csp.csp_admin_change_role_and_branch import CSPAdminRoleAndBranchChanger
            from src.config.nova_act_config import get_nova_act_api_key
        except ImportError as e:
            print(f"❌ Không thể import: {e}")
            print("Cài đặt: pip install nova-act fire pydantic")
            return
        
        # Get Nova Act API key
        try:
            api_key = get_nova_act_api_key()
            print("✅ Đã tải Nova Act API key")
        except Exception as e:
            print(f"❌ Lỗi Nova Act API key: {e}")
            print("💡 Vui lòng cấu hình API key trong src/config/nova_act_config.py")
            return
        
        changer = CSPAdminRoleAndBranchChanger("", api_key)
        
        # Cấu hình worker
        parallel_workers = 2
        try:
            workers_input = input("Số worker song song (1-4, mặc định=2): ").strip()
            if workers_input:
                parallel_workers = max(1, min(4, int(workers_input)))
        except ValueError:
            parallel_workers = 2
        
        print(f"🔧 Worker: {parallel_workers}")
        print("=" * 40)
        
        # Chạy tự động hóa
        success = changer.run_batch(
            input_file=input_file,
            per_user_session=True,
            parallel_workers=parallel_workers if parallel_workers > 1 else None
        )
        
        print("=" * 40)
        if success:
            print("✅ Hoàn thành thành công!")
        else:
            print("⚠️  Hoàn thành với lỗi")
        print("📄 Kết quả lưu trong file JSON")
            
    except KeyboardInterrupt:
        print("\n⚠️  Bị gián đoạn")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")

def main():
    """Hàm chính"""
    try:
        while True:
            clear_screen()
            print_header()
            print_menu()
            
            choice = input("Chọn một tùy chọn (1-6): ").strip()
            
            if choice == '1':
                csp_admin_change_role_and_branch()
            elif choice == '6':
                print("\n👋 Tạm biệt! Cảm ơn bạn đã sử dụng ứng dụng!")
                break
            else:
                print("\n❌ Lựa chọn không hợp lệ! Vui lòng thử lại.")
                input("Nhấn Enter để tiếp tục...")
                
    except KeyboardInterrupt:
        print("\n\n👋 Tạm biệt! Cảm ơn bạn đã sử dụng ứng dụng!")
    except Exception as e:
        print(f"\n❌ Đã xảy ra lỗi: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
