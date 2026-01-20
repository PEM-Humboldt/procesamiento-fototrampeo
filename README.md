> Este repositorio se ha modificado a nuevos estándares, consulte [cam-trap-flow](https://github.com/PEM-Humboldt/cam-trap-flow) y [dashboard-red-otus](https://github.com/PEM-Humboldt/dashboard-red-otus) para funcionalidades similares

---

# procesamiento-fototrampeo
Este repositorio contiene una serie de scripts para el procesamiento de información de proyectos de Wildlife Insights (WI). El procesamiento consiste principalmente en la creación de nuevas tablas que sirven como insumo para futuros análisis y en la conversión del formato utilizado por WI al estándar Darwin Core (necesario para la publicación de datos a través del SiB Colombia y GBIF).

Estos scripts utilizan las funciones del paquete [`wiutils`](https://github.com/PEM-Humboldt/wiutils) y están pensados para procesar diferentes proyectos de fototrampeo del Instituto Humboldt como por ejemplo Fibras, ANH y Días de Cámaras Trampa.

## Instalación
Para ejecutar los scripts de procesamiento es necesario instalar `wiutils` y otras dependencias. Para esto se utiliza [`conda`](https://docs.conda.io/en/latest/), un gestor de paquetes y entornos virtuales. `conda` está disponible en la instalación de [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (recomendado) o [Anaconda](https://www.anaconda.com/).

Antes de instalar las liberías, es necesario clonar este repositorio en su máquina. Para eso, ejecute el siguiente comando dentro de la carpeta donde quiera clonarlo:
```shell
git clone https://github.com/PEM-Humboldt/procesamiento-fototrampeo
```

Una vez clonado el repositorio, navegue a la raíz de este con el siguiente comando:
```shell
cd procesamiento-fototrampeo
```

Para evitar conflictos con la instalación base de Anaconda o Miniconda, todas las dependencias serán instaladas en un entorno virtual. Para crear este entorno e instalar las depencencias necesarias, ejecute el siguiente comando:
```shell
conda env create -f environment.yml
```

## Ejecución

1. Revisión e inconsistencias

2. Análisis
- Conteo detallado
- Conteo general
- Datos generales
- Historias de detección
- Números de Hill

3. Darwin Core


## Autores y contribuidores
* Adriana Restrepo-Isaza
* Angélica Diaz-Pulido
* Marcelo Villa-Piñeros - [marcelovilla](https://github.com/marcelovilla)

## Licencia
Este proyecto está licenciado bajo MIT License - ver [LICENSE.txt](LICENSE.txt) para más información.
