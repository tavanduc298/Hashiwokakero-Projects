# Hashiwokakero-Projects

Hashiwokakero, còn được gọi là Bridges hoặc Hashi, là một câu đố logic thách thức người chơi kết nối các đảo được đánh số với một số lượng cầu cụ thể trong khi tuân theo một bộ quy tắc đơn giản. Được xuất bản bởi Nikoli, câu đố này đòi hỏi tư duy chiến lược và lập kế hoạch cẩn thận để đảm bảo tất cả các đảo được kết nối với nhau mà không vượt quá số lượng cầu được phép trên mỗi đảo. Trò chơi đã trở nên phổ biến trên toàn thế giới dưới nhiều tên gọi khác nhau, chẳng hạn như Ai-Ki-Ai ở Pháp, Đan Mạch, Hà Lan và Bỉ. Với thiết kế thanh lịch và chiều sâu logic, Hashiwokakero mang đến một thử thách hấp dẫn cho những người đam mê câu đố ở mọi cấp độ kỹ năng.

tác dụng từng file:

-   data/: Chứa dữ liệu bài toán và kết quả.
        + puzzles/: Chứa các file bài toán Hashiwokakero
        + solutions/: Lưu kết quả đầu ra

-   src/:  Chứa mã nguồn chính
        +cnf_generator.py          Chuyển đổi bài toán thành các ràng buộc CNF
        + sat_solver.py             Giải bài toán bằng thư viện PySAT
        + a_star_solver.py          Giải bài toán bằng thuật toán A*
        + brute_force_solver.py      Giải bài toán bằng brute-force để so sánh
        + backtracking_solver.py     Giải bài toán bằng backtracking để so sánh
        + puzzle_parser.py           Đọc và xử lý file input
        + bridge_validator.py        Kiểm tra điều kiện hợp lệ của cầu
        + hashi_visualizer.py        Vẽ và hiển thị kết quả
        + _init__.py                Để đánh dấu thư mục này là module Python

-   tests/: Chứa các file kiểm thử
        + test_cnf_generator.py      Kiểm thử chuyển đổi CNF
        + test_sat_solver.py         Kiểm thử SAT solver
        + test_a_star_solver.py      Kiểm thử thuật toán A*
        + test_puzzle_parser.py      Kiểm thử đọc dữ liệu đầu vào
        + est_bridge_validator.py   Kiểm thử kiểm tra điều kiện hợp lệ của cầu
        + __init__.py                Để đánh dấu thư mục này là module Python

-   results/: Chứa kết quả benchmark
        + benchmark_results.txt    So sánh tốc độ các thuật toán
        + log.txt                  Lưu log quá trình chạy chương trình

-   docs/: Chứa tài liệu, báo cáo
        + report.pdf                 Báo cáo cuối cùng
        + cnf_rules.md               Mô tả ràng buộc CNF
        + readme.md                  Hướng dẫn sử dụng

-   main.py                        Chương trình chính để chạy solver
-   requirements.txt                Danh sách thư viện cần cài đặt
