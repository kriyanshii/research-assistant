# Research Assistant

## Ask Relevant Questions to Get Relevent Answers!

## The Product

We have designed an aid for the everyday researcher and knowledge gatherer. You never have to comb through a sea of text trying to find that one statistic, that one conclusion that can win you an argument or complete your citation. Just plug those lengthy pdfs into this tool and ask questions to your very own research assistant (at a salary: Rs. 0/hr impressive, right?).

A user can upload a number of well-formatted (mostly plaintext) PDFs. This tool is focused on research papers due to their standard format, making it very easy to extract text. Also, the need for such a tool is greater because research papers tend to have a lot of data and sifting through many research papers to obtain data related to a query can become tedious.

## Usecases

### Utilise documents without actually reading them!

Anything that requires a big knowledge base and can benefit from semantic search nad finding answers to non specific queries.
Example:

- Add user manuals to the knowledge base and instantly know the answer to why there is an orange light blinking away
- Upload research papers and find immediate answers to your questions.

## Under the hood

Text is extracted from the uploaded PDFs and cleaned such that each piece of text contains information such that minimum outside context is needed. A vector is created from this text using a process known as embedding.

The text - approximately 40-200 words in length, is embedded using a sentence transformer model. This basically encodes the text data into hundreds of dimensions of vector space so that it can be denoted using numbers. These dense vectors are stored in an index in a vector database.

We have created two approaches for this. A local approach uses a fairly performant and cost effective model (can produce accurate and swift results without a GPU) and uses dot product as a similarity metric.
This model was chosen after careful deliberation due to the following factors:

- Best SBERT model in terms of performance
- High output vector size (768 dimensions)
- Based on the microsoft mpnet model and then trained on 215M+ question-answer samples from various sources.
- Cost effective

The second approach uses the OpenAI embeddings API and creates a 1536 dimension dense vector, offloading demanding tasks to remote servers. This uses a cosine similarity metric.

Whenever the user asks a question, it is converted into a vector using the _same_ embedding model. The order of similarity metrics between vectors in the knowledge base and query vector provide relevance. Text metadata from the top three vectors with highest similarity are further used as a context into the large language model powered completions API by OpenAI which provides a great human-readable answer.

## Competitors

There are currently no large scale competitors to this product. Despite appearances, summarization tools (even those harnessing the power of AI) are vastly different from this product.

Indirect competitors AI summary tools: scholarcy, paper-digest

## Potential Improvements

<hr />

1. Better support for images, tables, mathematical formulas and non-english alphabets (can be attained by modifying the corpus reader function).

2. Users can have a dedicated storage for all their documents and can provide easy retrieval, also providing category based indexes (unfortunately, this functionality can <!-- only exist in a revenue generating product/ -->increase cost dramatically).

3. A more advanced system can be easily engineered from this point that can highlight and annotate (from GPT's completion answer), the original sources.

4. A chrome extension that can add any text you select to this knowledge database. So, the next time you find any information that you would like to use in the future, select and click.

5. Next gen storage for the user's life data. Imagine a product that is so tightly integrated with your devices that any text you see/any conversation you have can be transcribed and saved as a vector. Instead of asking yourself "What did she say?" you can ask your virtual personal assistant.
   Major obstacles:

- Maintaining privacy
- Integration with all personal devices of the user

Link to google colab (used for testing) - https://colab.research.google.com/drive/1FQqfs4N5aeqiuv_EMNdSOj50UCD_PuBA?usp=sharing

## Deployments

Multiple deployments ensure zero downtime even when on free tiers ;)

<a href="https://researchgpt-grs5.onrender.com/">Render</a>
<br />
<a href="https://research-assistant-production.up.railway.app/">Railway</a>
<br />
<a href="http://ec2-13-233-118-234.ap-south-1.compute.amazonaws.com/">AWS</a>

> This project was made during the course of the stranger hacks event by devfolio with the objective to develop a web app that can provide proof of concept and basic functionality. Development of a more robust and feature rich version of this project is to continue post the hackathon.
