import pandas as pd
import re

# 读取Excel文件
df = pd.read_excel('movie_info_整理版.xlsx')
print(df.columns)

# # 1. 去掉title2列最前面的"/"
# if 'title2' in df.columns:
#     df['title2'] = df['title2'].astype(str).str.lstrip('/ ').str.strip()

# # 2. 提取bd列信息
# def extract_movie_info(bd):
#     result = {
#         '导演': '',
#         '主演': '',
#         '年份': '',
#         '国家': '',
#         '类型': '',
#         '片长': ''
#     }
#     try:
#         director_match = re.search(r'导演: (.*?)(?=\s*主演:|$)', bd)
#         if director_match:
#             result['导演'] = director_match.group(1).strip()
#         actors_match = re.search(r'主演: (.*?)(?=\s*\d{4}|$)', bd)
#         if actors_match:
#             result['主演'] = actors_match.group(1).strip()
#         year_match = re.search(r'(\d{4})', bd)
#         if year_match:
#             result['年份'] = year_match.group(1)
#         country_match = re.search(r'/([^/]+?)(?=\s*/\s*[^/]+?$)', bd)
#         if country_match:
#             result['国家'] = country_match.group(1).strip()
#         type_match = re.search(r'/([^/]+?)$', bd)
#         if type_match:
#             result['类型'] = type_match.group(1).strip()
#         duration_match = re.search(r'(\d+)分钟', bd)
#         if duration_match:
#             result['片长'] = duration_match.group(1) + '分钟'
#     except Exception as e:
#         print(f"处理数据时出错: {e}")
#     return result

# movie_info_df = pd.DataFrame([extract_movie_info(bd) for bd in df['bd']])

# # 3. 合并新信息
# df = pd.concat([df, movie_info_df], axis=1)

# # 4. 列名中英文对照（请根据实际英文列名补充/修改）
# col_map = {
#     'pic href': '电影详情链接',
#     'pic src': '图片链接',
#     'title': '影片中文名',
#     'rating_num': '评分',
#     'inq': '概况',
#     'bd 2': '评价人数',
#     'quote': '简介'
# }
# df = df.rename(columns=col_map)

# # 5. 保存到新文件
# df.to_excel('movie_info_整理版.xlsx', index=False)
# print("已保存到 movie_info_整理版.xlsx")

