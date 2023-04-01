from sentence_transformers import SentenceTransformer
from tqdm.auto import tqdm
from PyPDF2 import PdfReader
import pinecone, openai
import re, os, shutil


def init(queryText):
    model = SentenceTransformer('sentence-transformers/multi-qa-mpnet-base-dot-v1')

    ### CAN USE ENVIRONMENT VARIABLES FOR THIS
    openai.api_key = ""
    pinecone.init(
        api_key='26d1b4b3-00e8-4565-8a2f-9874758426f4',
        environment='eu-west1-gcp',
    )
    index_name = 'user-index-nimit'
    ###

    if index_name not in pinecone.list_indexes():
      pinecone.create_index(
          index_name,
          dimension=768,
          metric='dotproduct',
          metadata_config={'indexed': []}
      )

    ## GET INDEX
    index = pinecone.Index(index_name)
    print(index.describe_index_stats())
    
    for filename in os.listdir('data'):
      total_vectors = index.describe_index_stats()['total_vector_count']
      f = filename.split('.')
      title = ''.join(f[:-1])
      if(f[-1] != 'pdf'):
         raise NotImplementedError

      path = f'data/{filename}'
      sentences = getCorpus(path)
      shutil.move(path, 'used_data')
      
      print(f'Vectors for {title}:', len(sentences))

      ids = list(map(str, [*range(total_vectors, total_vectors + len(sentences))]))
      embeds = [model.encode(sentence, convert_to_numpy=True).tolist() for sentence in sentences] # type: ignore
      meta = [{'title': title, 'text': sentence} for sentence in sentences]

      to_upsert = list(zip(ids, embeds, meta))

      # print(to_upsert[0])

      index.upsert(vectors=to_upsert)
    
    # query = 'question answering capability of gpt-2'
    query = queryText
    qv = model.encode(query).tolist() # type: ignore

    completionResult = index.query(qv, top_k=3, include_metadata=True)
    # print(res)
    
    contexts = [x['metadata']['text'] for x in completionResult['matches']]
    prompt_start = (
        "Answer the question based on the context below.\n\n"+
        "Context:\n"
    )
    prompt_end = (
        f"\n\nQuestion: {query}\nAnswer:"
    )
    prompt = ''
    limit = 3750
    for i in range(1, len(contexts)):
        if len("\n\n---\n\n".join(contexts[:i])) >= limit:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(contexts[:i-1]) +
                prompt_end
            )
            break
        elif i == len(contexts)-1:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(contexts) +
                prompt_end
            )

    # print(prompt)
    # return prompt

    completionResult = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        temperature=0,
        max_tokens=400,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    ans = completionResult['choices'][0]['text'].strip() # type: ignore
    print('*********************************************************')
    # print(ans)
    return ans




def getCorpus(path):
    pdf_file = open(path, 'rb')
    pdf_reader = PdfReader(pdf_file)
    num_pages = len(pdf_reader.pages)

    text = ''
    for i in range(num_pages):
        page = pdf_reader.pages[i]
        text += page.extract_text()

    pdf_file.close()

    text = text.lower()
    text = text.replace('-\n', '')
    sentences = re.split(r'\.\n', text.split('references\n')[0])

    for i in range(len(sentences)):
      sentences[i] = re.sub(r'[^ -~]', ' ', sentences[i])

    for s in sentences:
      if len(s) < 10:
        sentences.remove(s)
    return sentences


if __name__ == '__main__':
    init()
