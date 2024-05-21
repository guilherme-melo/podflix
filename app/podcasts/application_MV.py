import docker
from vespa.io import VespaResponse, VespaQueryResponse
from vespa.package import (
    ApplicationPackage,
    Field,
    Schema,
    Document,
    HNSW,
    RankProfile,
    Component,
    Parameter,
    FirstPhaseRanking,
    SecondPhaseRanking,
    FieldSet,
    GlobalPhaseRanking,
    Function,
)
from vespa.deployment import VespaDocker
import pandas as pd

class VespaAppMV:
    def __init__(self):
        self.docker_check()
        self.app = self.start_vespa()


    def docker_check(self):
        # tava tendo problema de deixar salvo e ficar rodando e ficar duplicando dados
        client = docker.from_env()
        if 'podflix' in [container.name for container in client.containers.list()]:
            container = client.containers.get('podflix')
            container.stop()  
            container.remove()  


    def create_application(self):
        package = ApplicationPackage(
            name="podflix",
            schema=[
                Schema(
                    name="doc",
                    document=Document(
                        fields=[
                            Field(name="id", type="string", indexing=["summary"]),
                            Field(
                                name="title",
                                type="string",
                                indexing=["index", "summary"],
                                index="enable-bm25",
                            ),
                            Field(
                                name="description",
                                type="string",
                                indexing=["index", "summary"],
                                index="enable-bm25",
                                bolding=True,
                            ),
                            Field(
                                name="lines",
                                type="array<string>",
                                indexing=["index", "summary"],
                                index="enable-bm25",
                                bolding=True,
                            ),
                            Field(
                                name="line_embeddings",
                                type="tensor<float>(p{}, x[384])",
                                indexing=[
                                    "input lines",
                                    "embed",
                                    "index",
                                    "attribute",
                                ],
                                ann=HNSW(distance_metric="angular"),
                                is_document_field=False,
                            ),
                            # Field(
                            #     name="embedding",
                            #     type="tensor<float>(p{}, x[384])",
                            #     indexing=[
                            #         'input title . " " . input description . " " . input lines',
                            #         "embed",
                            #         "index",
                            #         "attribute",
                            #     ],
                            #     ann=HNSW(distance_metric="angular"),
                            #     is_document_field=False,
                            # ),
                        ]
                    ),
                    fieldsets=[
                        FieldSet(name="default", fields=["title", "description","lines"])
                    ],
                    rank_profiles=[
                        RankProfile(
                            name="bm25",
                            inputs=[("query(q)", "tensor<float>(x[384])")],
                            functions=[
                                Function(name="bm25sum", expression="bm25(title) + bm25(description) + bm25(lines)")
                            ],
                            first_phase="bm25sum",
                        ),
                        RankProfile(
                            name="semantic",
                            inputs=[("query(q)", "tensor<float>(x[384])")],
                            inherits="default",
                            first_phase="cos(distance(field,line_embeddings))",
                            match_features=["closest(line_embeddings)"],
                        ),
                        # RankProfile(
                        #     name="fusion",
                        #     inherits="bm25",
                        #     inputs=[("query(q)", "tensor<float>(x[384])")],
                        #     first_phase="closeness(field, line_embeddings)",
                        #     global_phase=GlobalPhaseRanking(
                        #         expression="reciprocal_rank_fusion(bm25sum, closeness(field, line_embeddings))",
                        #         rerank_count=1000,
                        #     ),
                        # ),
                        RankProfile(
                            name="hybrid",
                            inherits="semantic",
                            functions=[
                                Function(
                                    name="avg_line_similarity",
                                    expression="""reduce(
                                                sum(l2_normalize(query(q),x) * l2_normalize(attribute(line_embeddings),x),x),
                                                avg,
                                                p
                                            )""",
                                ),
                                Function(
                                    name="max_line_similarity",
                                    expression="""reduce(
                                                sum(l2_normalize(query(q),x) * l2_normalize(attribute(line_embeddings),x),x),
                                                max,
                                                p
                                            )""",
                                ),
                                Function(
                                    name="all_line_similarities",
                                    expression="sum(l2_normalize(query(q),x) * l2_normalize(attribute(line_embeddings),x),x)",
                                ),
                            ],
                            first_phase=FirstPhaseRanking(
                                expression="cos(distance(field,line_embeddings))"
                            ),
                            second_phase=SecondPhaseRanking(
                                expression="firstPhase + avg_line_similarity() + log( bm25(title) + bm25(lines) + bm25(description))"
                            ),
                            match_features=[
                                "closest(line_embeddings)",
                                "firstPhase",
                                "bm25(title)",
                                "bm25(description)",
                                "bm25(lines)",
                                "avg_line_similarity",
                                "max_line_similarity",
                                "all_line_similarities",
                            ],
                        )
                    ],
                )
            ],
            components=[
                Component(
                    id="e5",
                    type="hugging-face-embedder",
                    parameters=[
                        Parameter(
                            "transformer-model",
                            {
                                "url": "https://github.com/vespa-engine/sample-apps/raw/master/simple-semantic-search/model/e5-small-v2-int8.onnx"
                            },
                        ),
                        Parameter(
                            "tokenizer-model",
                            {
                                "url": "https://raw.githubusercontent.com/vespa-engine/sample-apps/master/simple-semantic-search/model/tokenizer.json"
                            },
                        ),
                    ],
                )
            ],
        )

        return package


    def deploy_vespa(self):
        package = self.create_application()

        vespa_docker = VespaDocker()
        app = vespa_docker.deploy(application_package=package)

        return app


    def transform_row(self, row):
        return {
            "id": row['episode'],
            "fields": {
                "title": row['title'],
                "description": row['description'],
                "lines": row['transcript'].split('\n'),
                "id": row['episode']
            }
        }


    def callback(self, response:VespaResponse, id:str):
        if not response.is_successful():
            print(f"Error when feeding document {id}: {response.get_json()}")


    def hits_as_df(self, response:VespaQueryResponse, fields) -> pd.DataFrame:
        records = []
        for hit in response.hits:
            record = {}
            for field in fields:
                record[field] = hit['fields'][field]
            records.append(record)
        return pd.DataFrame(records)


    def start_vespa(self):
        data = pd.read_csv('app/podcasts/data/transcribed_podcasts.csv') # TODO: change to read from sqlite3
        data = data.head(5) # LIMITANDO POR CAPACIDADE COMPUTACIONAL 
        
        vespa_feed = data.apply(self.transform_row, axis=1).tolist()

        app = self.deploy_vespa()
        app.feed_iterable(vespa_feed, schema="doc", namespace="podflix", callback=self.callback)

        return app


    # def query_bm25(self, input_query):
    #     with self.app.syncio(connections=1) as session:
    #             query = input_query
    #             response:VespaQueryResponse = session.query(
    #                 yql="select * from sources * where userQuery() limit 10",
    #                 query=query,
    #                 ranking="bm25"
    #             )
    #             assert(response.is_successful())

    #     return self.hits_as_df(response, ['id', 'title'])

    # def query_semantic(self, input_query):
    #     with self.app.syncio(connections=1) as session:
    #         query = input_query
    #         response: VespaQueryResponse = session.query(
    #             yql="select * from sources * where ({targetHits:1000}nearestNeighbor(line_embeddings,q)) limit 10",
    #             query=query,
    #             ranking="semantic",
    #             body={"input.query(q)": f"embed({query})"},
    #         )
    #         assert response.is_successful()

    #     return self.hits_as_df(response, ['id', 'title'])
    
    # def query_fusion(self, input_query):
    #     with self.app.syncio(connections=1) as session:
    #         query = input_query
    #         response: VespaQueryResponse = session.query(
    #             yql="select * from sources * where userQuery() or ({targetHits:1000}nearestNeighbor(line_embeddings,q)) limit 10",
    #             query=query,
    #             ranking="fusion",
    #             body={"input.query(q)": f"embed({query})"},
    #         )
    #         assert response.is_successful()

    #     return self.hits_as_df(response, ["id", "title"])    


    def query_MV_bm25(self, input_query, return_df = True):
        with self.app.syncio(connections=1) as session:
            query = input_query
            response: VespaQueryResponse = session.query(
                yql="select * from sources * where userQuery() ",
                query=query,
                ranking="bm25",
                model="bm25",
            )
            assert response.is_successful()
        
        if return_df:
            return self.hits_as_df(response, ['id', 'title'])
        else:
            return response


    def query_MV_semantic(self, input_query, return_df = True):
        with self.app.syncio(connections=1) as session:
            query = input_query
            response: VespaQueryResponse = session.query(
                yql="select * from sources * where ({targetHits:1000}nearestNeighbor(line_embeddings,q)) ",
                query=query,
                ranking="semantic",
                model="semantic",
                body={"input.query(q)": f"embed({query})"},
            )
            assert response.is_successful()

        if return_df:
            return self.hits_as_df(response, ['id', 'title'])
        else:
            return response

    def query_MV_hybrid(self, input_query, return_df = True):
        with self.app.syncio(connections=1) as session:
            query = input_query
            response: VespaQueryResponse = session.query(
                yql="select * from sources * where userQuery() or ({targetHits:1000}nearestNeighbor(line_embeddings,q))",
                query=query,
                ranking="hybrid",
                body={"input.query(q)": f"embed({query})"},
            )
            assert response.is_successful()

        if return_df:
            return self.hits_as_df(response, ['id', 'title'])
        else:
            return response
            
