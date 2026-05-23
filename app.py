import pandas as pd
from PIL import Image
import re
import streamlit as st
import cv2
from groq import Groq
import io
from streamlit_drawable_canvas import st_canvas
import torch
import base64
import numpy as np
from diffusers import AutoPipelineForInpainting
import numpy as np
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

# from langchain.schema import Document
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer,util
from code_editor import code_editor
from streamlit_image_select import image_select
import os
import sys
import pymupdf as fitz
import PyPDF2
import requests 
from streamlit_navigation_bar import st_navbar
from langchain_community.llms import Ollama
import base64
from io import BytesIO
from PIL import Image, ImageDraw
from streamlit_lottie import st_lottie 
from streamlit_option_menu import option_menu
import json
from transformers import pipeline
import streamlit as st
from streamlit_modal import Modal
import streamlit.components.v1 as components
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval
from streamlit_pdf_viewer import pdf_viewer
import uuid
import time 
def get_new_uuid():
    # Generate a random UUID (UUID4) and convert it to a string
    return str(uuid.uuid4())


st.set_page_config(layout="wide")
dictionary=st.session_state
if "toggle" not in dictionary:
    dictionary["toggle"]=False

@st.cache_resource
def encoding_model():
    """
    Initializes and returns a SentenceTransformer model for text encoding.
    """
    model_name = "all-MiniLM-L6-v2"
    # model_name = "mixedbread-ai/mxbai-embed-large-v1"
    model = SentenceTransformer(model_name)
    return model
    
@st.cache_resource
def Q_and_A_model():
    qa_model = pipeline('question-answering', model='CATIE-AQ/QAmembert-large', tokenizer='CATIE-AQ/QAmembert-large')
    return qa_model
    
def executer(query):
    try:
        output = io.StringIO()
        sys.stdout = output
        
        exec(query)
        sys.stdout = sys.__stdout__
        return False
    except Exception as e:
        return f"Error: {str(e)}"
def dataframe_info(data):
    value= data[:5]
    data_columns = ",".join(data.columns)+"\n"
    instructions ="\nbelow is column names and data sample itself\n"
    return instructions+data_columns+str(value)

def extract_python_code(text):
    code_block=text.split("```")
    try:
        return [code_block[1].replace('python',"",1).replace('Python',"",1)]
    except:
        return []


# @st.cache_resource
def run_code_blocks(code_blocks,df,prompt=""):
    import io
    from contextlib import redirect_stdout

    buffer = io.StringIO()
    coder = str(code_blocks)
    runner_execute=True
    count=0
    while runner_execute:
            try:
                with redirect_stdout(buffer):
                    exec(coder)
    
                output = buffer.getvalue()
                runner_execute = False
            except Exception as e:
                coder_instruction = "\nCorrect the above mention code having below error\n"
                coder_instruction += "\nAlso keep in mind df is already has a dataframe in it don't add it by assuming anything\n"
                coder_instruction += "\nHere is the user request :{prompt} which has to bw fixed\n"
                code_error_value =str(e)
                st.error(code_error_value)
                coder = "\n".join(extract_python_code(consume_llm_api(coder+"\n"+coder_instruction+code_error_value)))
    
            if count==2:
                break
            count+=1

@st.cache_resource
def file_handler(file):
    """
    Handles file upload and returns the file path.
    """
    file_name = file.name
    if file_name.split(".")[-1] in ["csv"]:
        value = pd.read_csv(file)
        return value
    elif file_name.split(".")[-1] in ["xlsx"]:
        value = pd.read_excel(file)
        return value
    
    else:
        return None
def run_agent(prompt,df):

    intermediate_steps = prompt+"\n"
    intermediate_steps += "\nAbove is the user request that has to be completed. \n"
    intermediate_steps += "Below is the dataframe sample provided . \n"
    intermediate_steps += "The dataframe is as follows:\n"
    intermediate_steps +=  dataframe_info(df)+"\n"
    intermediate_steps += "You are a senior pandas dataframe developer and you have to write code to complete the user request.\n"
    intermediate_steps += "Below are the instructions\n"
    intermediate_steps += "There is a variable name 'df' which is a dataframe and have values.\n"
    intermediate_steps += "write code using df to manipulate it and give result according to user instruction.\n"
    intermediate_steps += "No need to load the data 'df' is the required variable.\n"
    intermediate_steps += "Whole team told you that you no need to use pd.read data is already there in df.\n"
    # intermediate_steps += "Statement present in the request willwe generic so consider column name related to sample data , Don't assume until said in request. \n"
    intermediate_steps += "Since we are showing code output in 'streamlit' not in terminal so code it properly as per streamlit need. \n"
    intermediate_steps += "This is last warning as a ceo of the company, you have to return only required code as per user request.\n"
    intermediate_steps += "Example\n" 
    intermediate_steps += "User request: 'show me the rows which has highest electricity_kwh_per_month\n"
    intermediate_steps += "```\nst.write(df[df['electricity_kwh_per_month'] == df['electricity_kwh_per_month'].max()])\n```\n"
    intermediate_steps += "You can see that above is the required code(in quotes) for user query(only required) and below is the next request.\n"
    intermediate_steps += "User request: {prompt}\n"
    intermediate_steps += "Generate code for the above request only but write some code to full fill user query.\n"
    return intermediate_steps
                
