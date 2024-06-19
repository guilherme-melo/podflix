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
from vespa.deployment import VespaCloud
from vespa.application import Vespa
import pandas as pd
import os

class VespaApp:
    def __init__(self, deploy = False, key = None, key_location = None, token_name = None, token = None):
        self.key = key
        self.key_location = key_location
        self.token_name = token_name
        self.token = token
        self.app = self.start_vespa() if deploy else self.connect_vespa()

    def connect_vespa(self):
        if self.token is None:
            with open('token.txt', 'r') as f:
                self.token = f.read()
        
        os.environ['VESPA_CLOUD_SECRET_TOKEN'] = self.token
        url = "https://bad202d2.b20230ac.z.vespa-app.cloud/"
        app = Vespa(url=url)
        return app

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
                                name="transcript",
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
                                name="embedding_MV",
                                type="tensor<float>(p{},x[384])",
                                indexing=[
                                    "input lines",
                                    "embed",
                                    "index",
                                    "attribute",
                                ],
                                ann=HNSW(distance_metric="angular"),
                                is_document_field=False,
                            ),
                            Field(
                                name="embedding_title",
                                type="tensor<float>( x[384])",
                                indexing=[
                                    'input title',
                                    "embed",
                                    "index",
                                    "attribute",
                                ],
                                ann=HNSW(distance_metric="angular"),
                                is_document_field=False,
                            ),
                            Field(
                                name="embedding_title_description",
                                type="tensor<float>( x[384])",
                                indexing=[
                                    'input title . " " . input description',
                                    "embed",
                                    "index",
                                    "attribute",
                                ],
                                ann=HNSW(distance_metric="angular"),
                                is_document_field=False,
                            ),
                            Field(
                                name="embedding_full",
                                type="tensor<float>( x[384])",
                                indexing=[
                                    'input title . " " . input description . " " . input transcript',
                                    "embed",
                                    "index",
                                    "attribute",
                                ],
                                ann=HNSW(distance_metric="angular"),
                                is_document_field=False,
                            ),
                        ]
                    ),
                    fieldsets=[
                        FieldSet(name="default", fields=["title", "description","transcript","lines"])
                    ],
                    rank_profiles=[
                        #########################################################
                        RankProfile(
                            name="bm25_title",
                            inputs=[("query(q)", "tensor<float>(x[384])")],
                            functions=[
                                Function(name="bm25sum_title", expression="bm25(title)")
                            ],
                            first_phase="bm25sum_title",
                        ),
                        RankProfile(
                            name="bm25_title_description",
                            inputs=[("query(q)", "tensor<float>(x[384])")],
                            functions=[
                                Function(name="bm25sum_title_description", expression="bm25(title) + bm25(description)")
                            ],
                            first_phase="bm25sum_title_description",
                        ),
                        RankProfile(
                            name="bm25_full",
                            inputs=[("query(q)", "tensor<float>(x[384])")],
                            functions=[
                                Function(name="bm25sum", expression="bm25(title) + bm25(description) + bm25(transcript)")
                            ],
                            first_phase="bm25sum",
                        ),
                        RankProfile(
                            name="bm25_MV_full",
                            inputs=[("query(q)", "tensor<float>(x[384])")],
                            functions=[
                                Function(name="bm25sum_MV", expression="bm25(title) + bm25(description) + bm25(lines)")
                            ],
                            first_phase="bm25sum_MV",
                        ),
                        #########################################################
                        RankProfile(
                            name="semantic_title",
                            inputs=[("query(q)", "tensor<float>(x[384])")],
                            inherits="default",
                            first_phase="cos(distance(field,embedding_title))",
                            match_features=["closest(embedding_MV)"],
                        ),
                        RankProfile(
                            name="semantic_title_description",
                            inputs=[("query(q)", "tensor<float>(x[384])")],
                            inherits="default",
                            first_phase="cos(distance(field,embedding_title_description))",
                            match_features=["closest(embedding_MV)"],
                        ),
                        RankProfile(
                            name="semantic_full",
                            inputs=[("query(q)", "tensor<float>(x[384])")],
                            inherits="default",
                            first_phase="cos(distance(field,embedding_full))",
                            match_features=["closest(embedding_MV)"],
                        ),
                        RankProfile(
                            name="semantic_MV_full",
                            inputs=[("query(q)", "tensor<float>(x[384])")],
                            inherits="default",
                            first_phase="3*cos(distance(field,embedding_MV))+cos(distance(field,embedding_title_description))",
                            match_features=["closest(embedding_MV)"],
                        ),
                        #########################################################
                        RankProfile(
                            name="fusion_title",
                            inherits="bm25_title",
                            inputs=[("query(q)", "tensor<float>(x[384])")],
                            functions=[
                                 Function(name="cosine_title", expression="cos(distance(field,embedding_title))")
                                 ],
                            first_phase="cosine_title",
                            global_phase=GlobalPhaseRanking(
                                expression="reciprocal_rank_fusion(bm25sum_title, cosine_title)",
                                rerank_count=1000,
                            ),
                        ),

                        RankProfile(
                            name="fusion_title_description",
                            inherits="bm25_title_description",
                            inputs=[("query(q)", "tensor<float>(x[384])")],
                            functions=[
                                 Function(name="cosine_title_description", expression="cos(distance(field,embedding_title_description))")
                                 ],
                            first_phase="cosine_title_description",
                            global_phase=GlobalPhaseRanking(
                                expression="reciprocal_rank_fusion(bm25sum_title_description, cosine_title_description )",
                                rerank_count=1000,
                            ),
                        ),

                        RankProfile(
                            name="fusion_full",
                            inherits="bm25_full",
                            inputs=[("query(q)", "tensor<float>(x[384])")],
                            functions=[
                                 Function(name="cosine_distance_full", expression="cos(distance(field,embedding_full))")
                                 ],
                            first_phase="cosine_distance_full",
                            global_phase=GlobalPhaseRanking(
                                expression="reciprocal_rank_fusion(bm25sum, cosine_distance_full)",
                                rerank_count=1000,
                            ),
                        ),


                        RankProfile(
                            name="fusion_MV_full",
                            inherits="bm25_MV_full",
                            inputs=[("query(q)", "tensor<float>(x[384])")],
                            functions=[
                                 Function(name="cosine_distance_MV_full", expression="3*cos(distance(field,embedding_MV))+cos(distance(field,embedding_title_description))")
                                 ],
                            first_phase="cosine_distance_MV_full",
                            global_phase=GlobalPhaseRanking(
                                expression="reciprocal_rank_fusion(bm25sum_MV, cosine_distance_MV_full)",
                                rerank_count=1000,
                            ),
                        ),

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
        vespa_cloud = VespaCloud(
            tenant="grupo5",
            application="podflix",
            key_location=self.key_location,
            key_content=self.key,
            application_package=package,
            auth_client_token_id=self.token_name
        )
        app = vespa_cloud.deploy()
        return app




    def transform_row(self, row):
        return {
            "id": row['episode'],
            "fields": {
                "title": row['title'],
                "description": row['description'],
                "transcript": row['transcript'],
                "lines": row['transcript'].split('\n'),
                "id": row['episode']
            }
        }


    def callback(self, response:VespaResponse, id:str):
        if not response.is_successful():
            print(f"Error when feeding document {id}: {response.get_json()}")

    def start_vespa(self):
        data = pd.read_csv('app/podcasts/data/transcribed_podcasts.csv') # TODO: change to read from sqlite3
        vespa_feed = data.apply(self.transform_row, axis=1).tolist()

        app = self.deploy_vespa()
        app.feed_iterable(vespa_feed, schema="doc", namespace="podflix", callback=self.callback)

        return app



            
    def hits_as_df(self, response:VespaQueryResponse, fields) -> pd.DataFrame:
        records = []
        for hit in response.hits:
            record = {}
            for field in fields:
                record[field] = hit['fields'][field]
            records.append(record)
        return pd.DataFrame(records)

    def query_bm25_MV_full(self, input_query, return_df = True):
        with self.app.syncio(connections=1) as session:
            query = input_query
            response: VespaQueryResponse = session.query(
                yql="select * from sources * where userQuery() ",
                query=query,
                ranking="bm25_MV_full",
            )
            assert response.is_successful()
        
        if return_df:
            return self.hits_as_df(response, ['id', 'title'])
        else:
            return response

    def query_bm25_full(self, input_query, return_df = True):
        with self.app.syncio(connections=1) as session:
            query = input_query
            response: VespaQueryResponse = session.query(
                yql="select * from sources * where userQuery() ",
                query=query,
                ranking="bm25_full",
            )
            assert response.is_successful()
        
        if return_df:
            return self.hits_as_df(response, ['id', 'title'])
        else:
            return response

    def query_bm25_title_description(self, input_query, return_df = True):
        with self.app.syncio(connections=1) as session:
            query = input_query
            response: VespaQueryResponse = session.query(
                yql="select * from sources * where userQuery() ",
                query=query,
                ranking="bm25_title_description",
            )
            assert response.is_successful()
        
        if return_df:
            return self.hits_as_df(response, ['id', 'title'])
        else:
            return response

    def query_bm25_title(self, input_query, return_df = True):
        with self.app.syncio(connections=1) as session:
            query = input_query
            response: VespaQueryResponse = session.query(
                yql="select * from sources * where userQuery() ",
                query=query,
                ranking="bm25_title",
            )
            assert response.is_successful()
        
        if return_df:
            return self.hits_as_df(response, ['id', 'title'])
        else:
            return response


    def query_semantic_MV_full(self, input_query, return_df = True):
        with self.app.syncio(connections=1) as session:
            query = input_query
            response: VespaQueryResponse = session.query(
                yql="select * from sources * where ({targetHits:1000}nearestNeighbor(embedding_MV,q)) ",
                query=query,
                ranking="semantic_MV_full",
                body={"input.query(q)": f"embed({query})"},
            )
            assert response.is_successful()

        if return_df:
            return self.hits_as_df(response, ['id', 'title'])
        else:
            return response
        
    def query_semantic_full(self, input_query, return_df = True):
        with self.app.syncio(connections=1) as session:
            query = input_query
            response: VespaQueryResponse = session.query(
                yql="select * from sources * where ({targetHits:1000}nearestNeighbor(embedding_full,q)) ",
                query=query,
                ranking="semantic_full",
                body={"input.query(q)": f"embed({query})"},
            )
            assert response.is_successful()

        if return_df:
            return self.hits_as_df(response, ['id', 'title'])
        else:
            return response
        
    def query_semantic_title_description(self, input_query, return_df = True):
        with self.app.syncio(connections=1) as session:
            query = input_query
            response: VespaQueryResponse = session.query(
                yql="select * from sources * where ({targetHits:1000}nearestNeighbor(embedding_MV,q)) ",
                query=query,
                ranking="semantic_title_description",
                body={"input.query(q)": f"embed({query})"},
            )
            assert response.is_successful()

        if return_df:
            return self.hits_as_df(response, ['id', 'title'])
        else:
            return response
        
    def query_semantic_title(self, input_query, return_df = True):
        with self.app.syncio(connections=1) as session:
            query = input_query
            response: VespaQueryResponse = session.query(
                yql="select * from sources * where ({targetHits:1000}nearestNeighbor(embedding_MV,q)) ",
                query=query,
                ranking="semantic_title",
                body={"input.query(q)": f"embed({query})"},
            )
            assert response.is_successful()

        if return_df:
            return self.hits_as_df(response, ['id', 'title'])
        else:
            return response

    def query_fusion_MV_full(self, input_query, return_df = True):
        with self.app.syncio(connections=1) as session:
            query = input_query
            response: VespaQueryResponse = session.query(
                yql="select * from sources * where userQuery() or ({targetHits:1000}nearestNeighbor(embedding_MV,q)) limit 10",
                query=query,
                ranking="fusion_MV_full",
                body={"input.query(q)": f"embed({query})"},
            )
            assert response.is_successful()

        if return_df:
            return self.hits_as_df(response, ['id', 'title'])
        else:
            return response

    def query_fusion_full(self, input_query, return_df = True):
        with self.app.syncio(connections=1) as session:
            query = input_query
            response: VespaQueryResponse = session.query(
                yql="select * from sources * where userQuery() or ({targetHits:1000}nearestNeighbor(embedding_full,q)) limit 10",
                query=query,
                ranking="fusion_full",
                body={"input.query(q)": f"embed({query})"},
            )
            assert response.is_successful()

        if return_df:
            return self.hits_as_df(response, ['id', 'title'])
        else:
            return response

    def query_fusion_title_description(self, input_query, return_df = True):
        with self.app.syncio(connections=1) as session:
            query = input_query
            response: VespaQueryResponse = session.query(
                yql="select * from sources * where userQuery() or ({targetHits:1000}nearestNeighbor(embedding_title_description,q)) limit 10",
                query=query,
                ranking="fusion_title_description",
                body={"input.query(q)": f"embed({query})"},
            )
            assert response.is_successful()

        if return_df:
            return self.hits_as_df(response, ['id', 'title'])
        else:
            return response

    def query_fusion_title(self, input_query, return_df = True):
        with self.app.syncio(connections=1) as session:
            query = input_query
            response: VespaQueryResponse = session.query(
                yql="select * from sources * where userQuery() or ({targetHits:1000}nearestNeighbor(embedding_title,q)) limit 10",
                query=query,
                ranking="fusion_title",
                body={"input.query(q)": f"embed({query})"},
            )
            assert response.is_successful()

        if return_df:
            return self.hits_as_df(response, ['id', 'title'])
        else:
            return response
        

    def query(self, input_query, type_query = "bm25", fields = "full" , MV = True ,  return_df = True):
        # fields in ['title', 'title+drescription', 'full']
        # MV in [True, False]
        if MV == "on":
            MV = True
        else:
            MV = False

        if MV:
            if type_query == 'bm25':

                if fields == 'title':
                    return self.query_bm25_title(input_query, return_df)
                
                elif fields == 'title+description':
                    return self.query_bm25_title_description(input_query, return_df)
                
                elif fields == 'full':
                    return self.query_bm25_MV_full(input_query, return_df)
                
            elif type_query == 'semantic':
                
                if fields == 'title':
                    return self.query_semantic_title(input_query, return_df)
                
                elif fields == 'title+description':
                    return self.query_semantic_title_description(input_query, return_df)
                
                elif fields == 'full':
                    return self.query_semantic_MV_full(input_query, return_df)

            elif type_query == 'fusion':
                
                if fields == 'title':
                    return self.query_fusion_title(input_query, return_df)
                
                elif fields == 'title+description':
                    return self.query_fusion_title_description(input_query, return_df)
                
                elif fields == 'full':
                    return self.query_fusion_MV_full(input_query, return_df)

                
        else:
            if type_query == 'bm25':

                if fields == 'title':
                    return self.query_bm25_title(input_query, return_df)
                
                elif fields == 'title+description':
                    return self.query_bm25_title_description(input_query, return_df)
                
                elif fields == 'full':
                    return self.query_bm25_full(input_query, return_df)
                
            elif type_query == 'semantic':
                    
                if fields == 'title':
                    return self.query_semantic_title(input_query, return_df)
                
                elif fields == 'title+description':
                    return self.query_semantic_title_description(input_query, return_df)
                
                elif fields == 'full':
                    return self.query_semantic_full(input_query, return_df)
    
            elif type_query == 'fusion':
                    
                if fields == 'title':
                    return self.query_fusion_title(input_query, return_df)
                
                elif fields == 'title+description':
                    return self.query_fusion_title_description(input_query, return_df)
                
                elif fields == 'full':
                    return self.query_fusion_full(input_query, return_df)


