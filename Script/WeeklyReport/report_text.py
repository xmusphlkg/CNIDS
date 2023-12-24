from openai import OpenAI
import os
import time

def openai_single(model_create, model_check, user_content, section, disease, token = 500, max_retries=10, delay=1):
    """
    Fetches a response from the OpenAI API with automatic retries on failure.

    - model_create: The name of the model to use for the completion.
    - model_check: The name of the model to use for the check.
    - user_content: The content provided by the user for the completion.
    - section: The section of the report.
    - disease: The disease of the report.
    - token: The maximum number of tokens to generate.
    - max_retries: Maximum number of retries before giving up.
    - delay: Delay between retries in seconds.
    :return: The API response or None if all retries failed.
    """
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["OPENAI_API_BASE"],
    )

    print(f"Creating response for {section} section of {disease} report...")
    attempt = 0
    while attempt < max_retries:
        print("Start generate raw content...")
        box_content = fetch_openai(model_create, client,
                                   user_content,
                                   "You are a epidemiologist.",
                                   token, max_retries, delay)
        print("Start check content...")
        box_check = fetch_openai(model_check, client,
                                 f"""Analyze the following text and tell me if it is the {section} section to {disease} analysis report. If it is, please answer me Yes. If not, please answer me No.
                                          
                                {box_content}""",
                                "You are a language editing robot.",
                                token, max_retries, delay)
        if "Yes" in box_check:
            break
        else:
            attempt += 1
            print(f"Retrying ({attempt}/{max_retries})...\n")
            print(f"box_check: {box_check}\n")
            print(f"box_content: {box_content}\n")
    if attempt >= max_retries:
        print(f"Maximum retries reached. Failed to create response.")
        return None
    else:
        print(f"Response created successfully after {attempt} try.")
        return box_content
    
def openai_mail(model_create, model_check, user_content, token = 4096, max_retries=10, delay=1):
    """
    Fetches a response from the OpenAI API with automatic retries on failure.

    - model_create: The name of the model to use for the completion.
    - model_check: The name of the model to use for the check.
    - user_content: The content provided by the user for the completion.
    - token: The maximum number of tokens to generate.
    - max_retries: Maximum number of retries before giving up.
    - delay: Delay between retries in seconds.
    :return: The API response or None if all retries failed.
    """
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["OPENAI_API_BASE"],
    )

    attempt = 0
    print(f"Creating response for mail content...")
    while attempt < max_retries:
        print("Start generate raw content...")
        content_raw = fetch_openai(model_create, client,
                                   user_content,
                                    "You are a epidemiologist.",
                                   token, max_retries, delay)
        print("Start check content...")
        box_check = fetch_openai(model_check, client,
                                  f"""Analyze the following text and tell me if it is a short list of important points of infectious diseases. If it is, please answer me Yes. If not, please answer me No.
                                  
                                  {content_raw}""",
                                  "You are a language editing robot.",
                                  token, max_retries, delay)
        if "Yes" in box_check:
            break
        else:
            attempt += 1
            print(f"Retrying ({attempt}/{max_retries})...\n")
            print(f"box_check: {box_check}\n")
            print(f"box_content: {content_raw}\n")
    if attempt >= max_retries:
        print(f"Maximum retries reached. Failed to create response.")
        return None
    else:
        print(f"Response created successfully after {attempt} try.")
        return content_raw

def openai_key(model_create, model_check, user_content, token = 4096, max_retries=10, delay=1):
    """
    Fetches a response from the OpenAI API with automatic retries on failure.

    - model_create: The name of the model to use for the completion.
    - model_check: The name of the model to use for the check.
    - user_content: The content provided by the user for the completion.
    - token: The maximum number of tokens to generate.
    - max_retries: Maximum number of retries before giving up.
    - delay: Delay between retries in seconds.
    :return: The API response or None if all retries failed.
    """
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["OPENAI_API_BASE"],
    )

    attempt = 0
    print(f"Creating response for mail content...")
    while attempt < max_retries:
        print("Start generate raw content...")
        content_raw = fetch_openai(model_create, client,
                                   user_content,
                                   "You are a Prompt Creator.",
                                   token, max_retries, delay)
        print("Start check content...")
        box_check = fetch_openai(model_check, client,
                                  f"""Analyze the following text and tell me if it is a Prompt.
                                  If it is, please answer me Yes. If not, please answer me No.
                                  
                                  {content_raw}""",
                                  "You are a content check robot.",
                                  token, max_retries, delay)
        if "Yes" in box_check:
            break
        else:
            attempt += 1
            print(f"Retrying ({attempt}/{max_retries})...\n")
            print(f"box_check: {box_check}\n")
            print(f"box_content: {content_raw}\n")
    if attempt >= max_retries:
        print(f"Maximum retries reached. Failed to create response.")
        return None
    else:
        print(f"Response created successfully after {attempt} try.")
        return content_raw
    
