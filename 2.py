import os

# === 配置区 ===
# 指向你的 robotwin2 文件夹
local_base_dir = "./public/videos/robotwin2"
web_url_prefix = "/rcaf-policy/videos/robotwin2"

def generate_video_grid():
    if not os.path.exists(local_base_dir):
        print(f"找不到文件夹: {local_base_dir}，请检查路径！")
        return

    mdx_code = "## RoboTwin 2.0 Benchmark Demonstrations\n\n"
    
    # 【核心改变】：只开一个贯穿全局的大网格！电脑端一行4个，手机一行2个
    mdx_code += '<div className="grid grid-cols-2 md:grid-cols-4 gap-4">\n'

    # 获取所有子文件夹并排序
    subfolders = sorted([d for d in os.listdir(local_base_dir) if os.path.isdir(os.path.join(local_base_dir, d))])

    for folder in subfolders:
        folder_path = os.path.join(local_base_dir, folder)
        videos = sorted([v for v in os.listdir(folder_path) if v.endswith('.mp4')])
        
        for video in videos:
            video_url = f"{web_url_prefix}/{folder}/{video}"
            
            # 把文件夹名字（如 click_bell）变成好看的标题（如 Click Bell）
            task_name = folder.replace("_", " ").title()
            
            # 排版：干脆利落的视频 + 底部一行极简的任务名称
            mdx_code += "  <figure>\n"
            mdx_code += f'    <video src="{video_url}" autoPlay loop muted playsInline className="w-full rounded-lg shadow-sm border border-gray-100" />\n'
            mdx_code += f'    <figcaption className="text-center text-sm mt-2 text-gray-700 font-medium">{task_name}</figcaption>\n'
            mdx_code += "  </figure>\n"

    mdx_code += "</div>\n\n"

    with open("generated_robotwin2_code.txt", "w", encoding="utf-8") as f:
        f.write(mdx_code)
    
    print("✅ RoboTwin2.0 代码已成功生成！快去看看 txt 文件吧。")

if __name__ == "__main__":
    generate_video_grid()