import torch
print("開始檢查..")
print(f"PyTorch 版本: {torch.__version__}")
print(f"CUDA 是否可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print("GPU數量：",torch.cuda.device_count())
    print(f"CUDA 裝置數量: {torch.cuda.device_count()}")
    print(f"當前 CUDA 裝置名稱: {torch.cuda.get_device_name(0)}")
    print("cudnn是否可用：",torch.backends.cudnn.enabled)
    print("cudnn 版本：", torch.backends.cudnn.version())
    print("記憶體狀態：",torch.cuda.mem_get_info())
else:
    print("PyTorch 未偵測到 CUDA 裝置。")
    print("cuda是否可用：",torch.cuda.is_available())