def openai_image(model_create, user_content):
    """
    Fetches a response from the OpenAI API with automatic retries on failure.

    - model_create: The name of the model to use for the completion.
    - user_content: The content provided by the user for the completion.
    :return: The API response or None if all retries failed.
    """
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["OPENAI_API_BASE"],
    )

    attempt = 0
    print(f"Creating response for image content...")
    while attempt < 1:
        print("Start generate raw content...")
        response = client.images.generate(
          model=model_create,
          prompt=user_content,
          size="1024x1792",
          quality="standard",
          n=1,
        )
        url = response.data[0].url
        break
    if attempt >= 1:
        print(f"Maximum retries reached. Failed to create response.")
        return None
    else:
        print(f"Response created successfully after {attempt} try.")
        return url

def openai_analysis(model_create, model_check, user_content, token = 4096, max_retries=10, delay=1):
    """
    Fetches a response from the OpenAI API with automatic retries on failure.

    - model_create: The name of the model to use for the completion.
    - model_check: The name of the model to use for the check.
    - user_content: The content provided by the user for the completion.
    - token: The maximum number of tokens to generate.
    - max_retries: Maximum number of retries before giving up.
    - delay: Delay between retries in seconds.
    :return: The API response or None if all retries failed.
    """
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["OPENAI_API_BASE"],
    )

    attempt = 0
    print(f"Creating response for analysis...")
    while attempt < max_retries:
        print("Start generate raw content...")
        content_raw = fetch_openai(model_create, client,
                                   user_content,
                                    "You are a epidemiologist.",
                                   token, max_retries, delay)
        print("Start check content...")
        # print(content_raw)
        # box_check = fetch_openai(model_check, client,
        #                         f"""Analyze the following text and tell me if it is the analysis of infectious diseases. If it is, please answer me Yes. If not, please answer me No.
                                
        #                         {content_raw}""",
        #                         "You are a language editing robot.",
        #                         token, max_retries, delay)
        box_check = 'Yes'
        if "Yes" in box_check:
            break
        else:
            attempt += 1
            print(f"Retrying ({attempt}/{max_retries})...\n")
            print(f"box_check: {box_check}\n")
            print(f"box_content: {content_raw}\n")
    if attempt >= max_retries:
        print(f"Maximum retries reached. Failed to create response.")
        return None
    else:
        print(f"Response created successfully after {attempt} try.")
        return content_raw

def bing_analysis(model_create, model_clean, model_check, user_content, max_retries=10, delay=1):
    """
    Fetches a response from the OpenAI API with automatic retries on failure.

    - model_create: The name of the model to use for the completion.
    - model_clean: The name of the model to use for the clean.
    - model_check: The name of the model to use for the check.
    - user_content: The content provided by the user for the completion.
    - max_retries: Maximum number of retries before giving up.
    - delay: Delay between retries in seconds.
    :return: The API response or None if all retries failed.
    """
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["OPENAI_API_BASE"],
    )

    attempt = 0
    print(f"Creating response from news...")
    while attempt < max_retries:
        print("Start generate raw content...")
        content_raw = fetch_google(model_create, client,
                                  user_content,
                                  "You are a epidemiologist.",
                                  max_retries, delay)
        content_raw = fetch_google(model_clean, client,
                                  f"""Clean the following text and generate a new summary using below format:
                                  <b>Summary</b>:
                                  (Provide an overall summary of the infectious disease events)
                                  <b>Outbreaks of Known Diseases:</b>
                                  (Detail the outbreaks of known diseases during this period)
                                  <b>Emergence of Novel Pathogens:</b>
                                  (Discuss any new pathogens that have emerged)

                                  This is content you need to clean:
                                  {content_raw}""",
                                  "You are a epidemiologist.",
                                  max_retries, delay)
        print("Start check content...")
        box_check = fetch_google(model_check, client,
                                f"""Analyze the following text and tell me if it is the analysis of infectious diseases, contains summary section and reference section. If it is, please answer me Yes. If not, please answer me No.
                                
                                {content_raw}""",
                                "You are a language editing robot.",
                                max_retries, delay)
        if "Yes" in box_check:
            # content_raw = content_raw.split("<h3>Summary:</h3>")[1]
            break
        else:
            attempt += 1
            print(f"Retrying ({attempt}/{max_retries})...\n")
            print(f"box_check: {box_check}\n")
            print(f"box_content: {content_raw}\n")
    if attempt >= max_retries:
        print(f"Maximum retries reached. Failed to create response.")
        return None
    else:
        print(f"Response created successfully after {attempt} try.")
        return content_raw

