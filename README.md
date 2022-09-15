# API_ERN_BLife

# Mục Lục
1. [Cài đặt](#setup)
2. [Thiết lập tham số](#thiết-lập-tham-số)
    - [Mô hình dự đoán](#mô-hình-dự-đoán)
    - [Luồng dữ liệu vào](#luồng-dữ-liệu-vào)
    - [Luồng dữ liệu ra](#luồng-dữ-liệu-ra)
    - [Các tham số khác](#các-tham-số-khác)
3. [Khởi chạy chương trình](#khởi-chạy-chương-trình)
# Cài đặt <a name = setup></a>
## Cài thư viện
Các thư viện cần thiết được mô tả trong file **requirements.txt**. Để cài đặt sử dụng câu lệnh:

    pip install -r requirements.txt

# Thiết lập tham số 
## Mô hình dự đoán 
Các thông số của mô hình dự đoán được thiết lập tại class **ModelSetting()**. Các thông số này bao gồm:

- **name**: tên mô hình  
- **path**: đường dẫn của file mô hình dự đoán
- **channels**: danh sách các kênh được sử dụng để dự đoán
- **sfreq**: tần số lấy mẫu của dữ liệu đưa vào mô hình
- **t_min**: thời điển bắt đầu của dữ liệu so với hành động. Đơn vị là giây.
- **t_max**: thời điểm bắt dầu của dữ liệu so với hành động. Đơn vị là giây.
- **l_freq**: lọc thông thấp
- **h_freq**: lọc thông cao
- **shape**: cặp thông số về kích thước dữ liệu đầu vào của mô hình và số dữ liệu sử dụng trên mỗi kênh. Ví dụ ((1,56), 28) thì (1,56) là kích thước đầu vào của mô hình, 28 là số điểm dữ liệu lấy trên 1 kênh

Khi muốn thay đổi mô hình dự đoán thì cần phải cập nhật file mô hình và các thông số tương ứng của mô hình mới

## Luồng dữ liệu vào
Luồng dữ liệu vào là các [Lab Streaming Layer (LSL)](https://github.com/sccn/labstreaminglayer) được thiết lập trong file api_inlet.py. Các thông số của luồng này bao gồm:
- **host**: địa chỉ api được khởi chạy
- **ET_stream_name**: tên của luồng dữ liệu gửi từ phần mềm blife

## Luồng dữ liệu ra
Luồng dữ liệu ra cũng là 1 LSL. Các thông số của luồng dữ liệu ra sẽ được thiết lập tại class **Outlet()**. Các thông số được thiết lập bao gồm:
- **name**: tên của luồng dữ liệu ra
- **n_channels**: số lượng kênh của dữ liệu ra
- **data_type**: loại dữ liệu ra (nên để là Maker)
- **sfreq**: tần số đưa tín hiệu ra
- **source_id**: tên nguồn đưa tín hiệu ra
- **outlet**: luồng tín hiệu ra (không sửa)
- **channel_name**: tên các kênh của dữ liệu ra

Mặc định dữ liệu ra sẽ có dạng **[[điểm dữ liệu], thời gian tương ứng]**. Nếu không cung cấp chuỗi thời gian thì sẽ tự động lấy thời gian của hệ thống. Để gửi thời gian mong muốn thì thêm vào nó vào tham số **timesample** khi gọi hàm **send_sample()**



## Các tham số khác
Thông số chung sẽ được thiết lập tại class **Setting()** trong file **config.py**. Các thông số này bao gồm:
- **RAW_SAMPLING_RATE**:  tần số lấy mẫu của tín hiệu điện não 
- **BUFFER_TIME**: độ dài đoạn tín hiệu điện não được lưu trữ liên tục. Đơn vị là giây.
- **use_ica**: có sử dụng ica hay không.
- **PREDICT_COUNT**: số lần dự đoán sau khi bấm phím

***Lưu ý***: thời gian thực hiện ica khoảng 0.8s/1s dữ liệu

# Khởi chạy chương trình

Khởi chạy API bằng câu lệnh:

    uvicon main:app --host x.x.x.x -- port y

với x.x.x.x là địa chỉ host và y là port khởi chạy API. Địa chỉ mặc định là 127.0.0.1:8000

Khởi chạy nhận luồng dữ liệu và đưa vào API:

    python api-inlet.py







