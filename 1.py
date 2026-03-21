import os

# === 配置区 ===
# 你的视频存放的本地基础路径
local_base_dir = "./public/videos/robotwin"
# 网页访问时的前缀路径（必须带上你的 base 配置）
web_url_prefix = "/rcaf-policy/videos/robotwin"

def generate_video_grid():
    if not os.path.exists(local_base_dir):
        print(f"找不到文件夹: {local_base_dir}，请检查路径是否正确！")
        return

    mdx_code = "## Simulation Results (RoboTwin)\n\n"

    # 获取所有子文件夹并排序
    subfolders = sorted([d for d in os.listdir(local_base_dir) if os.path.isdir(os.path.join(local_base_dir, d))])

    for folder in subfolders:
        # 为每个子任务生成一个小标题（首字母大写）
        mdx_code += f"### Task: {folder.capitalize()}\n\n"
        mdx_code += '<div className="grid grid-cols-2 md:grid-cols-3 gap-4">\n'
        
        folder_path = os.path.join(local_base_dir, folder)
        # 获取该文件夹下所有的 mp4 文件并排序
        videos = sorted([v for v in os.listdir(folder_path) if v.endswith('.mp4')])
        
        for video in videos:
            video_url = f"{web_url_prefix}/{folder}/{video}"
            
            # 直接生成干净的 video 标签，去掉所有的文字和 figure 包装
            mdx_code += f'  <video src="{video_url}" autoPlay loop muted playsInline className="w-full rounded-lg shadow-sm" />\n'
            
        mdx_code += "</div>\n\n<br/>\n\n"

    with open("generated_video_code.txt", "w", encoding="utf-8") as f:
        f.write(mdx_code)
    
    print("✅ MDX 代码已成功生成！所有的视频名字已经去掉啦。")

if __name__ == "__main__":
    generate_video_grid()