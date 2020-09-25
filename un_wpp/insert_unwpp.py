import datetime
import os
from glob import glob
import sys
sys.path.append("/home/owid/importers/importers")

import pandas as pd
from db import connection
from db_utils import DBUtils

with connection.cursor() as cursor:
    db = DBUtils(cursor)

    # Upsert entities
    entities = pd.read_csv("output/distinct_countries_standardized.csv")
    for entity_name in entities.name:
        db_entity_id = db.get_or_create_entity(entity_name)
        entities.loc[entities.name == entity_name, "db_entity_id"] = db_entity_id
    print(entities)

    # Upsert datasets
    datasets = pd.read_csv("output/datasets.csv")
    for dataset_name in datasets.name:
        db_dataset_id = db.upsert_dataset(name=dataset_name, namespace="unwpp", user_id=46)
        datasets.loc[datasets.name == dataset_name, "db_dataset_id"] = db_dataset_id
    print(datasets)

    # Upsert sources
    sources = pd.read_csv("output/sources.csv")
    sources = pd.merge(sources, datasets, left_on="dataset_id", right_on="id")
    for i, source_row in sources.iterrows():
        db_source_id = db.upsert_source(
            name=source_row.name,
            description=source_row.description,
            dataset_id=source_row.db_dataset_id
        )
        sources.iloc[i, "db_source_id"] = db_source_id
    print(sources)

    # # upsert variables
    # names_to_ids = {}
    # for i, row in variables.iterrows():

    #     dataset_name = datasets[datasets["id"] == row["dataset_id"]]["name"].values[0]
    #     dataset_id = dataset_name_ids[dataset_name]
    #     source_id = dataset_to_source_ids[dataset_name]<‡

    #     variable_id = db.upsert_variable(
    #                                     name=row["name"], 
    #                                     code=None, 
    #                                     unit=row["unit"], 
    #                                     short_unit=None, 
    #                                     source_id=source_id, 
    #                                     dataset_id=dataset_id, 
    #                                     description=None, 
    #                                     timespan=", 
    #                                     coverage=", 
    #                                     display={}
    #                                     )
    #     names_to_ids[row["name"]] = variable_id

    # # Inserting datapoints
    # datapoints_files = glob("datapoints/*.csv")
    # for x in datapoints_files: 
    #     # to get variable is
    #     v_id = int(x.split("_")[1].split(".")[0])

    #     # to get variable name
    #     variable_name = variables[variables["id"]==v_id]["name"].values[0]

    #     # to get variable id from db
    #     variable_id = names_to_ids[variable_name]
    #     data = pd.read_csv(x)

    #     for i, row in data.iterrows():
    #         entity_id = entities[entities["name"] == row["country"]]["db_entity_id"].values[0]

    #         year = row["year"]
    #         val = row["value"]

    #         db.upsert_one("""
    #             INSERT INTO data_values
    #                 (value, year, entityId, variableId)
    #             VALUES
    #                 (%s, %s, %s, %s)
    #             ON DUPLICATE KEY UPDATE
    #                 value = VALUES(value),
    #                 year = VALUES(year),
    #                 entityId = VALUES(entityId),
    #                 variableId = VALUES(variableId)
    #         """, [val, int(year), str(int(entity_id)), str(variable_id)])
    # 
