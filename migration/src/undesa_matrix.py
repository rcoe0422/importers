import pandas as pd
import os.path

from migration.src.utils import standardise_countries
from migration.src.un_desa import (
    international_migrants_by_destination,
    international_migrants_by_origin,
)


def add_selected_country_value(df: pd.DataFrame) -> pd.DataFrame:

    orig = international_migrants_by_origin()
    dest = international_migrants_by_destination()

    countries = df["Entity"].drop_duplicates()

    for country in countries:
        df_sub = df.loc[
            df["Entity"] == country, ["Entity", "Year", country + "_origin"]
        ]
        orig_sub = orig.loc[
            orig["Country"] == country,
            ["Country", "Year", "undesa_international_migrants_by_origin"],
        ]
        orig_comb = pd.merge(
            df_sub.assign(Year=df_sub.Year.astype(str)),
            orig_sub.assign(Year=orig_sub.Year.astype(str)),
            left_on=["Entity", "Year"],
            right_on=["Country", "Year"],
            how="left",
        )
        orig_comb = orig_comb[
            ["Entity", "Year", "undesa_international_migrants_by_origin"]
        ]
        orig_comb.rename(
            columns={"undesa_international_migrants_by_origin": country + "_origin"},
            inplace=True,
        )
        orig_comb[country + "_origin"] * -1
        df.loc[
            df["Entity"] == country, ["Entity", "Year", country + "_origin"]
        ] = orig_comb

        # destination
        df_sub = df.loc[
            df["Entity"] == country, ["Entity", "Year", country + "_destination"]
        ]
        dest_sub = dest.loc[
            dest["Country"] == country,
            ["Country", "Year", "undesa_international_migrants_by_destination"],
        ]
        dest_comb = pd.merge(
            df_sub.assign(Year=df_sub.Year.astype(str)),
            dest_sub.assign(Year=orig_sub.Year.astype(str)),
            left_on=["Entity", "Year"],
            right_on=["Country", "Year"],
            how="left",
        )
        dest_comb = dest_comb[
            ["Entity", "Year", "undesa_international_migrants_by_destination"]
        ]
        dest_comb.rename(
            columns={
                "undesa_international_migrants_by_destination": country + "_destination"
            },
            inplace=True,
        )
        dest_comb[country + "_destination"] * -1
        df.loc[
            df["Entity"] == country, ["Entity", "Year", country + "_destination"]
        ] = dest_comb

    return df


def migration_matrix():
    if os.path.exists(
        "migration/input/undesa_pd_2020_ims_stock_by_sex_destination_and_origin.csv"
    ):
        df = pd.read_csv(
            "migration/input/undesa_pd_2020_ims_stock_by_sex_destination_and_origin.csv"
        )
    else:
        df = pd.read_excel(
            "https://www.un.org/development/desa/pd/sites/www.un.org.development.desa.pd/files/undesa_pd_2020_ims_stock_by_sex_destination_and_origin.xlsx",
            sheet_name="Table 1",
            skiprows=10,
            usecols="B:N",
        )
        df.to_csv(
            "migration/input/undesa_pd_2020_ims_stock_by_sex_destination_and_origin.csv"
        )
    df[
        "Region, development group, country or area of destination"
    ] = standardise_countries(
        df["Region, development group, country or area of destination"]
    )

    df["Region, development group, country or area of origin"] = standardise_countries(
        df["Region, development group, country or area of origin"]
    )

    df = remove_regions(df)

    df["destination_origin"] = (
        df["Region, development group, country or area of destination"]
        + " _ "
        + df["Region, development group, country or area of origin"]
    )

    df.drop(
        [
            "Notes of destination",
            "Location code of destination",
            "Type of data of destination",
            "Location code of origin",
            "Region, development group, country or area of destination",
            "Region, development group, country or area of origin",
        ],
        axis=1,
        inplace=True,
    )

    df_melt = pd.melt(
        df,
        id_vars=["destination_origin"],
        value_vars=["1990", "1995", "2000", "2005", "2010", "2015", "2020"],
    )

    split = df_melt["destination_origin"].str.split(" _ ", n=1, expand=True)
    df_melt["destination"] = split[0]
    df_melt["origin"] = split[1]
    df_melt = df_melt.drop("destination_origin", axis=1)

    # add _destination to column names in df_wide_origin
    df_wide_origin = df_melt.pivot_table(
        index=["origin", "variable"], columns="destination", values="value"
    ).reset_index()
    cols = df_wide_origin.columns.drop(["origin", "variable"])
    new_cols = cols + "_destination"
    df_wide_origin.rename(columns=dict(zip(cols, new_cols)), inplace=True)
    df_wide_origin = df_wide_origin.rename(
        columns={"origin": "Entity", "variable": "Year"}
    )

    # add _origin to column names in df_wide_destination
    df_wide_destination = df_melt.pivot_table(
        index=["destination", "variable"], columns="origin", values="value"
    ).reset_index()
    cols = df_wide_destination.columns.drop(["destination", "variable"])
    new_cols = cols + "_origin"
    df_wide_destination.rename(columns=dict(zip(cols, new_cols)), inplace=True)
    df_wide_destination = df_wide_destination.rename(
        columns={"destination": "Entity", "variable": "Year"}
    )

    df_both = pd.merge(
        df_wide_origin, df_wide_destination, on=["Entity", "Year"], how="outer"
    )

    df_both = add_selected_country_value(df=df_both)

    res = df_both.apply(lambda x: x.fillna(""))
    res.columns = res.columns.str.replace(" ", "").str.lower()

    res.to_csv("migration/output/Migration_matrix.csv", index=False)


def remove_regions(df: pd.DataFrame) -> pd.DataFrame:

    regions = [
        "World",
        "Africa",
        "Asia",
        "Australia and New Zealand",
        "Central America",
        "Central Asia",
        "Central and Southern Asia",
        "Developed regions",
        "Eastern Africa",
        "Eastern Asia",
        "Eastern Europe",
        "Eastern and South-Eastern Asia",
        "Europe",
        "Europe and Northern America",
        "High-income countries",
        "Land-locked Developing Countries (LLDC)",
        "Latin America and the Caribbean",
        "Least developed countries",
        "Less developed regions",
        "Less developed regions, excluding China",
        "Less developed regions, excluding least developed countries",
        "Low-income countries",
        "Lower-middle-income countries",
        "Melanesia",
        "Micronesia (region)",
        "Middle Africa",
        "Middle-income countries",
        "Northern Africa",
        "Northern Africa and Western Asia",
        "Northern America",
        "Northern Europe",
        "Oceania",
        "Oceania (excluding Australia and New Zealand)",
        "Other",
        "Small island developing States (SIDS)",
        "South America",
        "South-Eastern Asia",
        "Southern Africa",
        "Southern Asia",
        "Southern Europe",
        "Sub-Saharan Africa",
        "Upper-middle-income countries",
        "Western Africa",
        "Western Asia",
        "Western Europe",
    ]
    df = df[
        ~df["Region, development group, country or area of destination"].isin(regions)
    ]
    df = df[~df["Region, development group, country or area of origin"].isin(regions)]
    return df
