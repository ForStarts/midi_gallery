# coding=utf-8

# @Date    : 2024-5-19
# @Author  : Chen Jin,Liu Huazhen

import streamlit as st
import csv
import pandas as pd
import math
import pretty_midi
import mido
import tempfile
# 存储静态数据变量的文件
import datastore
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 页面宽度拓宽
st.set_page_config(layout='wide',page_title='MIDI音乐馆',page_icon='🎧')

import base64
def main_bg(main_bg):
    main_bg_ext = "png"
    st.markdown(
        f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover
         }}
         </style>
         """,
        unsafe_allow_html=True
    )

# 调用
main_bg("back-picture1.jpg")

# 网页基础样式
st.markdown(
    '''
        <style>
            .stApp {
                min-width: 1600px;
            }
            div.st-emotion-cache-ocqkz7 div {
                /* margin: auto; */
            }
        </style>
    ''',
    unsafe_allow_html=True
)

# 头部说明文字
with st.container():
    title_col1,title_col2,title_col3=st.columns([0.5,0.3,0.2])
    with title_col1:
        st.title(':red[_MIDI_]:blue[,一种轻量化音乐格式]')
    with title_col3:
        WEBMASTER_KEY = 'mykey'
        master_password = st.text_input(label='管理员密码：',
                                        type='password',
                                        label_visibility='hidden')

# st.cache_data()的缓存方法：持续存储可序列化类型数据对象，它会在运行被@st.cache_data包裹的
# 函数之后持续的存储返回的数据结果，当你每次再次执行该函数时，它会在缓存中查询后立即返回结果，
# 而不是重新运行。
csv_filename = '新乐曲结果.csv'
@st.cache_data
def data_create(csv_filename):
    # 定义CSV文件的名称
    # 初始化空列表来存储每列的数据
    composer = []
    song_id = []
    link = []
    song_copyright = []
    # 初始化id列表
    id = []
    # 使用csv模块读取CSV文件
    with open(csv_filename, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        # 跳过第一行（列名）
        next(csv_reader)
        # 初始化计数器
        counter = 0
        # 遍历CSV文件中的每一行
        for row in csv_reader:
            # 将计数器的当前值添加到id列表中
            id.append(counter)
            # 将每列的数据添加到对应的列表中
            composer.append(row[0])
            song_id.append(row[1])
            link.append(row[2])
            song_copyright.append(row[3])
            # 更新计数器
            counter += 1

    # 将提取的数据存储在字典中
    data = {
        'id': id,
        'composer': composer,
        'song_id': song_id,
        'link': link,
        'song_copyright': song_copyright
    }
    data = pd.DataFrame(data=data)
    data.index = data['id']
    return data

# 推荐板块文件读取
def recommend_read(csv_filename):
    composer = []
    song_id = []
    link = []
    song_copyright = []
    # 初始化id列表
    id = []
    # 使用csv模块读取CSV文件
    with open(csv_filename, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        # 跳过第一行（列名）
        next(csv_reader)
        # 初始化计数器
        counter = 0
        # 遍历CSV文件中的每一行
        for row in csv_reader:
            # 这里读取文件里面的id文字符串形式，转换成字符形式
            id.append(int(row[0]))
            composer.append(row[1])
            song_id.append(row[2])
            link.append(row[3])
            song_copyright.append(row[4])
    # 将提取的数据存储在字典中
    data = {
        'id': id,
        'composer': composer,
        'song_id': song_id,
        'link': link,
        'song_copyright': song_copyright,
    }
    data = pd.DataFrame(data=data)
    data.index = data['id']
    return data

#中间部分页面（主要内容）
# 搜索框(两列）
with st.container():
    search_box = st.columns(2, gap='small')
    with search_box[0]:
        author_input = st.text_input(":violet[**搜索-作者名称：**]")
    with search_box[1]:
        song_code_input = st.text_input(":violet[**搜索-乐曲编码：**]")
#推荐和主要切换tabs
with st.container():
    recommend,mainpage=st.columns([2.5,7.5],gap='large')
    with recommend:
        if 'csv_data' not in st.session_state:
            # 此处返回的表格数据被缓存
            st.session_state['csv_data'] = data_create('新乐曲结果.csv')
        if 'com_data' not in st.session_state:
            st.session_state['com_data'] = recommend_read('recommend.csv')

        def add_music_to_com_data(music_id):
            # 检查指定ID是否存在于csv_data中
            if music_id in st.session_state.csv_data.index:
                # 获取指定ID的乐曲信息
                music_info = st.session_state.csv_data.loc[[music_id]]
                # 将乐曲信息添加到com_data中，忽略索引重复的问题
                if music_id in st.session_state.com_data.index:
                    st.error('歌曲已存在')
                # if 'com_data' not in st.session_state:
                #     st.session_state.com_data = music_info
                else:
                    st.session_state.com_data = pd.concat(
                        [st.session_state.com_data, music_info],
                        ignore_index=False)
                    st.session_state.com_data.to_csv('recommend.csv',
                                                     index=False,
                                                     encoding='utf-8')
                    st.success('成功添加')
            else:
                st.error('添加失败')


        def delete_music_from_com_data(music_id):
            # 检查指定ID是否存在于com_data中
            if 'com_data' in st.session_state and music_id in st.session_state.com_data.index:
                # 从com_data中删除指定ID的行
                st.session_state.com_data = st.session_state.com_data.drop(
                    music_id)
                st.session_state.com_data.to_csv('recommend.csv', index=False,
                                                 encoding='utf-8')
                st.success('成功删除')
            else:
                st.error('删除失败')

        recommend_now_data1 = st.session_state.com_data.to_dict(orient='records')

        # 下面内容之后替换成推荐板块内容
        with st.expander("**推荐板块**",expanded=True):
            for dt in recommend_now_data1:  # 存储当前展示页的音乐信息字典列表
                # 创建一个两列的布局，但我们只使用第一列。以后第二列可以添加一个emojy图。
                col1, col2 = st.columns([10, 1])
                with col1:
                    href = f'<a href="{dt["link"]}" download="{dt["id"]}.mid" target="_blank">:rainbow[{dt["song_id"]}]</a>'
                    st.markdown(href, unsafe_allow_html=True)

    with mainpage:
        #* 分出多个tab，按照：midi搜索、midi分析、midi学习指导 的顺序。
        #** midi搜索
        #*** 数据初始化
        tab1,tab2,tab3 = st.tabs([':rainbow[搜索乐曲表格]',':rainbow[midi乐曲分析]',':rainbow[midi学习指导]'])
        with tab1:
            # 在session_state中创建一个data数据集
            if 'csv_data' not in st.session_state:
                # 此处返回的表格数据被缓存
                st.session_state['csv_data'] = data_create()

            #*** 搜索内容判断。三种判断方式代表三种搜索方式，作者搜索、乐曲编码搜索和两者同时搜索
            def GetSearchContents(author_input,song_code_input):
                if author_input and song_code_input:
                    # 应用两个搜索条件进行筛选。
                    # 注意：这里假设你想找到同时包含这两个字符串的行，使用 str.contains
                    # 和 & 操作符。
                    # data_new存储搜索筛选后的数据。
                    st.session_state['data_new'] = st.session_state.csv_data.loc[
                        # pandas.Serial.str.contains()能匹配列表中的每个字符串到提供
                        # 的字符串中，并返回一个布尔值Serial。
                        # case=False 表示搜索时不区分大小写，na=False 表示忽略 NaN 值。
                        (st.session_state.csv_data['composer'].str.contains(
                                            author_input, case=False, na=False))
                        & (st.session_state.csv_data['song_id'].str.contains(
                                        song_code_input, case=False, na=False))]
                elif author_input:
                    st.session_state['data_new'] = st.session_state.csv_data.loc[
                            st.session_state.csv_data['composer'].str.contains(
                                            author_input, case=False, na=False)]
                elif song_code_input:
                    st.session_state['data_new'] = st.session_state.csv_data.loc[
                            st.session_state.csv_data['song_id'].str.contains(
                                        song_code_input, case=False, na=False)]
                else:
                    st.session_state['data_new'] = st.session_state.csv_data
                return st.session_state['data_new']

            search_csv_data = GetSearchContents(author_input,song_code_input)

            #*** 分列呈现
            col1_head, col2_head, col3_head, col4_head, col5_head = st.columns(
                [2 ,1 ,1 ,1.5 ,1.5])

            #**** 构建分页管理
            # 检查st.session_state字典中是否有一个名为'page'的键。如果'page'不存在，
            # 说明这是用户第一次访问或者某种情况下'page'被删除了，因此我们需要初始化它。
            if 'page' not in st.session_state:
                # 表示每页默认显示10条数据
                st.session_state['select_row'] = 8
                # 默认显示第一页
                st.session_state['page'] = 1
            page_num = st.session_state['page']
            limit_num = st.session_state['select_row']
            max_page = math.ceil(len(search_csv_data) / limit_num)

            def page_update(value):
                '''翻页回调（用于表格页面切换内容）
                :param value:
                :return:

                '''
                if value == 1:
                    st.session_state.page += 1
                elif value == 0:
                    st.session_state.page -= 1
                elif value == 2:
                    st.session_state.page = 0

            with col1_head:
                # 当前页
                st.subheader(f"当前页：{page_num}/{max_page}")

            with col4_head:
                # 切换上一页
                st.button(label='上一页', key='lastpage', on_click=page_update,
                          kwargs={'value': 0},disabled=True if page_num <= 1 else False,
                          use_container_width=True)
            with col5_head:
                # 切换下一页
                st.button(label='下一页', key='nextpage', on_click=page_update,
                          kwargs={'value': 1},disabled=True if page_num >= max_page else False,
                          use_container_width=True)

            #**** 分页数据获取
            # 从data这个DataFrame中取出当前页展示页的数据并并赋值给data_page
            data_page = search_csv_data[(int(page_num) - 1) * int(limit_num)
                                        : (int(page_num)* int(limit_num))]
            now_data = data_page.to_dict(orient='records')  # df 转 dict

            #*** 呈现类数据表
            with st.container(border=True):
                def ShowTab1():
                    #表头
                    csv_col1, csv_col2, csv_col3, csv_col4, csv_col5 = st.columns(
                        [1, 1, 1, 1, 1], gap='small')
                    csv_col1.markdown('**作曲家**')
                    csv_col2.markdown('**乐曲编码**')
                    csv_col3.markdown('**版权**')
                    csv_col4.markdown('**下载**')
                    csv_col5.markdown('**音乐索引**')
                    #数据表内容
                    for dt in now_data: #存储当前展示页的音乐信息字典列表
                        col1,col2,col3,col4,col5=st.columns(
                            [1,1,1,1,1],gap='small')
                        col1.write(dt['composer'])
                        col2.write(dt['song_id'])
                        col3.write(dt['song_copyright'])
                        with col4:
                            href = f'<a href="{dt["link"]}" download="{dt["song_id"]}.mid" target="_blank">下载</a>'
                            st.markdown(href, unsafe_allow_html=True)
                        col5.write(dt['id'])

                ShowTab1()

        #*** midi分析页面
        with tab2:
            #先写好核心的显示代码和分析midi的函数，后面再优化
            #功能实现顺序：上传、获取、分析、显示、异常处理。
            def UploadMidi():
                """用户上传文件，我们通过streamlit的file_uploader组件获取用户上传的文件字节流，
                用tempfile创建临时文件,并返回文件路径
                :return: 文件路径

                """
                uploaded_file=st.file_uploader('#### 📤 上传midi文件',
                                               type=['mid'])
                tmp_file=None
                if uploaded_file is not None:
                    file_bytes = uploaded_file.getvalue()
                    with tempfile.NamedTemporaryFile(suffix='.mid', delete=False)\
                            as tmp_file:
                        tmp_file.write(file_bytes)
                        tmp_file.close()  # 必须关闭文件才能确保所有数据都被写入
                    return tmp_file.name    #实际返回的是临时文件的路径

            def AnalyseMidi(upload_file):
                """
                使用mido库和pretty_midi库分析midi文件。获取音乐信息并返回。包括：所有用到
                的音色（乐器）；节拍，时长，BPM，PPQN；以及每个音轨的乐器中英文名称，编号，
                音符数量，音轨时长。第一个赋值是缺省值，可用于异常处理。
                :param upload_file:
                :return:
                """
                mid1=pretty_midi.PrettyMIDI(upload_file)
                mid2=mido.MidiFile(upload_file)

                #获取音色（乐器）信息
                instruments_infos=[]
                for intrument in mid1.instruments:
                    instruments_infos.append(
                        f"{datastore.program_to_name[intrument.program][1]}-{datastore.program_to_name[intrument.program][0]}")

                #获取节拍
                time_signature = ""
                for msg in mid2:
                    if msg.type == 'time_signature':
                        time_signature = f"{msg.numerator}/{msg.denominator}"
                        break  # 如果找到，则退出循环，防止出错

                #获取音乐总时长
                total_time_string=""
                total_time = mid1.get_end_time()
                if total_time < 60:
                    total_time_string=f"{total_time}s"
                else:
                    total_time_string = f"{int(total_time // 60)}m{int(total_time % 60)}s"

                #获取BPM
                bpm=0
                for msg in mid2.tracks[0]:
                    if msg.type == 'set_tempo':
                        # 这样可以只取第一个设置的tempo获得bpm值
                        bpm = int(mido.tempo2bpm(msg.tempo))
                        break

                #获取PPQN(pulses per quarter note)
                ppgn=0
                file_bytes=b''
                with open(upload_file, 'rb') as f:
                    file_bytes=f.read()
                file_hex=file_bytes.hex()
                ppgn_info_hex=file_hex[24:28]
                ppgn=int(ppgn_info_hex,16)

                #获取音轨信息
                #音轨信息包括：乐器名称（中文），乐器名称（英语），乐器ID，音符数量，音轨时长
                track_infos=[]
                for track in mid1.instruments:
                    track_time=track.get_end_time()
                    if track_time < 60:
                        track_time_string=f"{track_time}s"
                    else:
                        track_time_string = f"{int(track_time // 60)}m{int(track_time % 60)}s"
                    track_infos.append(
                        [datastore.program_to_name[track.program][1],
                         datastore.program_to_name[track.program][0],
                         track.program, len(track.notes), track_time_string])

                return [instruments_infos, time_signature, total_time_string,
                        bpm, ppgn, track_infos]

            def ShowMidiInfo(instruments_infos, time_signature,
                             total_time_string, bpm, ppgn, track_infos):
                '''
                展示midi信息
                :param instruments_infos:
                :param time_signature:
                :param total_time_string:
                :param bpm:
                :param ppgn:
                :param track_infos:
                :return:
                '''
                #展示音色信息
                st.markdown("#### 🎹 音色信息")
                instruments_infos_string=""
                for instrument_info in instruments_infos:
                    instruments_infos_string = instruments_infos_string \
                                               + f"<span> :blue[{instrument_info}]$~~$||$~~$</span>"
                with st.container(border=True):
                    st.markdown(instruments_infos_string, unsafe_allow_html=True)

                #展示时序信息（节拍，时长，BPM，PPQN）
                #两行两列
                st.markdown("#### 🕓 时序信息")
                with st.container(border=True):
                    col1,col2,col3,col4=st.columns(
                        [1,1,1,1],gap='large')
                    col1.markdown('''**节拍**''')
                    col2.markdown(f''':blue-background[{time_signature}]''')
                    col3.markdown('**时长**')
                    col4.markdown(f''':blue-background[{total_time_string}]''')
                    col1, col2, col3, col4 = st.columns(
                        [1, 1, 1, 1], gap='large')
                    col1.markdown('**BPM**')
                    col2.markdown(f''':blue-background[{bpm}]''')
                    col3.markdown('**PPQN**')
                    col4.markdown(f''':blue-background[{ppgn}]''')

                #展示音轨信息
                st.markdown("#### 🎶 音轨信息")
                for track_info in track_infos:
                    with st.container(border=True):
                        st.markdown(f"{track_info[0]} - {track_info[1]}")
                        col1,col2,col3=st.columns(
                            [1,1,1],gap='large')
                        col1.markdown(f"乐器ID$~~${track_info[2]}")
                        col2.markdown(f"音符数量$~~${track_info[3]}")
                        col3.markdown(f"音轨时长$~~${track_info[4]}")

            def ShowTab2():
                '''
                展示tab2
                :return:
                '''
                uploadfile=UploadMidi()
                if uploadfile is not None:
                    [instruments_infos, time_signature, total_time_string, bpm,
                            ppgn, track_infos] = AnalyseMidi(uploadfile)
                    ShowMidiInfo(instruments_infos, time_signature,
                                 total_time_string, bpm, ppgn, track_infos)

            ShowTab2()

        with tab3:
            # midi学习指南的内容
            #插入函数，指定列数，然后判断列数，插入内容；
            # 可以将content值存成到一个列表中，然后后面Show的时候通过循环将每个内容展示。
            # if 'guide_content' not in st.session_state:
            #     st.session_state['guide_content'] = {}
            #     st.session_state['guide_content'][1] = '你好'
            #     st.session_state['guide_content'][2] = '你好'
            #     st.session_state['guide_content'][3] = '你好啊'
            #将每一列的内容分别存储到guide1.csv,guide2.csv,guide3.csv中。
            neirong1='新添加内容1'
            neirong2='新添加内容2'
            neirong3='新添加内容3'
            #读取guide1.csv,guide2.csv,guide3.csv中的内容，展示在页面中。
            # 展示指南


            guide_col1, guide_col2, guide_col3 = st.columns(
                [1, 1, 1], gap='small')

            def GuideInsertContent(col:int,title:str,content:str):
                #还要写一个将插入内容存储到文件的功能。保证数据能被存储。
                #然后再写一个读取该变量的功能，将数据展示出来。(注意获取的参数有：emojy（可选）（默认），标题，内容)
                if col==1:
                    col1_csv=pd.read_csv('guide1.csv',encoding='gbk')['1']
                    if str:
                        string_list=[title,content]
                        insert_guide_content=('$$$').join(string_list)
                        col1_csv.loc[len(col1_csv)] = insert_guide_content
                        col1_csv.to_csv('guide1.csv',index=False,encoding='gbk')
                    else:
                        st.error('输入内容不能为空')
                elif col==2:
                    col2_csv=pd.read_csv('guide2.csv',encoding='gbk')['2']
                    if str:
                        string_list=[title,content]
                        insert_guide_content=('$$$').join(string_list)
                        col2_csv.loc[len(col2_csv)] = insert_guide_content
                        col2_csv.to_csv('guide2.csv',index=False,encoding='gbk')
                    else:
                        st.error('输入内容不能为空')
                elif col==3:
                    col3_csv=pd.read_csv('guide3.csv',encoding='gbk')['3']
                    if str:
                        string_list=[title,content]
                        insert_guide_content=('$$$').join(string_list)
                        col3_csv.loc[len(col3_csv)] = insert_guide_content
                        col3_csv.to_csv('guide3.csv',index=False,encoding='gbk')
                    else:
                        st.error('输入内容不能为空')

            def ShowGuideContent():
                with guide_col1:
                    col1_csv=pd.read_csv('guide1.csv',encoding='gbk')['1']
                    col1_list=list(col1_csv)
                    for data in col1_list:
                        [title,content]=data.split('$$$')
                        if len(content) > 200:
                            with st.container(border=True, height=400):
                                st.markdown(f"#### {title}")
                                st.markdown(content.replace('\n', '  \n'))
                        else:
                            with st.container(border=True):
                                st.markdown(f"#### {title}")
                                st.markdown(content.replace('\n', '  \n'))
                with guide_col2:
                    col2_csv = pd.read_csv('guide2.csv',encoding='gbk')['2']
                    col2_list = list(col2_csv)
                    for data in col2_list:
                        [title, content] = data.split('$$$')
                        if len(content) > 200:
                            with st.container(border=True, height=400):
                                st.markdown(f"#### {title}")
                                st.markdown(content.replace('\n', '  \n'))
                        else:
                            with st.container(border=True):
                                st.markdown(f"#### {title}")
                                st.markdown(content.replace('\n', '  \n'))
                with guide_col3:
                    col3_csv = pd.read_csv('guide3.csv',encoding='gbk')['3']
                    col3_list = list(col3_csv)
                    for i,data in enumerate(col3_list):
                        [title, content] = data.split('$$$')
                        if len(content)>200:
                            with st.container(border=True,height=400):
                                st.markdown(f"#### {title}")
                                st.markdown(content.replace('\n', '  \n'))
                        else:
                            with st.container(border=True):
                                st.markdown(f"#### {title}")
                                st.markdown(content.replace('\n','  \n'))
            ShowGuideContent()


            # 评论区
            def cunfangchange(filepath, n):
                # 读取CSV文件
                df = pd.read_csv(filepath)
                # 检查行数是否大于n
                if len(df) > n:
                    # 只保留前n行
                    df = df.iloc[:n-1]
                df.to_csv(filepath, index=False)

            def cunfangshow(filepath, n):
                # 使用csv库读取csv文件，并展示
                with open(filepath,'r',encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for index,row in enumerate(reader):
                        if index < n:
                            # 获取时间戳和文本内容
                            timestamp = row[0]
                            text = row[1]
                            # 显示时间戳和文本内容
                            with st.container(border=True):
                                st.write(f'{timestamp}')
                                st.markdown(f'''$~~~~${text}''')

            def UpLoadComment(txt):
                if txt.strip() != '':
                    # 使用strip()去除两端的空白字符后，检查字符串是否非空
                    csv_file = 'cunfang.csv'
                    # 读取整个CSV文件的内容（如果有的话）
                    csv_content = []
                    with open(csv_file, 'r', newline='',
                              encoding='utf-8') as f:
                        reader = csv.reader(f)
                        for row in reader:
                            csv_content.append(row)
                            # 添加时间戳和上传内容作为新行的列表
                    timestamp = datetime.now().strftime(
                        '%Y-%m-%d %H:%M:%S')  # 格式化时间戳
                    new_row = [timestamp, txt]  # 两列：时间戳和文本
                    # 将新行添加到内容列表的最前面
                    csv_content.insert(0, new_row)
                    # 写入更新后的内容到CSV文件
                    with open(csv_file, 'w', newline='',
                              encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerows(csv_content)
                    st.success('内容已成功上传并添加时间戳！')
                else:
                    # 如果txt为空或仅包含空白字符，则显示错误消息
                    st.error('上传内容不能为空')

            comment_filepath = "cunfang.csv"  # CSV文件路径
            n = 10  # 指定n的值
            comment_txt = st.text_area(label='*在这里畅所欲言吧……*',
                                       max_chars=200,
                                       help='最大长度限制为200',
                                       placeholder='请输入……',)
            if st.button('上传'):
                UpLoadComment(comment_txt)
            cunfangchange(comment_filepath, n)
            cunfangshow(comment_filepath, n)

if master_password==WEBMASTER_KEY:
    # 管理员修改信息
    st.sidebar.title('streamlit测试')
    # 选择修改的元素
    add_selectbox = st.sidebar.selectbox(
        "您好，管理者，请选择进行修改的板块",
        ("推荐", "评论", "指南")
    )
    if add_selectbox == "推荐":
        with st.sidebar:
            operater = st.sidebar.radio(
                "请选择进行增加，还是删除。",
                ("增加", "删除"),
                key='recommend1'
            )
        if operater == "增加":
            #给一个输入文本框，输入要添加的音乐id，并通过按钮点击上传。
            control_box = st.sidebar.columns([3,1], gap='small')
            add_input = control_box[0].number_input(label='请输入音乐id号',
                                                    value=0,
                                                    key='manage_input1',
                                                    label_visibility='collapsed',
                                                    format='%d')
            # 按钮触发一个add_music函数，将音乐添加进列表中。
            if control_box[1].button('确认',key='manage_yes1'):
                if add_input:
                    add_music_to_com_data(int(add_input))
                else:
                    st.sidebar.error('操作内容不能为空')

        if operater == "删除":
            control_box = st.sidebar.columns([3,1], gap='small')
            add_input = control_box[0].number_input(label='请输入音乐id号',
                                                    value=0,
                                                    key='manage_input2',
                                                    label_visibility='collapsed',
                                                    format='%d')
            if control_box[1].button('确认',key='manage_yes2'):
                if add_input:
                    delete_music_from_com_data(int(add_input))
                else:
                    st.sidebar.error('操作内容不能为空')

        #同时展示乐曲编号和乐曲索引。
        recommend_now_data2=st.session_state.com_data.to_dict(orient='records')
        # 存储当前展示页的音乐信息字典列表
        for dt in recommend_now_data2:
            # 创建一个两列的布局，但我们只使用第一列。以后第二列可以添加一个emojy图。
            col1, col2 = st.sidebar.columns([4, 1])
            with col1:
                href = f':rainbow[{dt["song_id"]}]'
                st.markdown(href, unsafe_allow_html=True)
            col2.write(dt["id"])

    if add_selectbox == "评论":
        #给出一个单选框，选择进行增加，修改还是删除（此处示例增加功能）
        with st.sidebar:
            operator = st.sidebar.radio(
                "请选择进行增加，修改还是删除。",
                ("增加", "删除"),key='comment1'
            )
            if operator == "增加":
                # 增加功能
                txt=st.text_input("请输入要增加的评论")
                if st.button('上传',key='manage_upload1'):
                    UpLoadComment(txt)
                    cunfangchange(comment_filepath, n)
                cunfangshow(comment_filepath, n)

            if operator == "删除":
                add_input = st.sidebar.number_input(label='请输入要删除的评论id',
                                                        value=0,
                                                        key='manage_input3',
                                                        format='%d')
                if st.sidebar.button('确认', key='manage_yes3'):
                    if add_input:
                        pass
                    else:
                        st.sidebar.error('操作内容不能为空')
                    # 使用csv库读取csv文件，并展示
                filepath = 'cunfang.csv'
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for index, row in enumerate(reader):
                        if index < n:
                            # 获取时间戳和文本内容
                            timestamp = row[0]
                            text = row[1]
                            # 显示时间戳和文本内容
                            with st.container(border=True):
                                st.write(index)
                                st.write(f'{timestamp}')
                                st.markdown(f'''$~~~~${text}''')



    if add_selectbox == "指南":
        pass
        # 提供一个单选框，选择进行增加还是删除。删除的话则指定索引进行删除。
        index_select = st.sidebar.radio(
            "请选择进行增加，修改还是删除。",
            ("增加", "删除"),key='manage_guide1'
        )
        # 获取选择插入的列
        guide_col = st.sidebar.selectbox(
            "请选择操作内容的列",
            ("1", "2", "3")
        )
        if index_select == "增加":
            #展示插入内容的界面
            title_input=st.sidebar.text_input('请输入标题')
            content_input=st.sidebar.text_area('请输入内容')
            if st.sidebar.button('上传插入内容',key='manage_insert_guide1'):
                if title_input.strip() and content_input.strip():
                    try:
                        GuideInsertContent(int(guide_col),title_input,content_input)
                    except UnicodeEncodeError:
                        st.sidebar.error('文本中含有不可解析字符，请删除后再上传！')
        elif index_select == "删除":
            # 删除功能
            pass
            id_input = st.sidebar.number_input(label='请输入要删除的索引',
                                               value=0,
                                               key='manage_delete_guide1',
                                               format='%d')
            if st.sidebar.button('确认删除',key='manage_delete_guide2'):
                if guide_col == "1":
                    col1_csv = pd.read_csv('guide1.csv', encoding='gbk')
                    length = len(col1_csv['1'])
                    if id_input>=0 and id_input<=length-1:
                        # 删除csv文件中指定索引的内容
                        col1_csv.drop(id_input,inplace=True)
                        col1_csv.to_csv('guide1.csv',encoding='gbk')
                    else:
                        st.sidebar.error('索引超出范围')
                if guide_col == "2":
                    col2_csv = pd.read_csv('guide2.csv', encoding='gbk')
                    length = len(col2_csv['2'])
                    if id_input>=0 and id_input<=length-1:
                        # 删除csv文件中指定索引的内容
                        col2_csv.drop(id_input,inplace=True)
                        col2_csv.to_csv('guide2.csv',encoding='gbk')
                    else:
                        st.sidebar.error('索引超出范围')
                if guide_col == "3":
                    col3_csv = pd.read_csv('guide3.csv', encoding='gbk')
                    length = len(col3_csv['3'])
                    if id_input>=0 and id_input<=length-1:
                        # 删除csv文件中指定索引的内容
                        col3_csv.drop(id_input,inplace=True)
                        col3_csv.to_csv('guide3.csv',encoding='gbk')
                    else:
                        st.sidebar.error('索引超出范围')

        # 展示某一个列的内容
        if guide_col == "1":
            col1_csv = pd.read_csv('guide1.csv', encoding='gbk')['1']
            col1_list = col1_csv.to_list()
            for i, data in enumerate(col1_list):
                [title, content] = data.split('$$$')
                with st.sidebar.container(border=True):
                    st.sidebar.write(i)
                    st.sidebar.markdown(f"#### {title}")
                    st.sidebar.markdown(content.replace('\n','  \n'))

        if guide_col == "2":
            col2_csv = pd.read_csv('guide2.csv', encoding='gbk')['2']
            col2_list = col2_csv.to_list()
            for i, data in enumerate(col2_list):
                [title, content] = data.split('$$$')
                with st.sidebar.container(border=True):
                    st.sidebar.write(i)
                    st.sidebar.markdown(f"#### {title}")
                    st.sidebar.markdown(content.replace('\n','  \n'))
        if guide_col == "3":
            col3_csv = pd.read_csv('guide3.csv', encoding='gbk')['3']
            col3_list = col3_csv.to_list()
            for i, data in enumerate(col3_list):
                [title, content] = data.split('$$$')
                with st.sidebar.container(border=True):
                    st.sidebar.write(i)
                    st.sidebar.markdown(f"#### {title}")
                    st.sidebar.markdown(content.replace('\n','  \n'))


st_autorefresh(interval=2000)
