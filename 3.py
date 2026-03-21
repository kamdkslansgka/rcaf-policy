import os

# === 配置区 ===
local_base_dir = "./public/videos/real_world"
web_url_prefix = "/rcaf-policy/videos/real_world"

# 任务英文名映射表
TASK_NAMES = {
    "pick_place": "Pick and Place",
    "throwing": "Dynamic Throwing",
    "pouring": "Grasping and Pouring Bottle"
}

def generate_comparison_mdx():
    if not os.path.exists(local_base_dir):
        print(f"找不到文件夹: {local_base_dir}，请检查路径！")
        return

    mdx_code = "## Real-World Generalization Results\n\n"
    mdx_code += "We evaluate the learned policies on physical hardware across dynamic and dexterous manipulation tasks. We compare our **RCAF** against state-of-the-art baselines.\n\n"

    # 获取所有子文件夹
    folders = sorted([d for d in os.listdir(local_base_dir) if os.path.isdir(os.path.join(local_base_dir, d))])

    for folder in folders:
        if folder not in TASK_NAMES:
            continue
            
        task_title = TASK_NAMES[folder]
        folder_path = os.path.join(local_base_dir, folder)
        
        # 获取该文件夹下所有的 mp4 视频
        videos = [v for v in os.listdir(folder_path) if v.endswith('.mp4')]
        if not videos:
            continue
            
        # 自定义排序逻辑：DP排第一，pi0排第二，ours排最后压轴
        def sort_key(v):
            v_lower = v.lower()
            if 'dp' in v_lower: return 0
            if 'pi0' in v_lower: return 1
            if 'ours' in v_lower: return 2
            return 3
        
        videos = sorted(videos, key=sort_key)

        mdx_code += f"### Task: {task_title}\n\n"
        
        # 根据视频数量动态决定网格列数 (2列或3列)
        if len(videos) >= 3:
            grid_class = "grid grid-cols-1 md:grid-cols-3 gap-4"
        else:
            grid_class = "grid grid-cols-1 md:grid-cols-2 gap-4"
            
        mdx_code += f'<div className="{grid_class}">\n'
        
        for video in videos:
            v_lower = video.lower()
            video_url = f"{web_url_prefix}/{folder}/{video}"
            
            # 智能识别视频对应的方法
            title = "Baseline"
            is_ours = False
            
            if 'dp' in v_lower:
                title = "Diffusion Policy (DP)"
            elif 'pi0' in v_lower:
                title = "π₀ (Pi0)"
            elif 'ours' in v_lower:
                title = "RCAF (Ours)"
                is_ours = True
            
            # 生成渲染代码（无需 TwoColumns，直接用原生 Grid 完美排版）
            mdx_code += '  <div className="flex flex-col">\n'
            if is_ours:
                mdx_code += f'    <h4 className="text-center font-bold text-blue-600 mb-2">{title}</h4>\n'
                mdx_code += f'    <video src="{video_url}" autoPlay loop muted playsInline className="w-full rounded-lg shadow-lg border-2 border-blue-200" />\n'
            else:
                mdx_code += f'    <h4 className="text-center font-semibold text-gray-700 mb-2">{title}</h4>\n'
                mdx_code += f'    <video src="{video_url}" autoPlay loop muted playsInline className="w-full rounded-lg shadow-sm border border-gray-200" />\n'
            mdx_code += '  </div>\n'
            
        mdx_code += "</div>\n\n<br/>\n\n"

    with open("generated_realworld_compare.txt", "w", encoding="utf-8") as f:
        f.write(mdx_code)
    
    print("✅ 智能真机对比代码已生成！支持 2列 和 3列 混排。")

if __name__ == "__main__":
    generate_comparison_mdx()