def fetch_google(model, client, user_content, role, max_retries=10, delay=1):
    """
    Fetches a response from the OpenAI API with automatic retries on failure.

    - model: The name of the model to use for the completion.
    - client: OpenAI client contains api_key and base_url.
    - user_content: The content provided by the user for the completion.
    - disease: The disease of the report.
    - token: The maximum number of tokens to generate.
    - max_retries: Maximum number of retries before giving up.
    - delay: Delay between retries in seconds.
    :return: The API response or None if all retries failed.
    """
    attempt = 0

    while attempt < max_retries:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": role},
                    {"role": "user", "content": user_content}
                ]
            )
            generated_text = response.choices[0].message.content
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            try:
                print(response)
            except:
                print("No response")
            attempt += 1
            time.sleep(delay)
            print(f"Retrying ({attempt}/{max_retries})...")

    if attempt >= max_retries:
        print("Maximum retries reached. Failed to fetch response.")
        return None
    else:
        print(f"Response fetched successfully after {attempt} try.")
        return generated_text

def fetch_openai(model, client, user_content, role, token = 500, max_retries=10, delay=1):
    """
    Fetches a response from the OpenAI API with automatic retries on failure.

    - model: The name of the model to use for the completion.
    - client: OpenAI client contains api_key and base_url.
    - user_content: The content provided by the user for the completion.
    - disease: The disease of the report.
    - token: The maximum number of tokens to generate.
    - max_retries: Maximum number of retries before giving up.
    - delay: Delay between retries in seconds.
    :return: The API response or None if all retries failed.
    """
    attempt = 0

    while attempt < max_retries:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": role},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=token
            )
            generated_text = response.choices[0].message.content
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            try:
                print(response)
            except:
                print("No response")
            attempt += 1
            time.sleep(delay)
            print(f"Retrying ({attempt}/{max_retries})...")

    if attempt >= max_retries:
        print("Maximum retries reached. Failed to fetch response.")
        return None
    else:
        print(f"Response fetched successfully after {attempt} try.")
        return generated_text

def update_markdown_file(disease, section, content, analysis_YearMonth):
    """
    Updates the specified section of the Markdown file for the given disease. If the section does not exist, it is created.

    - disease: The name of the disease, which determines the Markdown file name.
    - section: The section of the Markdown file to update.
    - content: The new content to write to the section.
    """
    file_name = f"../Report/history/{analysis_YearMonth}/{disease}.md"
    section_header = f"## {section}"
    new_content = f"{section_header}\n\n{content}\n"
    section_found = False

    # if not exist create folder
    os.makedirs(f"../Report/history/{analysis_YearMonth}", exist_ok=True)

    try:
        with open(file_name, 'r+') as file:
            lines = file.readlines()
            file.seek(0)
            in_section = False
            for line in lines:
                if line.strip() == section_header:
                    file.write(new_content)
                    in_section = True
                    section_found = True
                elif line.startswith("## ") and in_section:
                    in_section = False
                if not in_section:
                    file.write(line)
            file.truncate()
            # If the section was not found, add it to the end of the file
            if not section_found:
                file.write("\n" + new_content)
    except FileNotFoundError:
        # If the file does not exist, create it with the section content
        with open(file_name, 'w') as file:
            file.write(new_content)
    except Exception as e:
        print(f"An error occurred while updating the Markdown file: {e}")

# table_data_str = table_data.to_markdown(index=False)
# analysis_content = openai_analysis('gpt-4-32k', 'gpt-3.5-turbo',
#                                   f"""Analyze the monthly cases and deaths of different diseases in mainland China for {analysis_MonthYear}. Provide a deeply and comprehensive analysis of the data.
#                                   You need to pay attention: select noteworthy diseases, not all diseases and using below format:
#                                   <b>disease name:</b> analysis content. <br/><br/> <b>disease name:</b> analysis content. <br/><br/> .....
                                  
#                                   This the data for {analysis_MonthYear} in mainland, China:
#                                   {table_data_str}""",
#                                   4096)
# analysis_content = markdown.markdown(analysis_content)