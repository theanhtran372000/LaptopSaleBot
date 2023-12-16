import yaml
import json
import random
import openai
import streamlit as st

from utils.chatgpt import ChatGPTClient
from utils.prompt import generate_prompt
from utils.display import chat_display
from utils.database import filter_select
from utils.format import laptop_to_string

# Load config file
with open('configs.yml', 'r') as f:
    configs = yaml.full_load(f)

# Init openai client
client = ChatGPTClient(configs)

# Streamlit app
# st.title("SaleBot")
st.markdown("<h1 style='text-align: center; color: black; margin-top: -50px; margin-bottom: -20px'>SaleBot</h1>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; color: grey;'><i>- thegioididong.com -</i></h5>", unsafe_allow_html=True)
st.divider()

openai.api_key = st.secrets['OPENAI_API_KEY']

# Init session state
if 'model_name' not in st.session_state:
    st.session_state['model_name'] = configs['openai']['model_name']
    
if 'messages' not in st.session_state:
    st.session_state['messages'] = [{
        'role': 'assistant',
        'content': open(configs['prompt']['intro']['greet']).read()
    }]

# Display chat history
for message in st.session_state.messages:
    chat_display(message['role'], message['content'])
        
prompt = st.chat_input("Bạn cần giúp gì không ạ?")
if prompt:
    
    # Add prompt to history
    st.session_state.messages.append({
        'role': 'user',
        'content': prompt
    })
    
    # Display prompt
    chat_display('user', prompt)
    
    # Detect user intent
    if 'category' not in st.session_state:
        prompt_category = generate_prompt(
            configs['prompt']['utils']['category'],
            prompt
        )
        category = client.get_answer(
            [
                {
                    'role': 'user',
                    'content': prompt_category
                }
            ],
            stream=False
        ).replace('"', '')
        
        st.success('Phân loại: {}'.format(category), icon="✅")
        st.session_state['category'] = category            
    
    # With each category
    if  st.session_state['category'] == "Tư vấn bán hàng":
        
        # Init requirements
        if 'requirements' not in st.session_state:
            st.session_state['requirements'] = [prompt]
        else:
            st.session_state['requirements'].append(prompt)
        
        # Get number of matched product
        customer_requirements = '\n'.join(st.session_state['requirements'])
        
        # Convert requirements to JSON
        prompt_format = generate_prompt(
            configs['prompt']['require']['format'],
            customer_requirements
        )
        
        json_string = client.get_answer(
            [
                {
                    'role': 'user',
                    'content': prompt_format
                }
            ],
            stream=False
        )
        requirements = json.loads(json_string)
        # st.text("Requirement: {}".format(requirements))
        
        # Filter data
        matched = filter_select(configs, **requirements)
        
        n_matched = len(matched)
        st.info('Có {} sản phẩm trùng khớp với yêu cầu của bạn.\nMột số sản phẩm bạn có thể tham khảo:\n{}'.format(
                n_matched, 
                '\n'.join(
                    [
                        "{}. {}".format(
                            i + 1, 
                            prod[1]
                        ) for i, prod in enumerate(
                            random.sample(
                                matched, 
                                min(5, n_matched)
                            )
                        )
                    ])
            ), 
        icon="💡")
        
        # If still have lot of candidates
        if n_matched > configs['openai']['min_matched']:
            
            # Ask to get more info -> reduce candidate
            with st.chat_message('assistant'):
                
                # Prepare prompt
                prompt_get = generate_prompt(
                    configs['prompt']['require']['get'],
                    customer_requirements
                )

                message_placeholder = st.empty()
                full_response = ''
                
                for chunk in client.get_answer(
                    [{
                        'role': 'user',
                        'content': prompt_get
                    }], 
                    stream=True
                ):
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + '| ', unsafe_allow_html=True)
                
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': full_response
                })
        
        else:
            
            # Save matched laptops
            if 'matched' not in st.session_state:
                st.session_state['matched'] = matched
                
            if 'customer_requirements' not in st.session_state:
                st.session_state['customer_requirements'] = customer_requirements
            
            if len(st.session_state['matched']) > 0:
                
                # Prepare prompt
                detail_string = '\n'.join([laptop_to_string(device) for device in st.session_state['matched']])
                prompt_compare = generate_prompt(
                    configs['prompt']['utils']['compare'],
                    st.session_state['customer_requirements'], 
                    detail_string, st.session_state.messages[-1]['content']
                )
                
                # Start compare, stop asking
                with st.chat_message('assistant'):
                    
                    
                    message_placeholder = st.empty()
                    full_response = ''
                    
                    for chunk in client.get_answer(
                        [{
                            'role': 'user',
                            'content': prompt_compare
                        }], 
                        stream=True
                    ):
                        if chunk.choices[0].delta.content is not None:
                            full_response += chunk.choices[0].delta.content
                            message_placeholder.markdown(full_response + '| ', unsafe_allow_html=True)
                    
                    st.session_state.messages.append({
                        'role': 'assistant',
                        'content': full_response
                    })
            
            else:
                response = generate_prompt(configs['prompt']['anno']['runout'])        
        
                chat_display('assistant', response)    
                del st.session_state['category']
                
                # Add to history
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': response
                })
        
    
    # elif st.session_state['category'] == "Chăm sóc khách hàng":
        
    #     # Get answer
    #     with st.chat_message('assistant'):

    #         message_placeholder = st.empty()
    #         full_response = ''
            
    #         for chunk in client.get_answer(st.session_state.messages, stream=True):
    #             if chunk.choices[0].delta.content is not None:
    #                 full_response += chunk.choices[0].delta.content
    #                 message_placeholder.markdown(full_response + '| ', unsafe_allow_html=True)
            
    #         st.session_state.messages.append({
    #             'role': 'assistant',
    #             'content': full_response
    #         })
    
    else:
        response = generate_prompt(configs['prompt']['anno']['apology'])        
        
        chat_display('assistant', response)    
        del st.session_state['category']
        
        # Add to history
        st.session_state.messages.append({
            'role': 'assistant',
            'content': response
        })
    
    