def send_prompt():
    return "please respond according to the prompt asked below from the above context"
    
def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
    
def consume_llm_api_updater(prompt):
    
    client = Groq(
        api_key="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"
    )

    completion = client.chat.completions.create(
        
        model="llama-3.3-70b-versatile",
        messages=[

            {
                "role": "system",
                "content": prompt
            },
        ],
        top_p=1,

    )
    return completion.choices[0].message.content   

def consume_llm_api(prompt,messages=None):
    """
    Sends a prompt to the LLM API and processes the streamed response.
    """
    url = "http://192.168.1.3:6000/api/llm-response"
    headers = {"Content-Type": "application/json"}
    payload = {"prompt": prompt}

    try:
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        return result.get("text", "")
        
    except requests.RequestException as e:
        print(f"Error consuming API: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

@st.cache_resource
def prompt_improvment(pre_prompt):

    enhancement="Please use details from the prompt mentioned above, focusing only what user is thinking with the prompt and also add 8k resolution. Its a request only provide image description and brief prompt no other text."
    prompt = pre_prompt+"\n"+enhancement

    return consume_llm_api(prompt)

def process_pdf(file):
    documents = []
    with open(file, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text = page.extract_text()
            if text:  # Ensure that the page has text
                documents.append(Document(page_content=text))
    return documents
    
def numpy_to_list(array):

    current=[]
    for value in array:
        if isinstance(value,type(np.array([]))):
            result=numpy_to_list(value)
            current.append(result)
        else:
            
            current.append(int(value))
    return current

def refer_api(prompt):

    init_image = [[1,1,1]*1000]*1000
    mask_image = [[True]*1000]*1000
    API_URL = "http://192.168.1.3:6000/api/llm-response"
    initial_image_base64 = numpy_to_list(np.array(init_image))
    mask_image_base64 = numpy_to_list(np.array(mask_image))
    payload = {
        "prompt": prompt,  # Replace with your desired prompt
        "initial_img": initial_image_base64,
        "masked_img": mask_image_base64,
        "negative_prompt": negative_prompt # Replace with your negative prompt
    }

    response_ = requests.post(API_URL, json=payload)
    response_data = response_.json()
    output_image_base64 = response_data.get("img", "")
    output_image=np.array(output_image_base64,dtype=np.uint8)

    output_image = Image.fromarray(output_image)
    # output_image.show()
    return output_image
    
def model_out_put(init_image,mask_image,prompt,negative_prompt):
    if np.array(mask_image).all():
        l,m=np.array(mask_image).shape
        image =refer_api(prompt).resize((l,m))
        return image
    API_URL = "http://192.168.1.3:6000/api/llm-response"
    initial_image_base64 = numpy_to_list(np.array(init_image))
    mask_image_base64 = numpy_to_list(np.array(mask_image))
    payload = {
        "prompt": prompt,  # Replace with your desired prompt
        "initial_img": initial_image_base64,
        "masked_img": mask_image_base64,
        "negative_prompt": negative_prompt # Replace with your negative prompt
    }
    response_ = requests.post(API_URL, json=payload)
    response_data = response_.json()
    output_image_base64 = response_data.get("img", "")

    output_image=np.array(output_image_base64,dtype=np.uint8)

    output_image = Image.fromarray(output_image)
    # output_image.show()
    return output_image

@st.cache_resource
def multimodel():
    pipeline_ = pipeline("text-classification", model = "model_path")
    return pipeline_
   
def multimodel_output(prompt):
    pipeline_ = multimodel()
    image = pipeline_(prompt)
    return image[0]['label']

def d4_to_3d(image):
    formatted_array=[]
    for j in image:
        neste_list=[]
        for k in j:
            if any([True if i>0 else False for i in k]):
                neste_list.append(True)
            else:
                neste_list.append(False)
        formatted_array.append(neste_list)
    return np.array(formatted_array)

def link_mask_image(dicts):
    os.makedirs("mask_image", exist_ok=True)
    with open(f"mask_image/{str(dictionary['new_id'])}.json", "w") as write:
            json.dump(dicts,write,indent=2)

    

screen_width = streamlit_js_eval(label="screen.width",js_expressions='screen.width')
screen_height = streamlit_js_eval(label="screen.height",js_expressions='screen.height')

st.write(screen_width,"screen width",screen_height,"screen height")
if screen_width<=495:
    st.header("Scroll down to use")
img_selection=None

# Specify canvas parameters in application
drawing_mode = st.sidebar.selectbox(
    "Drawing tool:", ("freedraw", "transform")
)



if "every_prompt_with_val" not in dictionary:
    dictionary['every_prompt_with_val']=[]
if "current_image" not in dictionary:
    dictionary['current_image']=[]
if "prompt_collection"  not in dictionary:
    dictionary['prompt_collection']=[]
if "user" not in dictionary:
    dictionary['user']=None
if "current_session" not in dictionary:
    dictionary['current_session']=None
if "image_movement" not in dictionary:
    dictionary['image_movement']=None
if "text_embeddings" not in dictionary:
    dictionary['text_embeddings']={}
if "rerun" not in dictionary:
    dictionary['rerun']="good"
    st.rerun()
if "upload_file_name" not in dictionary:
    dictionary['upload_file_name'] = "no file"
if "new_id" not in dictionary:
    dictionary["new_id"] = get_new_uuid()


stroke_width = st.sidebar.slider("Stroke width: ", 1, 1, 100)
if drawing_mode == 'point':
        point_display_radius = st.sidebar.slider("Point display radius: ", 1, 1, 100)
stroke_color = "#F0252FA6"
bg_color = "#eee"


column1,column2=st.columns([0.7,0.35])

with open("DataBase/datetimeRecords.json","r") as read:
    dateTimeRecord=json.load(read)
with column2:
    st.header("HISTORY")
    tab1,tab5,tab2,tab4=st.tabs(["CHAT HISTORY","FREE API","PROMPT IMPROVEMENT","LOGIN"])
    with tab1:

        
 
        if not len(dictionary['every_prompt_with_val']):
            st.header("I will store all the chat for the current session")
            with open("lotte_animation_saver/animation_4.json") as read:
                url_json=json.load(read)
            st_lottie(url_json,height = 400)
        else:

            with st.container(height=600):


                for index,prompts_ in enumerate(dictionary['every_prompt_with_val'][::-1]):
                    # messages = []

                    # for i_ in dictionary['every_prompt_with_val']:
                    #     if "@working" in i_[-1]:
                    #         messages.append({"role":"user","content":i_[0]})
                    #         # messages.append({"role":"assistant","content":dictionary['every_prompt_with_val'][i_][1]})
                    #     else:
                    #         messages.append({"role":"user","content":i_[0]})
                    #         messages.append({"role":"assistant","content":i_[1]})

                    if prompts_[-1]=="@working":
                        if index==0:
                            st.write(prompts_[0].split(send_prompt())[-1].upper() if send_prompt() in prompts_[0] else prompts_[0].upper())
                            data_need=""
                            while(len(data_need)==0):
                                if len(prompts_)==3:
                                        data_need = consume_llm_api(prompts_[1])
                                        st.write(data_need)
                                else:
                                        data_need = consume_llm_api(prompts_[0])
                                        st.write(data_need)
                                
                            dictionary['every_prompt_with_val'][-1]=(prompts_[0],str(data_need))


                            
                    elif isinstance(prompts_[-1],str):
                        show_case_text=prompts_[0].split(send_prompt())[-1].upper() if send_prompt() in prompts_[0] else prompts_[0].upper()
                        if index==0:
                            st.text_area(label=show_case_text,value=prompts_[-1],height=500,key=str(index))
                        else:
                            st.text_area(label=show_case_text,value=prompts_[-1],key=str(index))

                    else:
                        st.write(prompts_[0].upper())
                        with st.container(height=400):
                            format1,format2=st.columns([0.2,0.8])
                            with format1:
                                new_img=Image.open("ALL_image_formation/image_gen.png")
                                st.write("<br>",unsafe_allow_html=True)
                                size = min(new_img.size)
                                mask = Image.new('L', (size, size), 0)
                                draw = ImageDraw.Draw(mask)
                                draw.ellipse((0, 0, size, size), fill=255)

                                image = new_img.crop((0, 0, size, size))
                                image.putalpha(mask)
                                st.image(image)                    
                            with format2:

                                st.write("<br>",unsafe_allow_html=True)
                                size = min(prompts_[-1].size)
                                mask = Image.new('L', (size, size), 0)
                                draw = ImageDraw.Draw(mask)
                                draw.ellipse((0, 0, size, size), fill=255)

                                # Crop the image to a square and apply the mask
                                image = prompts_[-1].crop((0, 0, size, size))
                                image.putalpha(mask)
                                st.image(image)

    with tab5:
        st.write("ADD PINECONE API KEY TO GET FREE LLM API")
        random_val = """
def prompt_limmiter(prompt):

    import requests
    from sentence_transformers import SentenceTransformer
    from pinecone import Pinecone, ServerlessSpec
    Gen_api = "https://cb82b3240dd2.ngrok-free.app/api/llm-response"
    api_key = "xxxxxxxxxxxxxxxxxxxxxx----pine cone api key---xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    pc = Pinecone(api_key=api_key)
    model = SentenceTransformer("all-mpnet-base-v2")
    try:
        index_name = "quickstart"
        pc.create_index(
            name=index_name,
            dimension=768, 
            metric="cosine", 
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            ) 
        )
    except:
        pass
    index = pc.Index(index_name)
    index.upsert(
        vectors=[
            {
                "id": "lorum", 
                "values": [float(i) for i in list(model.encode("lorum"))],  
                "metadata": {"string":str(prompt)}
                
            }
        ]
    )

    gen_api_response = requests.post(url = Gen_api,json={"api_key": api_key},verify=False)

    if gen_api_response.json().get("status"):
        response = index.query(
        vector=[float(i) for i in model.encode(str(prompt))],
        top_k=1,
        include_metadata=True,
    )
        
    return response['matches'][0]['metadata']['string']
"""
        with st.container(height=int(screen_height//1.8)):
            st.code(random_val,language="python")
    with st.sidebar:
        
        if "current_image" in dictionary and len(dictionary['current_image']):
            with st.container(height=350):
                dictinory_length=len(dictionary['current_image'])
                
                img_selection = image_select(
                    label="",
                    images=dictionary['current_image'] if len(dictionary['current_image'])!=0 else None,
                )
                if img_selection in dictionary['current_image']:
                    dictionary['current_image'].remove(img_selection)
                    dictionary['current_image'].insert(0,img_selection)
                    if dictionary['image_movement']!=img_selection:
                        dictionary['image_movement']=img_selection
                        st.rerun()                    # st.rerun()

                img_selection.save("image.png")
            with open("image.png", "rb") as file:
                downl=st.download_button(label="DOWNLOAD",data=file,file_name="image.png",mime="image/png")
            os.remove("image.png")
        else:

            st.header("This section will store the updated images")
            with open("lotte_animation_saver/animation_1.json") as read:
                url_json=json.load(read)
            st_lottie(url_json,height = 200)
    with tab2:
        if len(dictionary['prompt_collection'])!=0:
            with st.container(height=600):
                prompt_selection=st.selectbox(label="Select the prompt for improvment",options=["Mention below are prompt history"]+dictionary["prompt_collection"],index=0)

                if prompt_selection!="Mention below are prompt history":

                    generated_prompt=prompt_improvment(prompt_selection)
                    dictionary['generated_image_prompt'].append(generated_prompt)
                    st.write_stream(generated_prompt)

        else:

            st.header("This section will provide prompt improvement section")
            with open("lotte_animation_saver/animation_3.json") as read:
                url_json=json.load(read)
            st_lottie(url_json,height = 400)
        with tab4:
            
            # with st.container(height=600):

            if not dictionary['user']   : 
                with st.form("my_form"):
                    # st.header("Please login for save your data")
                    with open("lotte_animation_saver/animation_5.json") as read:
                        url_json=json.load(read)
                    st_lottie(url_json,height = 200)                
                    user_id = st.text_input("user login")
                    password = st.text_input("password",type="password")
                    submitted_login = st.form_submit_button("Submit")
                    # Every form must have a submit button.

                    if submitted_login:
                        with open("DataBase/login.json","r") as read:
                            login_base=json.load(read)
                        if user_id in login_base and login_base[user_id]==password:
                            dictionary['user']=user_id
                            st.rerun()
                        else:
                            st.error("userid or password incorrect")

                        st.write("working")
                    modal = Modal(
                        "Sign up", 
                        key="demo-modal",
                        
                        padding=10,    # default value
                        max_width=600  # default value
                    )
                open_modal = st.button("sign up")
                if open_modal:
                    modal.open()

                if modal.is_open():
                    with modal.container():

                        with st.form("my_form1"):
                            sign_up_column_left,sign_up_column_right=st.columns(2)
                            with sign_up_column_left:
                                with open("lotte_animation_saver/animation_6.json") as read:
                                    url_json=json.load(read)
                                st_lottie(url_json,height = 200) 
    
                            with sign_up_column_right:
                                user_id = st.text_input("user login")
                                password = st.text_input("password",type="password")
                                submitted_signup = st.form_submit_button("Submit")

                            if submitted_signup:
                                with open("DataBase/login.json","r") as read:
                                    login_base=json.load(read)
                                if not login_base:
                                    login_base={}
                                if user_id not in login_base:
                                    login_base[user_id]=password
                                    with open("DataBase/login.json","w") as write:
                                        json.dump(login_base,write,indent=2)  
                                    st.success("you are a part now")  
                                    dictionary['user']=user_id
                                    modal.close()                       
                                else:
                                    st.error("user id already exists")
            else:
                st.header("REPORTED ISSUES")
                with st.container(height=370):

                    with open("DataBase/datetimeRecords.json") as feedback:
                        temp_issue=json.load(feedback)

                    arranged_feedback=reversed(temp_issue['database'])
                    
                    for report in arranged_feedback:
                        user_columns,user_feedback=st.columns([0.3,0.8])

                        with user_columns:
                            st.write(report[-1])
                        with user_feedback:
                            st.write(report[1])
                     
                feedback=st.text_area("Feedback Report and Improvement",placeholder="")
                summit=st.button("submit")
                if summit:
                    with open("DataBase/datetimeRecords.json","r") as feedback_sumit:
                        temp_issue_submit=json.load(feedback_sumit)        
                    if  "database" not in temp_issue_submit:
                        temp_issue_submit["database"]=[]
                    temp_issue_submit["database"].append((str(datetime.now()),feedback,dictionary['user'])) 
                    with open("DataBase/datetimeRecords.json","w") as feedback_sumit:
                        json.dump(temp_issue_submit,feedback_sumit)                    
                            


                    # st.rerun()
                
                
                    



bg_image = None
bg_doc = st.sidebar.file_uploader("PLEASE UPLOAD DOC FOR PPT/PDF/STORY:", type=["pdf","xlsx","csv","png", "jpg"])
if bg_doc and bg_doc.name.split(".")[-1] in ["png", "jpg"]:
    bg_image = bg_doc
    bg_doc=None


if "bg_image" not in dictionary:
    dictionary["bg_image"]=None

if img_selection  and dictionary['bg_image']==bg_image:
    gen_image=dictionary['current_image'][0]
else:
    if bg_image:
        gen_image=Image.open(bg_image) 
    else:
        gen_image=None





with st.spinner('Wait for it...'):
    with column1:
    # Create a canvas component
        changes,implementation,current=st.columns([0.01,0.9,0.01])

        model = encoding_model()
        with implementation:
            with st.spinner('Wait for it...'):
                    # pdf_file = st.file_uploader("Upload PDF file", type=('pdf'))
                    st.write("<br>"*3,unsafe_allow_html=True)
                    if bg_doc:
                        canvas_result=None
                        # st.write(bg_doc.name)
                        file_type = file_handler(bg_doc)
                        
                        if isinstance(file_type,type(None)) :
                            
                            with open(bg_doc.name, "wb") as f_work:
                                f_work.write(bg_doc.getbuffer())

                            data = process_pdf(bg_doc.name)
                            if str(data) not in dictionary['text_embeddings']:
                                dictionary['text_embeddings']={}
                                text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=2000)
                                chunks = text_splitter.split_documents(data)

                                dictionary['text_embeddings'][str(data)]={str(chunk.page_content):model.encode(str(chunk.page_content)) for chunk in chunks}

                                embeddings = [dictionary['text_embeddings'][str(data)][i] for i in dictionary['text_embeddings'][str(data)]]
                                vector_store = []
                                for i in dictionary['text_embeddings'][str(data)]:
                                    vector_store.append((dictionary['text_embeddings'][str(data)][i],i))
                            else:
                                embeddings = [dictionary['text_embeddings'][str(data)][i] for i in dictionary['text_embeddings'][str(data)]]
                                vector_store = []
                                for i in dictionary['text_embeddings'][str(data)]:
                                    vector_store.append((dictionary['text_embeddings'][str(data)][i],i))
                        else:

                            code_runner,code_check,data_frame = st.tabs(["🗃 code runner", "code","📈 Chart"])
                            with data_frame:
                                file_type = st.data_editor(file_type,hide_index=True,use_container_width=True,num_rows='dynamic')
                            with code_check:
                                if len(dictionary['every_prompt_with_val'])!=0:
                                    with st.form("code_form"):
                                        code_new=extract_python_code(dictionary['every_prompt_with_val'][-1][-1])
                                        code_new = "\n".join(code_new)
                                        response = code_editor(code_new, lang="python", key="editor1",height=screen_height/4,allow_reset=True,response_mode="blur",focus=True)

                                        submitted = st.form_submit_button("Submit Code")

                            with code_runner:
                                if dictionary['upload_file_name']==str(bg_doc.name):
                                    if len(dictionary['every_prompt_with_val'])!=0 and submitted:
                                        code_new = response.get('text')
                                        run_code_blocks(code_new,file_type)
                                    elif len(dictionary['every_prompt_with_val'])!=0 :
                                        code_new=extract_python_code(dictionary['every_prompt_with_val'][-1][-1])
                                        code_new = "\n".join(code_new)
                                        run_code_blocks(code_new,file_type,dictionary['every_prompt_with_val'][-1][0])
                                st.header("Please ask your query from data")
                                

                    else:
                        dictionary['toggle'] = st.toggle("Image Editor mode",key=dictionary["new_id"],value = dictionary['toggle'])
                        # toggle = st.toggle("Toggle",key=dictionary["new_id"])
                        # else:
                        #     toggle = st.toggle("Toggle",value=dictionary.toggle)
                        
                        
                        if dictionary['toggle'] :
                        # st.image(Image.open("ALL_image_formation\image_gen.png"))
                            
                            
                            canvas_result = st_canvas(
                                    fill_color="rgba(0, 0, 0, 0.3)",  # Fixed fill color with some opacity
                                    stroke_width=stroke_width,
                                    stroke_color=stroke_color,
                                    background_color=bg_color,
                                    background_image=gen_image if gen_image else Image.open("ALL_image_formation/image_gen.png"),
                                    update_streamlit=True,
                                    height=int(screen_height//2.16) if screen_height!=1180 else screen_height//2,
                                    width=int(screen_width//2.3)  if screen_width!=820 else screen_width//2,
                                    drawing_mode=drawing_mode,
                                    point_display_radius=point_display_radius if drawing_mode == 'point' else 0,
                                    key="canvas",
                                )

                        else:
                            
                            user,about_me = st.tabs(["WEB SEARCH","Developer"])
                            with user:
                                st.markdown("### 🤖 Generative Studio")
                                st.info(
                                    """
                                    This AI-powered assistant goes **beyond general chat system** by combining:
                                    - 💬 Conversational AI 
                                    - 🧠 Code generation & explanations
                                    - 📑 Summarization & translation
                                    - 🖼 Image generation (AI art)
                                    - 📊 File-based data analysis (PDF,CSV, EXCEL,PNG,JPG)
                                    - 🔗 Can connect to developer in right tab
                                    
                                    Built with **Streamlit + LLama based + Python**, the app creates a full-stack AI experience that’s interactive, creative, and practical for coders, writers, and curious minds alike.
                                    """,
                                    icon="🚀"
                                )
                            with about_me:
                                with st.container(height=400):
                                        

                                    # Header and Subheader
                                    st.title("Mayank Raj")
                                    st.subheader("Associate II Data Scientist | AI/ML Specialist")

                                    st.write("📧 rajstarts35325@gmail.com")
                                    # st.write("📞 6204396601")
                                    st.write("📍 Kolkata, India")

                                    st.markdown("---")

                                    # --- ABOUT ME ---
                                    st.header("👋 About Me")
                                    st.write("""
                                    AI/ML Specialist skilled in developing and deploying AI solutions including LLM fine-tuning, NLP search optimization,
                                    and automated data pipelines. Proficient in Python, Streamlit, and cloud platforms. Proven track record in
                                    boosting system efficiency and reducing resource costs. Eager to leverage my expertise to drive innovation
                                    and optimize AI-driven solutions in a challenging and rewarding role.
                                    """)

                                    st.markdown("---")

                                    # --- WORK EXPERIENCE ---
                                    st.header("🚀 Work Experience")

                                    st.subheader("Associate II - Data Scientist | UST Global")
                                    st.write("📅 Dec 2023 – Present")
                                    st.markdown("""
                                    - Designed a multi-model **Generative AI Code Copilot** to improve software development cycle, cutting down COBOL code conversion time from 1–2 days to 3–4 hours.  
                                    - Dockerized and deployed the solution on **GCP Cloud Run** for seamless CI/CD integration.  
                                    - Developed a **comprehensive NLP search engine pipeline** utilizing BERT-based models (NER, intent classification), with auto-triggered configuration refresh and vector updates.  
                                    - Built a **clinical NER system** with spaCy to extract patient conditions from discharge summaries, mapping to **ICD + HCC codes**, with a **Streamlit-agraph knowledge graph**.  
                                    - Crafted a **multi-LLM Q&A web application** using Streamlit + Langchain + Pinecone/FAISS, integrating vector search on Azure OpenAI, AWS Bedrock, Vertex AI, and OpenAI.  
                                    - Fine-tuned RoBERTa-base with prompt engineering to avoid week-long training cycles, enabling faster model outcome prediction.
                                    """)

                                    st.subheader("Associate I - Data Scientist | UST Global")
                                    st.write("📅 Jan 2023 – Jun 2023")
                                    st.markdown("""
                                    - Automated data generation and **model ID pipelines** for named entity recognition use cases.  
                                    - Improved NLP search engine performance from **10 seconds to 10 milliseconds**.  
                                    - Generated 700k+ data rows using **LLaMA** for healthcare EDA analysis.  
                                    - Developed **RFI Response Builder** using prompt-engineered document segmentation.  
                                    - Optimized sentence transformer pipeline from 5 min → 1.4 sec using **Pinecone vector DB**.  
                                    - Built graph-based clinical assistants showing full medical workflows post-entity recognition.  
                                    - Enabled **document-based querying** using **Langchain RAG over LLMs** on GCP Streamlit apps.
                                    """)

                                    st.markdown("---")

                                    # --- PROJECTS ---
                                    st.header("🛠 Projects")

                                    st.subheader("🔸 Generative Image Studio")
                                    st.markdown("""
                                    - Adobe-style **AI-powered generative image editing** using fill, expand, and text-to-edit prompts.  
                                    - Cloud-deployed on **Hugging Face Spaces (RTX 3070)** with multi-device UI and gallery support.  
                                    - Includes **chat + Q&A generation** from structured CSV/Excel inputs using LLM agents.  
                                    - Powered by **RunPod-hosted LLMs** for real-time editing + insights from uploaded data.
                                    """)

                                    st.subheader("🔸 Data Generation via Agentic Search")
                                    st.markdown("""
                                    - Multi-agent LLM workflow to search and extract clean training data from Wikipedia API.  
                                    - Designed for **hallucination reduction**, accuracy improvement, and auditing workflows.  
                                    - GPU-accelerated deployment (RTX 3070).  
                                    """)

                                    st.subheader("🔸 Zexture (Gesture Recognition)")
                                    st.markdown("""
                                    - OpenCV-based real-time **hand gesture classification system**.  
                                    - Random Forest classifier with 90% accuracy.  
                                    - Open-sourced and demo available on LinkedIn (25k+ views).
                                    """)

                                    st.markdown("---")

                                    # --- SKILLS ---
                                    st.header("🧠 Skills")
                                    st.markdown("""
                                    - **Core AI/ML**: NLP, Deep Learning, Pytorch, Langchain, Hugging Face, Transformers  
                                    - **MLOps & Deployment**: Streamlit, Docker, Cloud Run (GCP), Vertex AI, Azure  
                                    - **Libraries**: scikit-learn, pandas, numpy, matplotlib, OpenCV, spaCy, TSNE  
                                    - **Database & Vector DBs**: MongoDB, FAISS, Pinecone  
                                    - **Developer Tools**: Git, OLLAMA, NGROK  
                                    - **Concepts/Models**: Autoencoders, Recommender Systems, Classification, Retrieval-Augmented Generation (RAG)
                                    """)

                                    st.markdown("---")

                                    # --- EDUCATION ---
                                    st.header("🎓 Education")
                                    st.markdown("""
                                    **B.Tech in Information Technology**  
                                    Institute of Engineering and Management, Kolkata (2018 – 2022)  
                                    CGPA: 8.3 / 10  
                                    """)

                                    # --- CERTIFICATIONS ---
                                    st.header("📜 Certifications")
                                    st.markdown("""
                                    - Microsoft Certified: Azure Fundamentals  
                                    - [Problem Solving (Intermediate) – HackerRank](https://www.hackerrank.com/certificates/e58b24078d49)  
                                    - [Python (Intermediate) – HackerRank](https://www.hackerrank.com/certificates/6c8372e09ea1)  
                                    - [SQL (Intermediate) – HackerRank](https://www.hackerrank.com/certificates/d541d8ca0176)  
                                    """)

                                    st.markdown("---")

                                    # --- LINKS ---
                                    st.header("🔗 Links")
                                    st.markdown("""
                                    - GitHub: [https://github.com/warhawkmonk](https://github.com/warhawkmonk)  
                                    - LinkedIn: [https://www.linkedin.com/in/mayank-raj-2b51a3178/](https://www.linkedin.com/in/mayank-raj-2b51a3178/)  
                                    - Hackerrank: [https://www.hackerrank.com/warhawk_monk](https://www.hackerrank.com/warhawk_monk)  
                                    - CodeChef: [https://www.codechef.com/users/monk5235](https://www.codechef.com/users/monk5235)  
                                    """)

                                    st.markdown("---")

                                    st.caption("🚀 Built with ❤️ using Streamlit | Updated: July 2025")

                            
                            class B():
                                def __init__(self):
                                    self.image_data = gen_image if gen_image else Image.open("ALL_image_formation/image_gen.png")
                            canvas_result = B()




with column1:
    # prompt=st.text_area("Please provide the prompt")
    prompt=st.chat_input("Please provide the prompt")
   
    negative_prompt="the black masked area"

    # run=st.button("run_experiment")
if bg_doc:
    if dictionary['upload_file_name']!=str(bg_doc.name) and prompt:
        dictionary['upload_file_name'] = str(bg_doc.name) 
    if len(dictionary['every_prompt_with_val'])==0:
        query_embedding = model.encode(["something"])
    else:

        query_embedding = model.encode([dictionary['every_prompt_with_val'][-1][0]])
    if isinstance(file_type,type(None)) :
        retrieved_chunks = max([(util.cos_sim(match[0],query_embedding),match[-1])for  match in vector_store])[-1]
        with implementation:
            with st.spinner('Wait for it...'):
                text_lookup=retrieved_chunks
                pages=[]
                buffer = bg_doc.getbuffer()
                byte_data = bytes(buffer)
                with fitz.open(stream=byte_data, filetype="pdf") as doc:
                                
                    for page_no in range(doc.page_count):
                        pages.append(doc.load_page(page_no - 1))
                    
                    with st.container(height=int(screen_height//1.8)):
                        for pg_no in pages[::-1]:
                            areas = pg_no.search_for(text_lookup)
                            for area in areas:
                                pg_no.add_rect_annot(area)

                            pix = pg_no.get_pixmap(dpi=100).tobytes()
                            st.image(pix,use_column_width=True)
                        
if bg_doc and prompt:
    with st.spinner('Wait for it...'):  
        query_embedding = model.encode([prompt])
        if isinstance(file_type,type(None)) :
            retrieved_chunks = [(util.cos_sim(match[0],query_embedding),match[-1]) for  match in vector_store]
            retrieved_chunks.sort(reverse=True)

            combined_context = ""
            for select in retrieved_chunks[:2]:
                combined_context += select[-1] + "\n"
            
            prompt = "Context: "+ combined_context +"\n"+send_prompt()+ "\n"+prompt

            modifiedValue="@working"
            dictionary['every_prompt_with_val'].append((prompt,modifiedValue))
            st.rerun()
        else:
            modifiedValue="@working"
            new_prompt = run_agent(prompt,file_type)
            dictionary['every_prompt_with_val'].append((prompt,new_prompt,modifiedValue))
            st.rerun()

elif not bg_doc and canvas_result.image_data is not None:
    if prompt:

        text_or_image=multimodel_output(prompt)
        
        if text_or_image=="LABEL_0" :
        
            if "generated_image_prompt" not in dictionary:
                dictionary['generated_image_prompt']=[]
            if prompt not in dictionary['prompt_collection'] and prompt not in dictionary['generated_image_prompt']:
                dictionary['prompt_collection']=[prompt]+dictionary['prompt_collection']
            new_size=np.array(canvas_result.image_data).shape[:2]
            new_size=(new_size[-1],new_size[0])
            if bg_image!=dictionary["bg_image"] :
                dictionary["bg_image"]=bg_image
                if bg_image!=None:
                    imf=Image.open(bg_image).resize(new_size)
                else:
                    with open("lotte_animation_saver/animation_4.json") as read:
                        url_json=json.load(read)        
                    st_lottie(url_json) 
                    imf=Image.open("ALL_image_formation/home_screen.jpg").resize(new_size)
            else:
                if len(dictionary['current_image'])!=0:
                    imf=dictionary['current_image'][0]
                else:
                    with open("lotte_animation_saver/animation_4.json") as read:
                        url_json=json.load(read)        
                    st_lottie(url_json) 
                    imf=Image.open("ALL_image_formation/home_screen.jpg")

            negative_image =d4_to_3d(np.array(canvas_result.image_data))
            if np.sum(negative_image)==0:
                negative_image=Image.fromarray(np.where(negative_image == False, True, negative_image))
            else:
                negative_image=Image.fromarray(negative_image)
            
            modifiedValue=model_out_put(imf,negative_image,prompt,negative_prompt)
            # modifiedValue.save("ALL_image_formation/current_session_image.png")
            dictionary['current_image']=[modifiedValue]+dictionary['current_image']
            dictionary['every_prompt_with_val'].append((prompt,modifiedValue))
            st.rerun()
        else:
            modifiedValue="@working"
            dictionary['every_prompt_with_val'].append((prompt,modifiedValue))
            st.rerun()

temp_saving = []
for elements in dictionary['every_prompt_with_val']:
    space =[]
    space.append(elements[0])
    if not isinstance(elements[-1], str):
        space.append(list(elements[-1].getdata()))
    else:
        space.append(elements[-1])
    temp_saving.append(space)
link_mask_image(temp_saving)






    
        
        


