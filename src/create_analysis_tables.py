"""
Genera las siguientes tablas para posteriores análisis:

- Conteo detallado
- Conteo general
- Datos generales
- Historias de detección
- Números de Hill
"""
import pathlib
import warnings

import click
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterstats
import regi0
import wiutils


def process_general_count(images, deployments, season_list, output_path, data_folder):
    if data_folder:
        checklist = pd.read_csv(
            data_folder.joinpath("taxonomic/Cifras_resolucion_2019_CC.csv"),
            encoding="latin-1",
        )
    with pd.ExcelWriter(output_path.joinpath(f"ConteoDetalladoEspecie.xlsx")) as writer:
        for season in season_list:
            if season == "Consolidado":
                result = wiutils.compute_general_count(
                    images,
                    deployments,
                    groupby="location",
                    add_taxonomy=True,
                    rank="class",
                )
            else:
                result = wiutils.compute_general_count(
                    images.loc[images["season"] == season, :],
                    groupby="deployment",
                    add_taxonomy=True,
                    rank="class",
                )

            if data_folder:
                result[
                    ["categoria_mads", "endemismo", "cites", "categoria_iucn"]
                ] = regi0.taxonomic.get_checklist_fields(
                    result["taxon"],
                    checklist,
                    name_field="scientificName",
                    fields=[
                        "measurementValue (Categoria de amenaza MADS)",
                        "measurementValue (ENDEMISMO)",
                        "appendixCITES",
                        "threatStatus",
                    ],
                )

            result.to_excel(
                writer,
                sheet_name=season,
                index=False,
            )


def process_general_data(images, deployments, season_list, output_path, data_folder):
    with pd.ExcelWriter(
        output_path.joinpath(f"DatosGenerales.xlsx"),
    ) as writer:
        for season in season_list:
            if season == "Consolidado":
                result = wiutils.compute_count_summary(
                    images,
                    deployments,
                    groupby="location",
                    add_records_by_class=True,
                    add_taxa_by_class=True,
                    remove_unidentified_kws={"rank": "genus"},
                )
            else:
                result = wiutils.compute_count_summary(
                    images.loc[images["season"] == season, :],
                    groupby="deployment",
                    add_records_by_class=True,
                    add_taxa_by_class=True,
                    remove_unidentified_kws={"rank": "genus"},
                )

            if data_folder:
                if season == "Consolidado":
                    col = "placename"
                else:
                    col = "deployment_id"
                result = pd.merge(
                    result,
                    deployments[[col, "longitude", "latitude"]],
                    on=col,
                    how="left",
                )
                result = gpd.GeoDataFrame(
                    result,
                    geometry=gpd.points_from_xy(result["longitude"], result["latitude"]),
                    crs="EPSG:4326",
                )
                ecosystems = gpd.read_file(
                    data_folder.joinpath("geographic/E_ECCMC_Ver21_100K.shp"),
                    mask=result.to_crs("epsg:3116").geometry
                )
                result["bioma"] = regi0.geographic.get_layer_field(
                    result, ecosystems, "BIOMA_IAvH"
                )
                result["ecosistema"] = regi0.geographic.get_layer_field(
                    result, ecosystems, "ECOS_SINTE"
                )
                result["porcentaje_bosque"] = rasterstats.point_query(
                    result.geometry,
                    data_folder.joinpath("geographic/porcentaje_bosque.tif"),
                    interpolate="nearest",
                )

                result["IHEH"] = rasterstats.point_query(
                    result.geometry,
                    data_folder.joinpath("geographic/IHEH_2018.tif"),
                    interpolate="nearest",
                )
                criteria = [
                    result["IHEH"].between(0, 15),
                    result["IHEH"].between(16, 40),
                    result["IHEH"].between(41, 60),
                    result["IHEH"].between(61, 100),
                ]
                values = ["Natural", "Bajo", "Medio", "Alto"]
                result["IHEH_cat"] = np.select(criteria, values)
                result = result.drop(columns=["longitude", "latitude", "geometry"])

            result.to_excel(
                writer,
                sheet_name=season,
                index=False,
            )


