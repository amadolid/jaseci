import openai
from os import environ, unlink
from datetime import datetime
from requests import get
from uuid import uuid4

from .utils import extract_text_from_file, get_embeddings, generate_chunks
from jaseci.jsorc.live_actions import jaseci_action
from elasticsearch import Elasticsearch, NotFoundError

CLIENT = None
CONFIG = {
    "elastic": {
        "url": environ.get("ELASTICSEARCH_URL", "http://localhost:9200"),
        "key": environ.get("ELASTICSEARCH_API_KEY"),
        "index_template": {
            "name": environ.get("ELASTICSEARCH_INDEX_TEMPLATE") or "openai-embeddings",
            "index_patterns": (
                environ.get("ELASTICSEARCH_INDEX_PATTERNS") or "oai-emb-*"
            ).split(","),
            "priority": 500,
            "version": 1,
            "template": {
                "settings": {
                    "number_of_shards": int(environ.get("ELASTICSEARCH_SHARDS", "1")),
                    "number_of_replicas": int(
                        environ.get("ELASTICSEARCH_REPLICAS", "1")
                    ),
                    "refresh_interval": "1s",
                },
                "mappings": {
                    "_source": {"enabled": True},
                    "properties": {
                        "id": {"type": "keyword"},
                        "embedding": {
                            "type": "dense_vector",
                            "dims": int(
                                environ.get("ELASTICSEARCH_VECTOR_SIZE", "1536")
                            ),
                            "index": True,
                            "similarity": environ.get(
                                "ELASTICSEARCH_SIMILARITY", "cosine"
                            ),
                        },
                        "version": {"type": "keyword"},
                    },
                },
            },
        },
    },
    "openai": {
        "key": openai.api_key,
        "type": openai.api_type,
        "base": openai.api_base,
        "version": openai.api_version,
        "embedding": {
            "deployment_id": environ.get("OPENAI_EMBEDDING_DEPLOYMENT_ID"),
            "model": environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002"),
        },
    },
    "chunk_config": {
        "chunk_size": environ.get("CHUNK_SIZE", 200),
        "min_chunk_size_chars": environ.get("MIN_CHUNK_SIZE_CHARS", 350),
        "min_chunk_length_to_embed": environ.get("MIN_CHUNK_LENGTH_TO_EMBED", 5),
        "max_num_chunks": environ.get("MAX_NUM_CHUNKS", 10000),
    },
    "batch_size": int(environ.get("ELASTICSEARCH_UPSERT_BATCH_SIZE", "100")),
}


@jaseci_action(allow_remote=True)
def setup(config: dict = CONFIG, rebuild: bool = False, reindex_template: bool = False):
    """ """
    global CONFIG, CLIENT
    CONFIG = config

    if rebuild:
        CLIENT = None

    if reindex_template:
        reapply_index_template()

    openai_config = CONFIG["openai"]
    openai.api_key = openai_config.get("key") or openai.api_key
    openai.api_type = openai_config.get("type") or openai.api_type
    openai.api_base = openai_config.get("base") or openai.api_base
    openai.api_version = openai_config.get("version") or openai.api_version


@jaseci_action(allow_remote=True)
def upsert(index: str, data: dict, reset: bool = False, refresh=None, meta: dict = {}):
    """ """
    bs = CONFIG["batch_size"]

    doc_u = data.get("url", [])
    doc_t = data.get("text", [])

    # only works if not remote
    doc_f = data.get("file", [])

    if reset:
        reset_index(index)
    else:
        delete(index, [doc["id"] for doc in doc_t] + [doc["id"] for doc in doc_u])

    doc_a = []
    for doc in doc_u:
        file_name: str = "/tmp/" + (doc.pop("name", None) or str(uuid4()))
        with get(doc.pop("url"), stream=True) as res, open(file_name, "wb") as buffer:
            res.raise_for_status()
            for chunk in res.iter_content(chunk_size=8192):
                buffer.write(chunk)

        doc["text"] = extract_text_from_file(file_name)

        unlink(file_name)
        doc_a += generate_chunks(doc, CONFIG["chunk_config"])

    for doc in doc_t:
        doc_a += generate_chunks(doc, CONFIG["chunk_config"])

    hook = meta.get("h")
    if hasattr(hook, "get_file_handler"):
        for doc in doc_f:
            fh = hook.get_file_handler(doc["file"])
            doc["text"] = extract_text_from_file(fh.absolute_path)
            doc_a += generate_chunks(doc, CONFIG["chunk_config"])

    ops_index = {"index": {"_index": index}}
    ops_t = []
    for docs in [doc_a[x : x + bs] for x in range(0, len(doc_a), bs)]:
        for i, emb in enumerate(
            get_embeddings([doc["text"] for doc in docs], CONFIG["openai"])
        ):
            docs[i]["embedding"] = emb
            docs[i]["created_time"] = int(
                datetime.fromisoformat(docs[i]["created_time"]).timestamp()
            )
            ops_t.append(ops_index)
            ops_t.append(docs[i])

    elastic().bulk(operations=ops_t, index=index, refresh=refresh)

    return True


@jaseci_action(allow_remote=True)
def delete(index: str, ids: [], all: bool = False):
    """ """
    if all:
        return reset_index(index)
    elif ids:
        return (
            elastic()
            .delete_by_query(
                index=index,
                query={"terms": {"id": ids}},
                ignore_unavailable=True,
            )
            .body
        )


@jaseci_action(allow_remote=True)
def query(index: str, data: list):
    """ """
    bs = CONFIG["batch_size"]

    search_index = {"index": index}
    searches = []
    for queries in [data[x : x + bs] for x in range(0, len(data), bs)]:
        for i, emb in enumerate(
            get_embeddings([query["query"] for query in queries], CONFIG["openai"])
        ):
            top = queries[i].get("top") or 3
            query = {
                "knn": {
                    "field": "embedding",
                    "query_vector": emb,
                    "k": top,
                    "num_candidates": queries[i].get("num_candidates") or (top * 10),
                    "filter": queries[i].get("filter") or [],
                }
            }

            min_score = queries[i].get("min_score")
            if min_score:
                query["min_score"] = min_score

            searches.append(search_index)
            searches.append(query)

    return [
        {
            "query": query,
            "results": [
                {
                    "id": hit["_source"]["id"],
                    "text": hit["_source"]["text"],
                    "score": hit["_score"],
                }
                for hit in result["hits"]["hits"]
            ],
        }
        for query, result in zip(
            queries,
            elastic().msearch(searches=searches, ignore_unavailable=True)["responses"],
        )
    ]


@jaseci_action(allow_remote=True)
def reset_index(index: str):
    return elastic().indices.delete(index=index, ignore_unavailable=True).body


@jaseci_action(allow_remote=True)
def reapply_index_template():
    """ """
    index_template = CONFIG["elastic"]["index_template"]
    try:
        return elastic().indices.get_index_template(name=index_template["name"]).body
    except NotFoundError:
        return elastic().indices.put_index_template(**index_template).body


def elastic() -> Elasticsearch:
    global CONFIG, CLIENT
    if not CLIENT:
        config = CONFIG.get("elastic")
        try:
            client = Elasticsearch(
                hosts=[config["url"]],
                api_key=config["key"],
                request_timeout=config.get("request_timeout"),
            )
            client.info()
            CLIENT = client
        except Exception as e:
            raise e
    return CLIENT
