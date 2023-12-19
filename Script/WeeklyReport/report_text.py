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

    attempt = 0
    while attempt < max_retries:
        box_content = fetch_openai_single(model_create, client,
                                            user_content, section, disease,
                                            token, max_retries, delay)
        box_check = check_openai_single(model_check, client,
                                          f"""Analyze the following text and tell me if it is the {section} section to {disease} analysis report. If it is, please answer me Yes. If not, please answer me No.
                                          
                                          {box_content}""",
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

def fetch_openai_single(model, client, user_content, section, disease, token = 500, max_retries=10, delay=1):
    """
    Fetches a response from the OpenAI API with automatic retries on failure.

    - model: The name of the model to use for the completion.
    - client: OpenAI client contains api_key and base_url.
    - user_content: The content provided by the user for the completion.
    - section: The section of the report.
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
                    {"role": "system", "content": "You are a epidemiologist."},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=token
            )
            generated_text = response.choices[0].message.content
            update_markdown_file(disease, section, generated_text)
            break
        except Exception as e:
            print(f"{disease}\nAn error occurred: {e}")
            attempt += 1
            time.sleep(delay)
            print(f"{disease}\nRetrying ({attempt}/{max_retries})...")

    if attempt >= max_retries:
        print(f"{disease} {section}\nMaximum retries reached. Failed to fetch response.")
        return None
    else:
        print(f"{section} of {disease}: Response fetched successfully after {attempt} try.")
        return generated_text

def check_openai_single(model, client, user_content, token = 500, max_retries=10, delay=1):
    """
    Check the response from the OpenAI.

    - model: The name of the model to use for the completion.
    - user_content: The content provided by the user for the completion.
    - token: The maximum number of tokens to generate.
    - max_retries: Maximum number of retries before giving up.
    - delay: Delay between retries in seconds.
    :return: The API response or None if all retries failed.
    """
    attempt = 0
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["OPENAI_API_BASE"],
    )

    while attempt < max_retries:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a language editing robot."},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=token
            )
            generated_text = response.choices[0].message.content
            break
        except Exception as e:
            print(f"An error occurred: {e}\n")
            attempt += 1
            time.sleep(delay)
            print(f"Retrying ({attempt}/{max_retries})...")

    if attempt >= max_retries:
        print(f"Maximum retries reached. Failed to check response.")
        return None
    else:
        print(f"Response checked successfully after {attempt} try.")
        return generated_text

def update_markdown_file(disease, section, content):
    """
    Updates the specified section of the Markdown file for the given disease. If the section does not exist, it is created.

    - disease: The name of the disease, which determines the Markdown file name.
    - section: The section of the Markdown file to update.
    - content: The new content to write to the section.
    """
    file_name = f"../../Report/information/{disease}.md"
    section_header = f"## {section}"
    new_content = f"{section_header}\n\n{content}\n"
    section_found = False

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

def openai_month(model_create, model_check, user_content, token = 500, max_retries=10, delay=1):
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
    while attempt < max_retries:
        content_raw = fetch_openai_month(model_create, client,
                                         user_content,
                                         token, max_retries, delay)
        box_check = check_openai_month(model_check, client,
                                       f"""Analyze the following text and tell me if it is deeply and comprehensive analysis of infectious diseases. If it is, please answer me Yes. If not, please answer me No.
                                       
                                       {content_raw}""",
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
                  
def fetch_openai_month(model, client, user_content, token = 500, max_retries=10, delay=1):
    """
    Fetches a response from the OpenAI API with automatic retries on failure.

    - model: The name of the model to use for the completion.
    - client: OpenAI client contains api_key and base_url.
    - user_content: The content provided by the user for the completion.
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
                    {"role": "system", "content": "You are a epidemiologist."},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=token
            )
            generated_text = response.choices[0].message.content
            break
        except Exception as e:
            print(f"Monthly summary An error occurred: {e}")
            attempt += 1
            time.sleep(delay)
            print(f"Monthly summary Retrying ({attempt}/{max_retries})...")

    if attempt >= max_retries:
        print("Monthly summary: Maximum retries reached. Failed to fetch response.")
        return None
    else:
        print(f"Monthly summary: Response fetched successfully after {attempt} try.")
        return generated_text

def check_openai_month(model, client, user_content, token = 500, max_retries=10, delay=1):
    """
    Check the response from the OpenAI.

    - model: The name of the model to use for the completion.
    - user_content: The content provided by the user for the completion.
    - token: The maximum number of tokens to generate.
    - max_retries: Maximum number of retries before giving up.
    - delay: Delay between retries in seconds.
    :return: The API response or None if all retries failed.
    """
    attempt = 0
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["OPENAI_API_BASE"],
    )

    while attempt < max_retries:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a language editing robot."},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=token
            )
            generated_text = response.choices[0].message.content
            break
        except Exception as e:
            print(f"Monthly summary An error occurred: {e}\n")
            attempt += 1
            time.sleep(delay)
            print(f"Monthly summary Retrying ({attempt}/{max_retries})...")

    if attempt >= max_retries:
        print(f"Monthly summary Maximum retries reached. Failed to check response.")
        return None
    else:
        print(f"Monthly summary Response checked successfully after {attempt} try.")
        return generated_text
    
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
    while attempt < max_retries:
        content_raw = fetch_openai_analysis(model_create, client,
                                            user_content,
                                            token, max_retries, delay)
        box_check = check_openai_analysis(model_check, client,
                                          f"""Analyze the following text and tell me if it is the analysis of infectious diseases. If it is, please answer me Yes. If not, please answer me No.
                                          
                                          {content_raw}""",
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
    
def fetch_openai_analysis(model, client, user_content, token = 500, max_retries=10, delay=1):
    """
    Fetches a response from the OpenAI API with automatic retries on failure.

    - model: The name of the model to use for the completion.
    - client: OpenAI client contains api_key and base_url.
    - user_content: The content provided by the user for the completion.
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
                    {"role": "system", "content": "You are a epidemiologist."},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=token
            )
            generated_text = response.choices[0].message.content
            break
        except Exception as e:
            print(f"Analysis An error occurred: {e}")
            attempt += 1
            time.sleep(delay)
            print(f"Analysis Retrying ({attempt}/{max_retries})...")

    if attempt >= max_retries:
        print("Analysis: Maximum retries reached. Failed to fetch response.")
        return None
    else:
        print(f"Analysis: Response fetched successfully after {attempt} try.")
        return generated_text
    
def check_openai_analysis(model, client, user_content, token = 500, max_retries=10, delay=1):
    """
    Check the response from the OpenAI.

    - model: The name of the model to use for the completion.
    - user_content: The content provided by the user for the completion.
    - token: The maximum number of tokens to generate.
    - max_retries: Maximum number of retries before giving up.
    - delay: Delay between retries in seconds.
    :return: The API response or None if all retries failed.
    """
    attempt = 0
    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["OPENAI_API_BASE"],
    )

    while attempt < max_retries:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a language editing robot."},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=token
            )
            generated_text = response.choices[0].message.content
            break
        except Exception as e:
            print(f"Analysis An error occurred: {e}\n")
            attempt += 1
            time.sleep(delay)
            print(f"Analysis Retrying ({attempt}/{max_retries})...")

    if attempt >= max_retries:
        print(f"Analysis Maximum retries reached. Failed to check response.")
        return None
    else:
        print(f"Analysis Response checked successfully after {attempt} try.")
        return generated_text