def process_detection(images, deployments, season_list, output_path):
    with pd.ExcelWriter(output_path.joinpath(f"ConteoDetallado.xlsx")) as writer:
        for season in season_list:
            if season == "Consolidado":
                result = wiutils.compute_detection(
                    images,
                    deployments,
                    groupby="location",
                    compute_abundance=True,
                    pivot=True,
                )
            else:
                result = wiutils.compute_detection(
                    images.loc[images["season"] == season, :],
                    groupby="deployment",
                    compute_abundance=True,
                    pivot=True,
                )

            result.to_excel(
                writer,
                sheet_name=season,
                index=False,
            )


def process_detection_history(images, deployments, season_list, output_path):
    for days in [5, 8, 10]:
        with pd.ExcelWriter(output_path.joinpath(
                f"HistoriasDeteccion{days}dias.xlsx"
            ),
        ) as writer:
            for season in season_list:
                if season != "Consolidado":
                    result = wiutils.compute_detection_history(
                        images.loc[images["season"] == season],
                        deployments,
                        date_range="deployments",
                        days=days,
                        compute_abundance=False,
                        pivot=True,
                    )
                    result = result.fillna("NA")
                    result.to_excel(
                        writer,
                        sheet_name=season,
                        index=False,
                    )


def process_hill_numbers(images, deployments, season_list, output_path):
    for group in ["Aves", "Mammalia", ""]:
        if group:
            group_images = images.loc[images["class"] == group, :]
        else:
            group_images = images.copy()

        with pd.ExcelWriter(output_path.joinpath(f"NumerosHill{group}.xlsx")) as writer:
            for season in season_list:
                if season == "Consolidado":
                    result = wiutils.compute_hill_numbers(
                        group_images,
                        deployments,
                        groupby="location",
                        q_values=(0, 1, 2),
                        pivot=True
                    )
                else:
                    result = wiutils.compute_hill_numbers(
                        group_images.loc[group_images["season"] == season, :],
                        groupby="deployment",
                        q_values=(0, 1, 2),
                        pivot=True
                    )

                result.to_excel(
                    writer,
                    sheet_name=season,
                    index=False,
                )


@click.command()
@click.argument("bundle_path", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path(exists=False, path_type=pathlib.Path))
@click.option("--seasons", "-s", is_flag=True, default=False)
@click.option("--data-folder", "-df", type=click.Path(exists=True, path_type=pathlib.Path))
@click.option("--quiet", "-q", type=click.STRING)
def main(bundle_path, output_path, seasons, data_folder, quiet):
    if not quiet:
        if not data_folder:
            print("La ruta de la carpeta de datos auxiliares no fue especificada."
                  " Algunos resultados no tendran información adicional.")

    if not quiet:
        print(f"Leyendo bundle en {bundle_path}")
    cameras, deployments, images, projects = wiutils.read_bundle(bundle_path)
    output_path.mkdir(parents=True, exist_ok=True)

    if not quiet:
        print(f"Eventos: {len(deployments)}")
        print(f"Imágenes: {len(images)}")

    season_list = ["Consolidado"]
    if seasons:
        images["season"] = images["deployment_id"].str.extract(r"(T\d)")
        season_list += images["season"].unique().tolist()

    if not quiet:
        print(f"Filtrando imágenes")
    filtered_images = wiutils.remove_domestic(images, reset_index=True)
    filtered_images = wiutils.remove_unidentified(
        filtered_images, rank="genus", reset_index=True
    )
    filtered_images = wiutils.remove_duplicates(
        filtered_images, interval=30, unit="minutes", reset_index=True
    )

    if not quiet:
        print("Creando tabla de datos generales")
    process_general_data(images, deployments, season_list, output_path, data_folder)

    if not quiet:
        print("Creando tabla de conteo general")
    process_general_count(filtered_images, deployments, season_list, output_path, data_folder)

    if not quiet:
        print("Creando tabla de conteo detallado")
    process_detection(filtered_images, deployments, season_list, output_path)

    if not quiet:
        print("Creando tablas de historias de detección")
    process_detection_history(filtered_images, deployments, season_list, output_path)

    if not quiet:
        print("Creando tablas de números de Hill")
    process_hill_numbers(filtered_images, deployments, season_list, output_path)


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    main()
