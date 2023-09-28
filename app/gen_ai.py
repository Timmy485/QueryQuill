import pandas as pd
import json
import replicate
import os

path = os.path.dirname(__file__)
json_path = path+'/config.json'
with open(json_path, 'r') as config_file:
    config_data = json.load(config_file)
api_key = config_data.get('REPLICATE_API_TOKEN')



def generate_direct_answer_with_llama(search_results, user_query = "what is a valid offer?", save_csv=True):
    rep = replicate.Client(api_token=api_key)
    passages = ''

    if save_csv:
        df = pd.read_csv('../docs/questions_answers.csv', encoding='ISO-8859-1')
        # Extract passages and concatenate them to form a single passage
        passage_columns = [col for col in df.columns if "Passage" in col and "Metadata" not in col]
        combined_passages = df[passage_columns].apply(lambda row: ' '.join(row.dropna()), axis=1)
        passages = "".join(combined_passages)
    else:
        passages = [hit["_source"]["Passage"] for hit in search_results]

    prompt = f"""
        Use the following pieces of passages to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer. 
        Use three sentences maximum and keep the answer as concise as possible. 
        Only answer from the passages
        Passages: {' '.join(passages)}
        Question: {user_query}
    """


    output = rep.run(
        "meta/llama-2-70b-chat:2c1608e18606fad2812020dc541930f2d0495ce32eee50074220b87300bc16e1",
        input={"prompt": prompt},
        temperature = 0.1,
        seed = 0
    )

    out = ""
    for item in output:
        out += "".join(item)

    if save_csv:
        df['Generative AI Answer'] = out
        df.to_csv('../docs/questions_answers.csv', index=False)
    return out